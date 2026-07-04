# caw-slides デザインシステム（PPT Master default 準拠・日本語ローカライズ）

このドキュメントは、SVG-first で研究発表スライドを描くときの **オーサリング規約**。デザインは
**PPT Master のデフォルト出力に寄せる**（独自ブランドを起こさない）。配色・タイポ・レイアウトの
体系は PPT Master（© 2025–2026 Hugo He, MIT。`vendor/NOTICE.md` 参照）の default design spec を
distill し、**日本語の化学スライド向けにローカライズ**した（CJK フォントを MS Gothic に、化学
記号を扱う添字規約を明示）。個人ブランド（特定研究室のロゴ・色）は入れない。

> **§0 最優先**：スライドはテキストを読ませる媒体でなく、**図表で瞬時に伝える視覚装置**。数値・
> 比較・時系列・プロセス・関係は必ず図表（table / chart / flow / scheme）で。1 スライド 1 メッセージ。

---

## 1. キャンバス

- `width="1280" height="720" viewBox="0 0 1280 720"`（16:9・単位は unitless px）
- **安全マージン**：左右 80px、上下 50–72px。本文右端は ~1200px（右マージン 80）。
- 出力 pptx は 13.33in × 7.5in に自動マップ（vendor 変換器が担当）。

---

## 2. ページ家具（default レイアウト）

### 表紙（cover）
- 左端に navy の縦アクセントバー：`<rect x="0" y="0" width="12" height="720" fill="{ink}"/>`
- kicker（小見出し）：accent バー `rect x80 y150 w46 h6 fill={highlight}` ＋ `text x80 y192, 16px bold {primary} Arial letter-spacing="2"`
- タイトル：`text x80 y~292, 40–46px bold {ink}`（和文フォント）。副題 `22px {body}`。
- takeaway パネル（任意）：角丸 `path fill={panel}` に 1 行要約（色付き tspan で数値強調）。
- メタ：著者・誌名・DOI を `text x100, 16–19px {body}/{ink} Arial`、左に `rect w4 h60 fill={primary}`。

### 本文ページ（content）
- 背景：`<rect x0 y0 w1280 h720 fill={bg}/>`
- **ヘッダ**：`rect x80 y72 w40 h6 fill={primary}`（アクセントバー）＋ kicker `text x80 y104 15px bold {primary} Arial letter-spacing="2"`（和文語は tspan で MS Gothic）＋ タイトル `text x80 y142 28px bold {ink}` ＋ 区切り線 `line x1=80 x2=1200 y=166 stroke={divider}`。
- **本文エリア**：y~190–650。§4 のレイアウトパターンから選ぶ。
- **フッタ**：出典 `text x80 y694 13px {grey} Arial`（左）＋ ページ番号 `text x1200 y694 13px {grey} text-anchor="end"`（右、`"N / M"`）。

> タイトルは**主張形**にする（❌「結果」→ ✅「三重項が単項の約 300 倍」）。

---

## 3. 配色（role ベース・11 役）

PPT Master は配色を **役割で定義**し、デッキごとに値を選ぶ。caw の**既定パレット**（プロ調・化学に無難、
Master default 互換。上書き可）：

| 役割 | 既定 HEX | 用途 |
|---|---|---|
| background | `#FFFFFF` | ページ背景 |
| ink（primary text/dark） | `#16283D` | タイトル・濃色 |
| primary（accent） | `#1F6FEB` | アクセントバー・kicker・強調 |
| highlight | `#E8A33D` | 表紙装飾・注意喚起（gold） |
| positive | `#2E9E6B` | 良い方向の数値（green） |
| negative | `#D6455D` | 悪い方向・主強調（red） |
| body | `#47535F` | 本文 |
| panel（secondary bg） | `#F2F6FA` | カード・パネル背景 |
| grey（tertiary） | `#8894A2` | 脚注・出典・補足 |
| divider | `#D8E0E8` | 区切り線（薄 `#E0E6EC`） |
| table-head | `#16283D` | 表ヘッダ（白文字） |

- 透明度は `fill-opacity` / `stroke-opacity`（**`rgba()` 禁止**）。グラデは `<linearGradient>`/`<radialGradient>` ＋ `stop-opacity`。
- **グループ不透明度 `<g opacity>` 禁止**：各子要素に個別指定。

---

## 4. レイアウトパターン（情報の重みに従う。preset 比率に固執しない）

| パターン | 適する場面 |
|---|---|
| 単一カラム中央 | 表紙・結論・キーポイント |
| 対称 5:5 | 対等な 2 者比較 |
| 非対称 3:7 / 2:8 | 片方が主（図 vs 一言、データ vs 要約） |
| 上下分割 | プロセス・時系列・横長図＋説明 |
| 3–4 カラムカード | 並列項目・特徴列挙 |
| 2×2 マトリクス | 二軸分類・象限 |
| 中心放射 | コア概念＋周辺ノード・生態系図 |
| 図文オーバーラップ | ヒーロー（大数値・見出しを図に重ねる） |
| 余白主導 | 1 要素＋40–60% 余白で 1 論点を効かせる |

- 毎ページ対称グリッドにすると「AI くさい」→ **意図的に変える**。
- カード：角丸 8–16px、padding 20–32px、gap 20–32px。ブロック間 gap 24–40px。

---

## 5. タイポグラフィ（日本語ローカライズ）

### フォント（PPT-safe・run 末尾は必ずプリインストール書体）
- **和文**：`font-family="'MS Gothic','Hiragino Kaku Gothic ProN',Arial"`
- **英数**：`font-family="Arial"`
- 混在（英数ベースに日本語語句）：ベースを Arial にし、日本語語句だけ `<tspan font-family="'MS Gothic',...">…</tspan>` で囲む（例：`KINETICS <tspan …>速度論</tspan>`）。**逆も同様**（和文ベースに英数はそのまま Arial 継承可）。

### サイズ（body 基準の比率ランプ・unitless px、pt 禁止）
研究スライドは密度が高いので **body ≈ 16px** を既定にする（Master の balanced=24 より密。目的で調整）。

| 役割 | 既定 px | 太さ |
|---|---|---|
| 表紙タイトル | 40–46 | Bold |
| ページタイトル | 28 | Bold |
| セクション/パネル見出し | 17–22 | Bold/SemiBold |
| 本文 | 16 | Regular |
| 注釈・出典・脚注 | 13–15 | Regular |
| ヒーロー数値（KPI） | 60–96 | Bold |

- 同じ役割はデッキ全体で**同一サイズを固定**（ばらつきは素人っぽさの元）。16px 未満に自動縮小しない。

### 添字・上付き（化学で頻出・ここが罠）
- **Unicode の ₁ / ⁻ を使わない**。`<tspan baseline-shift="super" font-size="11">−4</tspan>` /
  `baseline-shift="sub"` で描く（例：`10<tspan baseline-shift="super" font-size="11">−4</tspan>`）。
- 添字 font-size は本体の ~0.6–0.7×。

---

## 6. アイコン・装飾

- **アイコンは native shape/path で自作**（`<circle>`/`<rect>`/`<path>`/`<line>`）。PPT Master の
  `<use data-icon="lib/name">` 方式は **caw では使わない**（11,600 アイコンライブラリを同梱しないため
  vendor 変換器で解決できない）。線画アイコンは細い stroke の path で描く。
- 表紙の同心円・アクセント図形などの装飾は native shape で。

---

## 7. SVG オーサリングの厳守事項（これを守らないと変換器が壊れる）

PPT Master `shared-standards.md`／`design_spec_reference §XI` 由来のハード制約：

1. **禁止要素**：`mask` / `<style>` / `class` / `<foreignObject>` / `textPath` / `animate*` / `<script>`。
2. **テキスト折返しは `<tspan>`**（`<foreignObject>` 不可）。座標は各 text/tspan に明示。
3. **透明度**：`fill-opacity` / `stroke-opacity`（`rgba()` 不可）。`<g opacity>` 不可（子に個別）。
4. **文字**：約物・記号は **raw Unicode**（`—` `–` `©` `→` `·` を直接）。HTML 実体参照（`&mdash;`
   `&nbsp;` 等）**禁止**。XML 予約文字は実体で（`R&amp;D`、`error &lt; 5%`）。
5. **背景は `<rect>`**。角丸ボックスは `<rect rx>` か `<path>`（`A` 円弧）で。
6. `marker-start`/`marker-end` は条件付き可（`<marker>` は `<defs>` 内・`orient="auto"`・形は三角/菱形/円）。
7. `clipPath` は **`<image>` 要素にのみ**可（`<defs>` 内・単一 shape child）。shape/group/text には使わず、目的の形を native 要素で直接描く。
8. インラインスタイルのみ。外部 CSS・`@font-face` 不可。

---

## 8. ゲートが拾わない 2 つの罠（目視 QA で必ず確認）

フォント/重なりゲート（§scripts）が緑でも残る既知の罠：

1. **中央寄せ × 混在フォント × 添字**：`text-anchor="middle"` のラベルに Arial tspan＋baseline-shift 添字が混ざると変換器が幅を誤測し、後続日本語が重なる/添字が飛ぶ。→ **中央寄せラベルは単一 MS Gothic 化**（Latin も MS Gothic で可）。**添字を含む式は左寄せ**にして x を手動調整。
2. **丸数字 ①②③（U+2460+）は Arial に無く豆腐 □**。→ 丸数字は必ず **MS Gothic run 内**に置く。
- ビルド後の pptx は **全ページ目視**（プレビュー PNG は scratchpad で生成し配布先には置かない）。

---

## 9. 内容の型（研究発表・目安）

- **論文紹介（6 枚）**：①表紙 ②背景・系 ③機構 ④自作データ（表 or 手描き chart）⑤速度論・主要図 ⑥結論＋**自研究への接続**。自作の表・図 ＋ 論文からの切り抜き図（`scripts/crop_paper_figures.py`）を混在。各図スライドに「図の読み方」支持本文（軸・色・主要数値・1 行解釈）を添える。
- **学会発表・報告会・講義**：用途別の目安は SKILL.md 参照。いずれも §0（図表優先・1 スライド 1 メッセージ）を最優先。

---

## 10. 由来と上書き

- 本デザインは **PPT Master default の distill＋日本語ローカライズ**。忠実度が最優先。
- プロジェクト固有の色・サイズ・語調は `office/presentation/CLAUDE.md`（Codex/Copilot は `AGENTS.md`、Gemini は `GEMINI.md`）に足す。本ファイル（配布物）は更新で上書きされるので直接編集しない。
