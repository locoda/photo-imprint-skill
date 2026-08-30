#!/usr/bin/env python3
"""photo_imprint update checker — 24h throttled, non-blocking, provenance-aware.

Patterns from:
- vercel-labs/skills (skill-lock.json + tree SHA)
- gh skill (provenance in SKILL.md frontmatter)
- majiayu000/version-checker (1h cache, 10s timeout, rollback, non-blocking)

This checker:
- reads local version from SKILL.md frontmatter
- reads local install SHA from git HEAD or .skill-lock.json
- fetches remote main HEAD SHA via `gh api` or GitHub Trees API
- compares; mismatch = update available
- throttles to 24h via cache file (XDG cache or skill-root/.cache)
- never blocks workflow; errors → "no update" with warning
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

SKILL_NAME = "photo_imprint"
DEFAULT_REPO = "locoda/photo-imprint-skill"
DEFAULT_BRANCH = "main"
CACHE_TTL_SECONDS = 24 * 3600  # 24h throttle as you requested
GITHUB_API_TIMEOUT = 10
GIT_TIMEOUT = 30

def skill_root() -> Path:
    return Path(__file__).resolve().parents[1]

def frontmatter_version(root: Path) -> str | None:
    text = (root / "SKILL.md").read_text(encoding="utf-8", errors="ignore")
    # simple yaml frontmatter parse
    m = re.search(r'^---\s*\n(.*?)\n---\s*\n', text, re.DOTALL | re.MULTILINE)
    if not m:
        return None
    fm = m.group(1)
    # version: "1.5.0" or version: 1.5.0
    vm = re.search(r'^\s*version\s*:\s*["\']?([0-9A-Za-z._-]+)["\']?\s*$', fm, re.MULTILINE)
    if vm:
        return vm.group(1).strip()
    return None

def frontmatter_source_repo(root: Path) -> str:
    text = (root / "SKILL.md").read_text(encoding="utf-8", errors="ignore")[:3000]
    # look for source.repository or repository field
    m = re.search(r'repository\s*:\s*["\']?([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)["\']?', text)
    if m:
        return m.group(1)
    # fallback
    return DEFAULT_REPO

def local_git_sha(root: Path) -> str | None:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if out.returncode == 0:
            sha = out.stdout.strip()
            if len(sha) >= 7:
                return sha
    except Exception:
        pass
    # fallback to .skill-lock.json
    lock = root / ".skill-lock.json"
    if lock.exists():
        try:
            data = json.loads(lock.read_text(encoding="utf-8"))
            # vercel format: skills[name].skillFolderHash or top-level sha
            if isinstance(data, dict):
                if "sha" in data:
                    return str(data["sha"])
                # look for our skill entry
                for v in data.values():
                    if isinstance(v, dict) and "skillFolderHash" in v:
                        return v["skillFolderHash"]
                    if isinstance(v, dict) and "sha" in v:
                        return v["sha"]
        except Exception:
            pass
    # fallback to ~/.agents/.skill-lock.json
    home_lock = Path.home() / ".agents" / ".skill-lock.json"
    if home_lock.exists():
        try:
            data = json.loads(home_lock.read_text(encoding="utf-8"))
            # v3 format: { "skills": { "photo_imprint": { ... } } } or flat
            candidates = []
            if "skills" in data and isinstance(data["skills"], dict):
                candidates = [data["skills"].get(SKILL_NAME), data["skills"].get(f"{DEFAULT_REPO}/{SKILL_NAME}")]
            else:
                candidates = [data.get(SKILL_NAME)]
            for c in candidates:
                if isinstance(c, dict):
                    if "skillFolderHash" in c:
                        return c["skillFolderHash"]
                    if "sha" in c:
                        return c["sha"]
        except Exception:
            pass
    return None

def cache_path(root: Path) -> Path:
    # XDG_CACHE_HOME or ~/.cache/photo-imprint-skill/update-check.json
    xdg = os.environ.get("XDG_CACHE_HOME")
    if xdg:
        p = Path(xdg) / "photo-imprint-skill"
    else:
        p = Path.home() / ".cache" / "photo-imprint-skill"
    # if not writable (e.g. sandbox), fallback to skill-root/.cache
    try:
        p.mkdir(parents=True, exist_ok=True)
        return p / "update-check.json"
    except Exception:
        fallback = root / ".cache"
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback / "update-check.json"

def read_cache(cache_file: Path) -> dict[str, Any] | None:
    if not cache_file.exists():
        return None
    try:
        data = json.loads(cache_file.read_text(encoding="utf-8"))
        return data
    except Exception:
        return None

def write_cache(cache_file: Path, data: dict[str, Any]) -> None:
    try:
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        tmp = cache_file.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(cache_file)
    except Exception:
        pass  # non-blocking

def gh_token() -> str | None:
    for env in ("GITHUB_TOKEN", "GH_TOKEN"):
        t = os.environ.get(env)
        if t:
            return t.strip()
    # try gh auth token
    try:
        out = subprocess.run(
            ["gh", "auth", "token"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip()
    except Exception:
        pass
    return None

def fetch_remote_sha(repo: str, branch: str = DEFAULT_BRANCH) -> tuple[str | None, str, float]:
    """Return (sha, source, elapsed_ms). source = 'gh-cli' | 'github-api' | 'git-ls-remote'"""
    start = time.time()
    token = gh_token()
    # 1. gh api (authenticated, respects rate limit)
    try:
        cmd = ["gh", "api", f"repos/{repo}/commits/{branch}", "--jq", ".sha"]
        if token:
            env = os.environ.copy()
            env["GH_TOKEN"] = token
        else:
            env = None
        out = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=GITHUB_API_TIMEOUT,
            env=env,
        )
        if out.returncode == 0 and out.stdout.strip():
            elapsed = (time.time() - start) * 1000
            return out.stdout.strip(), "gh-cli", elapsed
    except Exception:
        pass

    # 2. GitHub API direct (tree SHA comparison pattern from vercel-labs)
    try:
        url = f"https://api.github.com/repos/{repo}/commits/{branch}"
        req = Request(url, headers={"Accept": "application/vnd.github.v3+json", "User-Agent": f"{SKILL_NAME}-update-checker/1.5"})
        if token:
            req.add_header("Authorization", f"Bearer {token}")
        with urlopen(req, timeout=GITHUB_API_TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            sha = data.get("sha")
            if sha:
                elapsed = (time.time() - start) * 1000
                return sha, "github-api", elapsed
    except (URLError, HTTPError, Exception):
        pass

    # 3. git ls-remote fallback (no API rate limit)
    try:
        out = subprocess.run(
            ["git", "ls-remote", f"https://github.com/{repo}.git", f"refs/heads/{branch}"],
            capture_output=True,
            text=True,
            timeout=GIT_TIMEOUT,
        )
        if out.returncode == 0 and out.stdout.strip():
            sha = out.stdout.strip().split()[0]
            elapsed = (time.time() - start) * 1000
            return sha, "git-ls-remote", elapsed
    except Exception:
        pass

    elapsed = (time.time() - start) * 1000
    return None, "none", elapsed

def main() -> int:
    parser = argparse.ArgumentParser(description="photo_imprint 24h throttled update checker (non-blocking)")
    parser.add_argument("--repo", default=None, help=f"GitHub repo owner/name (default from SKILL.md or {DEFAULT_REPO})")
    parser.add_argument("--branch", default=DEFAULT_BRANCH, help="branch to check (default main)")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--force", action="store_true", help="ignore 24h cache")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    root = skill_root()
    repo = args.repo or frontmatter_source_repo(root)
    local_version = frontmatter_version(root)
    local_sha = local_git_sha(root)
    cache_file = cache_path(root)

    # 0. update_check_started
    now = datetime.now(timezone.utc)
    now_iso = now.isoformat()
    cache = read_cache(cache_file)

    # throttle
    if cache and not args.force:
        last = cache.get("last_check_iso")
        try:
            last_dt = datetime.fromisoformat(last) if last else None
            if last_dt:
                age = (now - last_dt).total_seconds()
                if age < CACHE_TTL_SECONDS:
                    # cached result <100ms path
                    cached_result = {
                        "ok": True,
                        "throttled": True,
                        "age_seconds": int(age),
                        "ttl_seconds": CACHE_TTL_SECONDS,
                        "local_version": local_version,
                        "local_sha": (local_sha[:7] if local_sha else None),
                        "remote_sha": (cache.get("remote_sha")[:7] if cache.get("remote_sha") else None),
                        "update_available": cache.get("update_available", False),
                        "source": cache.get("source", "cache"),
                        "cache_file": str(cache_file),
                    }
                    if args.json:
                        print(json.dumps(cached_result, indent=2, ensure_ascii=False))
                    else:
                        if cached_result["update_available"]:
                            print(f"Update available (cached, {int(age//3600)}h ago): {repo} — local {local_version or '?'} vs remote newer")
                        else:
                            print(f"Up to date (cached {int(age//3600)}h ago, TTL 24h)")
                        if args.verbose:
                            print(f"cache: {cache_file}")
                    return 0
        except Exception:
            pass

    remote_sha, source, elapsed_ms = fetch_remote_sha(repo, args.branch)

    update_available = False
    reason = ""
    if remote_sha is None:
        # GitHub unreachable → non-blocking, log warning, return "no update"
        reason = "github unreachable, treating as no update (non-blocking)"
        update_available = False
    else:
        if local_sha is None:
            # no local sha → compare version only? treat as unknown, suggest update check via version
            # if remote differs from local version? we don't have remote version without cloning
            # safest: if we have no local SHA, assume update check can't prove outdated, but report remote SHA
            update_available = False
            reason = "no local SHA, cannot compare"
        else:
            # short comparison (full SHA or 7-char)
            update_available = (remote_sha != local_sha) and (not local_sha.startswith(remote_sha)) and (not remote_sha.startswith(local_sha))
            reason = "SHA mismatch" if update_available else "SHA match"

    # version_comparison_completed
    result = {
        "ok": True,
        "throttled": False,
        "local_version": local_version,
        "local_sha": local_sha[:7] if local_sha else None,
        "local_sha_full": local_sha,
        "remote_sha": remote_sha[:7] if remote_sha else None,
        "remote_sha_full": remote_sha,
        "update_available": update_available,
        "reason": reason,
        "repo": repo,
        "branch": args.branch,
        "source": source,
        "elapsed_ms": int(elapsed_ms),
        "last_check_iso": now_iso,
        "cache_file": str(cache_file),
        "events": [
            {"event": "update_check_started", "at": now_iso, "repo": repo},
            {"event": "github_api_call", "source": source, "elapsed_ms": int(elapsed_ms)},
            {"event": "version_comparison_completed", "update_available": update_available, "reason": reason},
        ],
    }

    # write cache
    write_cache(cache_file, {
        "last_check_iso": now_iso,
        "local_version": local_version,
        "local_sha": local_sha,
        "remote_sha": remote_sha,
        "update_available": update_available,
        "source": source,
        "repo": repo,
        "branch": args.branch,
    })

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if remote_sha is None:
            print(f"Update check: no network ({source}) — {reason}. Skipping (non-blocking).")
            print(f"  local {local_version or '?'} ({local_sha[:7] if local_sha else 'no SHA'})")
            if args.verbose:
                print(f"  cache {cache_file} — TTL 24h, elapsed {int(elapsed_ms)}ms")
            return 0
        if update_available:
            print(f"Update available: {repo}@{args.branch} — local {local_version or '?'} ({local_sha[:7] if local_sha else '?'}) → remote {remote_sha[:7]}")
            print(f"  gh skill update photo_imprint  # or: git pull origin {args.branch}")
        else:
            print(f"Up to date: {repo} — {local_version or ''} ({local_sha[:7] if local_sha else 'no SHA'}) matches remote {remote_sha[:7] if remote_sha else '?'} [{source} {int(elapsed_ms)}ms]")
        if args.verbose:
            print(f"  cache {cache_file}, TTL 24h")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
