# Photo Imprint (印痕)

> Keep the photo, remember it in a different stroke.

[简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md)

You came back with a camera roll full of drinks, airplane trays, street corners in Roppongi. You want to turn them into a little journal carousel for Xiaohongshu or IG. If you just prompt a model, it looks pretty, but the cup gets bigger, the street gets fake, and your photo disappears.

Photo Imprint does the opposite: it locks your photo in place and only changes the brush.

`locoda/photo-imprint-skill` · the skill itself is in English, Chinese name is 印痕

```
Please help me install this skill: https://github.com/locoda/photo-imprint-skill
```

---

## When you want a whole trip to feel like one little journal

Say you just got back from Japan. Your phone is full of cups you've had, in-flight moments, that one on a Roppongi street. You want to post them, but the raw photos are messy, you don't want to show your face, and you don't want the model to invent a Tokyo Tower that was never there.

What you want is:

- small cup stays small cup, lid and logo right where they were
- background cleaned up, just a little paper breathing room, nothing invented
- three images together that feel like the same book

That's the moment Photo Imprint is for.

### Before / After

| What Photo Imprint draws | Your source (blurred for privacy) |
|---|---|
| ![imprint 01](assets/samples/01-sjc-small-cup-paper-locked-v11.webp) | ![source 01](assets/samples/source-01.webp) |
| Small cup stays small, 50% paper white, caption on top | That green drink at SJC Airport, clear lid |
| ![imprint 02](assets/samples/02-in-flight-paper-locked-v11.webp) | ![source 02](assets/samples/source-02.webp) |
| Cabin softened into a faint color block, no invented sky | The one holding a cup on the plane |
| ![imprint 03](assets/samples/03-roppongi-paper-locked-v11.webp) | ![source 03](assets/samples/source-03.webp) |
| Background reduced to a few lines, no Tokyo Tower added | That cup on a Roppongi street |

Samples are compressed to webp <100KB in `assets/samples/`. Sources are blurred 12px. Final exports are 1152×2048 jpg ~400KB, no EXIF.

---

## How to use

Once installed, three steps:

1. Drop your photos in, they get sorted by when you took them
2. It draws just the first page, you look at the plan together
3. When you say go, it draws the rest, checks everything, and zips it up

If you say "this part feels off" at any point, it only fixes that part — it doesn't redo the whole set.

The tool tells you what to do next, it doesn't run ahead on its own.

---

## How it keeps your photo

Not one prompt. It keeps five things separate:

- what to draw — from your source photo
- how to draw it — watercolor feel from your reference, but not its content
- what stays separate — image is image, paper is paper, type is type
- where it goes — 9:16 paper, where the caption sits, how big the subject is, all fixed
- how it feels like a set — same brightness, same grain, same white space

What stays locked is the silhouette and proportions. What changes is the stroke. A little diffusion at the edge, color sampled from your photo, never invented.

---

## What we want to try next

- A template for open scenery (current set is cup-on-top, scenery-below is still coming)
- Lighter install, no long pip chain
- More intuitive edits, without remembering those English verbs

---

## License

MIT — see [LICENSE](LICENSE).

## Credits

- Workflow and boundaries: `SKILL.md`
- Samples in `assets/samples/`, all locally compressed
- No licensed fonts or images that need extra permission

---

## Made by

Made by [1mether](https://1mether.me).

## If this helps

If it helped you turn a trip into something you like, consider starring the repo.

If this skill is useful to you, consider starring the repository.

---

*Keep the photo, just remember it in a different stroke.*