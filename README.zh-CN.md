# Photo Imprint (印痕)

> 留住那张照片，只换一种笔触去记。Keep the photo, remember it in a different stroke.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) [![Version](https://img.shields.io/badge/version-1.2.0-blue)](SKILL.md) [![Skill](https://img.shields.io/badge/skill-photo__imprint-teal)](#)

`locoda/photo-imprint-skill` · 英文 skill，中文名印痕 · 9:16 竖版轮播，EXIF 排序，门禁式生产

---

## 一个让人有力量的瞬间

你在 SJC 买了一杯小杯，飞机上托盘里端着它，六本木夜里拎着它走了几条街。十二张照片躺在相册里——太私人不敢直接发，太散又不成故事。

你打开印痕。它按 EXIF 拍摄时间排序，锁住你真正拿过的那个杯子——轮廓、盖子、比例、logo 位置——为每一页写一页 `production_brief`。只渲第一页。

你看了一眼第一页说：“就要这个笔触，盖子保持这样，机舱简化成冷色块。”这句原话被原样记录为批准。

批处理用冻结的 `sample_style_contract` 跑完剩余页。版面按当前样式策略做 clean-plate 归一化，确定性合成为 1152×2048 暖白纸 `rgb(247,244,235)`，约 50% 留白，caption 在 y=300 / y=367，扩散克制在贴边 2–3 处、宽度 ≤10%。双层 QA 要求全尺寸和 360×640 手机尺寸逐页打开检查。ZIP 里不含 EXIF / GPS / XMP。

第一次把轮播发到小红书 / IG 时，你发现它仍然是你的那次旅行——只是换了一种笔触被记住了。你感到被看见了，但没有被改掉。被记住的掌控感，是这个 skill 想给的瞬间。

---

## 我们是怎么实现这个目的的

不是 prompt 合集，是把五个维度拆开独立控制的门禁流，笔触换了，照片还在。

### 1. Theme —— 画什么，以原片为准
原片是权威。每一页都要填完整的 `production_brief`：主体优先级、手机缩略图可读性、身份锚点、要抽象或省略的细节、材质/深度线索、来源支撑的结构线（`retain` / `retain_but_simplify`），以及 `forbidden_inventions`。不编造地点、日期、caption，除非你提供或明确允许草稿模式。

### 2. Style —— 怎么画，只取技法不取主体
样式只贡献技法，不贡献主体。自带的两个 Smithsonian 公开域风格包 `blue-lavender-watercolor` 和 `highway-485-lithograph`（Allen Tucker，公共域）各自声明 `technique_roles` 和 `subject_exclusions`，只有前者能进入渲染。可复用 preset 默认仍是 `watercolor-journal`，除非你的项目 preset 明确改名。生成的第一页永远不能成为风格参考。

Shape-lock 是它能留住照片的原因：Template B 锁定杯/瓶轮廓、比例、盖子、logo 位置，抽象只发生在笔触和边缘，颜色取自主图，扩散克制。

### 3. Layers / Composition / Unification —— 分层、放哪里、怎么统一
- **Layers** 管 plate / 纸 / 文字的分层与谁负责渲染。
- **Composition** 管确定性 9:16、1152×2048、暖白纸、摆放（Template A `travel-scene-caption-below` 图偏下 58–62%，Template B `drink-minimal-caption-above` 字在上）、字体 `NotoSerifDisplay-Regular 48pt / Light 27pt #403C44`、扩散限制、禁用元素。
- **Unification** 管共用纸张、亮度、颗粒、caption y、节奏。

`presets/travel-food-journal.json` 提供完整的工作流默认值，但真正的版面仍需要已配置的渲染器和已验证的收据（`renderer_receipt.py`，记录模型/版本/seed/设置与来源/参考/输出哈希）。`not-configured` 收据是诚实的阻塞，不是继续的许可。

### 4. 门禁式生产 —— 先 plan + sample，再明确批准
```
photos → EXIF 排序 → 每页 brief + sample_style_contract → production-plan.md
      → 只渲第1页 → 冻结 sample style contract
      → 一起讨论 plan+sample（artifact 或忠实摘要）→ 记录讨论方式
      → 你的原话明确批准 → 用冻结 contract 批处理 2..N
      → 按 profile 归一化 clean plate → 确定性合成
      → 双层 QA → 已验证 ZIP + release manifest
```
`workflow.py status` / `next` 只读不写，只告诉你下一步。私有参考图默认只存本地，传给外部图像服务需要另外的明确授权。

### 5. 双层独立 QA 与已验证打包
- **页级合规：** 每页是否满足自己的主体优先级、缩略图可读性、身份锚点、材质/深度线索、结构线操作、没有 forbidden inventions、背景干净、无矩形接缝/禁用边框。
- **组级统一：** 整组视觉是否统一、共用纸张一致、样式/笔触一致、字体一致、顺序/尺寸一致、跨页节奏、选配模块完整性。

任一维度不通过都阻止打包。`package_verified.py stage` 锁住带编号图片的哈希，QA 针对该 exact stage 跑，`package` 再校验来源、caption、渲染器/版面溯源、QA 锁、审核证据、staged 字节是否一致。交付时只复制已验证的 staged 产物，不重新生成。终版不含 EXIF / GPS / XMP。

### 6. 批准后修订不跑偏
非 sample 页的局部修订只允许四种操作：`remove`、`retain_but_simplify`、`add_as_secondary`、`preserve_unchanged`。Scope 只标记受影响页为 stale，未改动的已批准页保持哈希锁定。任何对第1页 / style contract / 来源/顺序 / 共享布局 / 系统 plan 的改动都会使批量批准失效，回到 plan+sample 门禁。

---

## 遗留议题与未来期冀

**1.2.0 诚实的限制：**

- 未自带图像生成后端。必须配置渲染器并提供已验证收据，否则在 render scope 停止。
- 字体需要提供可读的字体文件，不做静默替换。
- Template A（开阔旅行场景）已实现，但本仓库暂无锁定样张——提供 2–3 张场景照即可在 `assets/samples/` 补充 Template A 示例。
- 三个纯文本样式 profile 仍为 `reference_status: pending-selection`：`watercolor-journal`、`botanical-watercolor`、`paper-collage`，在加入带完整来源元数据的已批准参考前，靠文本规则渲染并保留警告。
- 私有参考图本地存储与外部处理是两次独立授权，本地有文件不代表允许上传。
- 仅靠 contact sheet 不能通过 QA——每页都必须有全尺寸与手机尺寸证据。

**未来方向（不是已实现功能）：**

- 更多布局模板（城市地图、食物手帐），保持 9:16 与约 50% 留白。
- 更多 Smithsonian 公开域风格包，满足单项权利验证与衍生图优化（长边 1600px、WebP 82–88、≤750KB）后入仓。
- 选配模块（手绘感 route 线与起止 marker、作为项目覆盖的 watermark、披露文案）保持可拆卸、默认关闭。
- 手机缩略图调优助手与 EXIF 校验 caption。
- 与对坐、牌间共享的评测集：来源忠实度、样式边界、版式合规、整组一致性。

---

## License

MIT License — Copyright (c) 2026 locoda。见 [LICENSE](LICENSE)。代码与文档为 MIT；自带风格包衍生图为公共域，单独溯源见 `assets/style-packs/*/source.json`。

## 素材与引用

- **自带样式参考（可选）：**
  - Allen Tucker *Watercolor no. 73, Blue and Lavender*（1928，水彩，Smithsonian American Art Museum 1966.34.7）——技法：透明水洗、软硬边过渡、冷蓝/薰衣草明度分组、选择性深色锚点。排除：海景、岸线、水天线、风景主体、构图。衍生图：1600×1107 WebP，242KB，已剥离 EXIF/GPS/XMP。来源 TIFF 149MB。权利：公共域，可自由使用。[馆藏记录](https://americanart.si.edu/artwork/watercolor-no-73-blue-and-lavender-24276)
  - Allen Tucker *Highway 485*（版画，SAAM 1966.34.9）——技法：稀疏断续干蜡笔/轮廓线、纸白留白、克制深色点缀、极度简化、有限排线。排除：道路、路牌、电线杆、电线、风景主体、构图。衍生图：1600×1113 WebP，83KB。权利：公共域。[馆藏记录](https://americanart.si.edu/artwork/highway-485-24266)
  - 均存于 `assets/style-packs/*/reference.webp`，`source.json` 含机构、藏品号、授权链接、检索日期、衍生设置。

- **Preset 与 profiles：** `presets/travel-food-journal.json` 组合五个关注点（theme/style/layers/composition/unification）与 `workflow_defaults`（EXIF 排序、强制 production-plan、仅第1页 sample、明确批准、确定性合成、类型化修订、哈希锁定 staging）。

- **字体 / 排版：** 默认排版期望 `NotoSerifDisplay-Regular` / Light（SIL OFL），需自行提供可读字体文件，skill 会校验并记录到 composition manifest。

- **校验：** `tests/` 含 34 项门禁/回归测试，`bin/validate_skill.py`、`bin/check_environment.py`。

私有参考图未获授权前不进入版本控制与交付，未获外部处理明确授权前不上传外部图像服务。

---

## Made by

Made by [1mether](https://1mether.me)。

---

如果这个 skill 对你有用，欢迎给仓库点个星。

[English](README.md) | [中文](README.zh-CN.md)
