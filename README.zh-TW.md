# Photo Imprint (印痕)

> 留住那張照片，只換一種筆觸去記。

[English](README.md) | [简体中文](README.zh-CN.md)

你拍了一路的照片，想把它整理成一套手帳輪播，發小紅書或 IG。直接丟給模型，它會畫得很漂亮，但杯子變大了，街景變假了，你的那張照片不見了。

印痕做的是反過來的：把你的照片鎖住，只在筆觸上做變化。

`locoda/photo-imprint-skill` · skill 本身是英文的，中文名叫印痕

```
請幫我安裝這個 skill：https://github.com/locoda/photo-imprint-skill
```

---

## 想把一堆旅行照整理成一套手帳的時候

比如剛從日本回來，手機裡一堆喝過的杯子、在飛機上、六本木街頭的照片。想發，但原片太雜，不想露臉，也不想讓模型瞎編一個東京鐵塔。

你想要的是：

- 小杯還是小杯，蓋子、logo 都在原來的位置
- 背景收乾淨，只留一點紙的呼吸感，不編造
- 三張圖放在一起，看起來像同一本手帳

印痕就是為這個時刻做的。

### 前後對比

| 印痕畫的 | 你的原片（已模糊，保護隱私） |
|---|---|
| ![印痕 01](assets/samples/01-sjc-small-cup-paper-locked-v11.webp) | ![原片 01](assets/samples/source-01.webp) |
| 小杯還是小杯，蓋子比例都在，50% 留白，字在上面 | SJC Airport 那個綠飲，透明蓋 |
| ![印痕 02](assets/samples/02-in-flight-paper-locked-v11.webp) | ![原片 02](assets/samples/source-02.webp) |
| 機艙化成一塊淡淡的顏色，不編造天空 | 飛機上端著杯子的那張 |
| ![印痕 03](assets/samples/03-roppongi-paper-locked-v11.webp) | ![原片 03](assets/samples/source-03.webp) |
| 背景只剩一點線，不加東京鐵塔 | 六本木街頭的那杯 |

範例都壓成了 webp，不到 100KB，放在 `assets/samples/`。原片都做了 12px 模糊。最後匯出的 1152×2048 jpg 在 400KB 左右，不帶 EXIF。

---

## 怎麼用

裝好後，三步：

1. 把照片丟進去，按拍攝時間排好
2. 先只畫第一張，你和它一起看看計畫對不對
3. 你說可以了，它再去畫剩下的，跑完檢查，打包成 ZIP

中間任何時候你說「這裡不對」，它只改你說的那一點，不會重來一整套。

工具會告訴你下一步該做什麼，不會自己偷偷往前跑。

---

## 它怎麼留住你的照片

不是靠一句 prompt。它把五件事拆開管：

- 畫什麼，聽你的原片
- 怎麼畫，參考你給的水彩感覺，但不抄它的內容
- 哪些要分開，圖是圖，紙是紙，字是字
- 放哪兒，9:16 的紙，字在哪裡，圖佔多大，都有定數
- 怎麼像一套，三張的亮度、顆粒、留白是一樣的

鎖住的是輪廓和比例，鬆開的是筆觸。杯口那一點點化開，只在邊上，顏色也從你照片裡取，不自己發明。

---

## 以後想做成什麼樣

- 風景照的範本（現在這套是杯子在上的，風景在下的還在補）
- 更輕的安裝，不用 pip 一串
- 更直觀的改法，不用記那幾個英文動詞

---

## License

MIT — 詳見 [LICENSE](LICENSE)。

## 致謝

- 風格參考：Allen Tucker《Highway 485》和《Watercolor No. 73, Blue and Lavender》——可獨立選擇，技法分工，避免主體洩漏
- 做法和邊界以 `SKILL.md` 為準
- 範例在 `assets/samples/`，都是本地壓的
- 沒有用需要額外授權的字型或圖片

---

## Made by

Made by [1mether](https://1mether.me).

## 如果對你有用

如果它幫你把一趟旅程整理成了你喜歡的樣子，考慮給倉庫點一個 star。

If this skill is useful to you, consider starring the repository.

---

*留住那張照片，只換一種筆觸。*