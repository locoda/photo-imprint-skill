# Photo Imprint (印痕)

> 不是滤镜。是保留你照片是谁，再重画它的感觉。

[English](README.md) | [中文](README.zh-CN.md)

把真实旅行照片转成一套风格统一的水彩手帐轮播，发小红书 / IG 用，不会把每张照片的身份丢掉。

`locoda/photo-imprint-skill` · 英文 skill，中文名印痕

## 能做什么

直接用 prompt 渲，好看但会忘掉你的照片。Photo Imprint 锁定杯/瓶的轮廓、比例、盖子、logo 位置，只在笔触上抽象。

| 原片 | Photo Imprint（Template B – drink-minimal-caption-above） |
|---|---|
| ![原片 01](assets/samples/source-01.webp) | ![印痕 01](assets/samples/01-sjc-small-cup-paper-locked-v11.webp) |
| SJC Airport – 小杯、绿饮、透明盖 | 同一个杯、同一个盖、同样比例。50% 留白，caption 在 y=300/367，扩散只在贴边 2-3 处，≤10% 宽度 |
| ![原片 02](assets/samples/source-02.webp) | ![印痕 02](assets/samples/02-in-flight-paper-locked-v11.webp) |
| 飞机上端杯 | 杯型锁定，机舱简化成冷色块，不编造天空 |
| ![原片 03](assets/samples/source-03.webp) | ![印痕 03](assets/samples/03-roppongi-paper-locked-v11.webp) |
| 六本木街头杯 | 杯型锁定，背景强简化，不编造东京塔 |

所有样张已本地压缩成 webp <100KB，放在 `assets/samples/`，可直接发版。完整 1152×2048 终版 jpg 399–430KB，无 EXIF。

Template A（travel-scene-caption-below，图在上字在下）同理，给 2-3 张背景干净的旅行照就能补一个例子。

## 怎么用

```bash
npx skills add locoda/photo-imprint-skill
# 或
git clone https://github.com/locoda/photo-imprint-skill.git
pip install -r requirements.txt
python3 bin/check_environment.py
```

3 步：

```bash
# 1. EXIF 排序 + manifest
python3 bin/preprocess.py --input /path/to/photos --output work/manifest.json --config work/resolved-config.json

# 2. Plan + 只渲第1页
python3 bin/build_production_plan.py --render-plan work/render-plan.json --output work/production-plan.md
# 渲第1页，和 plan 一起讨论

# 3. 明确批准后 → batch → QA → ZIP
python3 bin/package_verified.py package --input work/final --output dist/carousel.zip
```

`workflow.py status` / `next` 只读不写，告诉你下一步。

## 原理是怎么做的

不是 prompt 合集，是带门禁的生产流，把 5 个维度拆开独立控制：

1. **Theme** – 画什么（原片是权威）
2. **Style** – 怎么画（水洗、边缘、明度分组来自参考图，不带它的主体）
3. **Layers** – 什么必须分层（plate / 纸 / 文字）
4. **Composition** – 放哪（确定性合成，9:16，1152×2048，纸色 `rgb(247,244,235)`）
5. **Unification** – 怎么统一（同亮度、同颗粒、同 caption y=300/367）

流程：

```
photos → EXIF 排序 → 每页 production_brief（保留/简化/省略）→ production-plan.md
      → 只渲第1页 → 冻结 sample style contract（笔触、边缘、留白、明度、背景干净度、边框、抽象程度）
      → 讨论 plan+sample → 明确批准（原话）
      → batch 2..N 用冻结 contract → 洗版（profile-driven）
      → 确定性合成（纸、摆放、caption）→ 双层 QA
      → 已验证 ZIP（无 EXIF/GPS/XMP）
```

为什么要卡 sample？不卡会漂：小杯变大杯、瓶肩走形、MEGA 标记变样。这里有 shape-lock：

- Template B：杯/瓶轮廓、比例、盖子、液面、logo 位置锁定，抽象只在笔触和边缘
- 扩散克制：只允许 2-3 处贴边溶色（右侧 ≤10% 主体宽度，底部 ≤8% 主体高度），颜色取自主图，其余是干净纸

批准后改动用四种操作（`remove` / `retain_but_simplify` / `add_as_secondary` / `preserve_unchanged`），避免“路有点怪”被误读成“把路全删了”。

## 两套布局模板

都是 plan 的一部分，渲染前锁定，文字在合成阶段后加，不在 plate 里生成。

**Template A `travel-scene-caption-below`** – 图偏下（垂直中心 58-62%，高度 38-45%），caption 在图下方，约 50% 留白在顶部和两侧，背景只能是极淡水洗藏在主体后。

**Template B `drink-minimal-caption-above`** – caption 在上方 y=300/367，主体居中偏下 60-65%（高度 32-40%，小杯保持小），同留白，扩散克制。当前三张就用这个。

完整字段见 `production-plan.md`：canvas、paper、placement、typography（`NotoSerifDisplay-Regular 48pt / Light 27pt`，`#403C44`）、扩散限制、禁止项。

## 和直接 prompt 的区别

| 直接 prompt | Photo Imprint |
|---|---|
| 一套 prompt 渲所有页 | 每页 brief + 冻结 style contract |
| 编造背景/地标 | forbidden-inventions 列表挡住 |
| 小杯变大杯 | shape-lock，小杯保持小 |
| 三页三种纸 | 统一暖白，同亮度同颗粒，caption 对齐 |
| 无复核 | 页级合规 + 组级统一，两套独立门禁 |

## 目录

```
SKILL.md                  # 工作流（英文）
presets/travel-food-journal.json
profiles/{themes,styles,layers,compositions,unification}/
assets/samples/           # 压缩后的前后对比（webp <100KB）
assets/style-packs/       # 自带 Smithsonian 公开域风格包
tests/                    # 34 个门禁/回归测试
```

私有参考图只存本地，未经明确授权不外发。最终 ZIP 只含已验证编号图片 + release manifest。

## 验证

```bash
python3 -m unittest discover -s tests -v
python3 bin/validate_skill.py --json
```
