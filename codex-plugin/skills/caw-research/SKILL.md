---
name: caw-research
description: >
  「調べる（discovery）」スキル（研究・就活の両トラック対応）。研究トラックでは関心テーマの論文を検索し、クリックで論文ページに飛べる HTML リスト（work/topics/<topic>_<日付>_n<件数>.html）に書き出す（入手 PDF の登録・要約は caw-paper が担当）。
  就活トラックでは企業・業界を採用ページ・IR・ニュース等の公開情報から調べ、調査レベルと出力形式を選ばせて work/companies/ に汎用 8 ブロックで構造化し、必要なら HTML 可視化する。
---

# caw-research — 調べる（研究＝論文検索 / 就活＝企業・業界研究）

「調べる（discovery）」を担当する両トラック対応スキル。**研究トラックでは関心テーマの論文を検索して `work/topics/` に HTML リスト化**（タイトルをクリックで論文ページへ）し、**就活トラックでは企業・業界を公開情報から汎用 8 ブロックで構造化**する。トラックはプロジェクト設定で自動判定する。

## いつ使うか

- `/caw-research` を実行したとき
- 研究：「○○ について論文を集めて / 検索して」「関心テーマの文献を調べて」「最近の○○の論文は？」
- 就活：「○○社について調べて」「企業研究して」「業界研究して」「HTML で可視化して」「比較表を作って」

`office/` が無ければ `/caw` でセットアップを促す。該当部署（研究=research / 就活=research〔企業・業界研究〕）が未作成なら作成を提案する。

## トラック判定（最初に必ず）

`office/AGENTS.md`（Claude Code は `CLAUDE.md`、Gemini は `GEMINI.md`）の冒頭を読み、**`> トラック: 就活` があれば就活トラック（企業・業界研究）**、無ければ**研究トラック（論文検索）**として、対応するワークフローを実行する。

## はじめてモードを尊重する

このスキルを実行する前に `office/AGENTS.md`（Claude Code では `CLAUDE.md`）を読み、冒頭に `> 運用モード: はじめて` があれば、`caw` skill の「はじめてモードの挙動」を全応答に適用する：**平易な日本語**で話し、専門用語（arXiv・DOI・preprint・IR・選考フロー 等）は初出で 1 行説明を添え、各ステップの最後に**「次はこれをしましょう」を 1 つ**だけ提示する。

## 研究トラック：論文検索（関心テーマの文献を一括収集）

研究プロジェクトで「論文を探す・集める・文献調査する」段階を担当する。**探索してリスト化するところまで**が役割で、入手した PDF の登録・書誌付き要約・ナレッジベース登録は **`caw-paper`** が担当する（discovery と library の分担）。`office/research/` が無ければ `/caw` で research 部署追加を促す。

### R-Step 1: 入力を確認

- **検索テーマ**（例: "MOF-based luminescence", "mechanochromism in single crystals"）
- **件数**（既定 50、最大 100 程度）
- **期間 / ジャーナル絞り込み**（任意）

はじめてモードでは件数・期間を 1 つずつ平易に確認する。

### R-Step 2: 検索ソース（優先順に組み合わせ）

1. **arXiv API**（preprint・arXiv ID）
2. **Crossref API**（DOI lookup・書誌の最終確認）
3. **Semantic Scholar API**（引用ネットワーク・分野横断）
4. **OpenAlex API**（大規模・無料）
5. **PubMed API**（生命科学・医薬）
6. **WebFetch / Exa**（上記で拾えない場合の web 検索フォールバック）

web 検索 / MCP が使えない場合は、ユーザーに検索結果・キーワード・控えの貼り付けを依頼してフォールバックする。

### R-Step 3: HTML リストに書き出す（成果物）

`work/topics/<topic-slug>_<YYYYMMDD>_n<件数>.html` を生成する（**md は作らない**）。**1 ファイルで完結するオフライン HTML**（インライン CSS・CDN/JS なし）。ダブルクリックで開け、ネット接続なしで表示できる（論文リンクを押したときだけ通信）。**並べ替えのない静的な縦リスト**。

**ファイル名規則**：`<topic-slug>_<YYYYMMDD>_n<件数>.html`（例 `mof_20260618_n10.html`＝MOF・2026-06-18 取得・10 件）。`<topic-slug>` は検索テーマを小文字 ASCII の kebab-case に（日本語テーマは英語キーワードかローマ字、~40 字以内）。`<YYYYMMDD>` は取得日、`n<件数>` は掲載論文数。**同じテーマを再検索しても上書きせず日付で別ファイルとして残す**（同一 topic+日付が既にあれば末尾に `-2`, `-3`）。

**構成**
- **ヘッダ**：トピック名（`<h1>`）／検索条件（キーワード・期間・ジャーナル絞り込み）／件数／取得日／使用ソース。
- **本文＝縦リスト**（`<ol>`、1 論文 1 ブロック、薄い罫線区切り）。各ブロック：
  - **タイトル（必ずハイパーリンク）**：飛び先は DOI があれば `https://doi.org/<doi>`、arXiv なら `https://arxiv.org/abs/<id>`、どちらも無ければ Google Scholar 検索（`https://scholar.google.com/scholar?q=<タイトルを URL エンコード>`）。`target="_blank" rel="noopener"`。
  - **メタ行**（グレー小）：著者（多ければ「First 他」）・年・誌名。
  - **要約 1〜2 文**。
  - **補助リンク**：`DOI 10.1021/… ↗` または `arXiv:… ↗`（タイトルと同じ飛び先）。
- **フッタ**：「読みたい論文は PDF を `work/papers/` に置いて『登録して』と言うと `caw-paper` が要約・登録します」。

**デザイン**（装飾は最小・製品配色に合わせる）。`<style>` に：
`:root{--ink:#181d26;--body:#333840;--accent:#aa2d00;--line:#e2e2e2;--muted:#8a8a8a}` ／
`body{font-family:Inter,-apple-system,'Segoe UI','Hiragino Sans',sans-serif;color:var(--body);max-width:820px;margin:28px auto;padding:0 18px;line-height:1.7}` ／
`h1{font-size:20px;color:var(--ink);margin:0 0 4px}` ／ `.cond{color:var(--muted);font-size:13px;margin:0 0 18px}` ／
`ol.papers{list-style:none;padding:0;margin:0}` ／ `ol.papers>li{padding:14px 0;border-bottom:1px solid var(--line)}` ／
`a.ttl{color:var(--accent);font-weight:600;text-decoration:none;font-size:15.5px}` ＋ `a.ttl:hover{text-decoration:underline}` ／
`.meta{color:var(--muted);font-size:13px;margin:3px 0}` ／ `.sum{font-size:14px;margin:3px 0}` ／ `.id a{color:var(--muted);font-size:12.5px;text-decoration:none}` ／
`footer{color:var(--muted);font-size:12.5px;margin-top:20px;border-top:1px solid var(--line);padding-top:12px}`。
**影・色面・アイコン画像・背景色は使わない**（罫線区切りのみ）。

**雛形**

```html
<!doctype html><html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title><topic> — 文献リスト</title>
<style>/* 上記 */</style></head><body>
<header>
  <h1><topic></h1>
  <p class="cond">キーワード: … ／ 期間: … ／ 全 N 件 ／ 取得 YYYY-MM-DD ／ ソース: arXiv, Crossref …</p>
</header>
<ol class="papers">
  <li>
    <a class="ttl" href="https://doi.org/10.1021/…" target="_blank" rel="noopener">Tunable luminescence in coordination polymers</a>
    <div class="meta">Tanaka, Sato 他 · 2024 · J. Am. Chem. Soc.</div>
    <div class="sum">配位子置換で MOF の発光を可逆制御……（1〜2 文）</div>
    <div class="id"><a href="https://doi.org/10.1021/…" target="_blank" rel="noopener">DOI 10.1021/… ↗</a></div>
  </li>
  <!-- 件数分くり返し -->
</ol>
<footer>読みたい論文は PDF を <code>work/papers/</code> に置いて「登録して」と言うと caw-paper が要約・登録します。</footer>
</body></html>
```

**注意**：リンクは必ず実在の飛び先にする（DOI/arXiv が取れない論文は Google Scholar 検索リンクにフォールバック）。**要約はユーザーの言語（既定で日本語）で書く**（原文が英語でも日本語に要約する）。abstract が取得できない・出版社のボイラープレートで壊れている場合は、タイトルから内容を 1 行で示し「※要約データなし」を添える（具体的な知見は捏造しない）。HTML 生成のために書誌・要約を捏造しない。

### R-Step 4: 次の一歩（`caw-paper` へ橋渡し）

- 読みたい論文を選んでもらい、「**PDF を `work/papers/` に置いて『登録して』と言えば `caw-paper` が書誌付き要約と KB 登録をします**」と案内する（**PDF 自動ダウンロードは無し**＝ユーザーが手動で取得）。
- リストの DOI / arXiv ID は残す（`caw-paper` が登録時の重複チェックに使う）。

### 注意（研究トラック）

- **件数・カバレッジを正直に報告**（取りこぼしを黙らない）。一次情報（DOI・原著）を優先。
- メタデータは API の返り値をそのまま使い、**捏造しない**。読めなかった項目は「—」にする。

---

## 就活トラック：企業・業界研究

### Step 1: 対象・調査レベル・出力形式を確認（`AskUserQuestion`）

**【必須・省略禁止】caw-research を発動したら、調査を始める前に必ず `AskUserQuestion` で「調査レベル」と「出力形式」を尋ねる。** ユーザーが企業名・業界だけを伝えた場合でも（例:「味の素について企業研究して」）、**勝手に既定（L2・md 等）で進めず、必ず一度尋ねてから着手する**。確認するのは次の 3 つ（はじめてモードでは特に丁寧に）。

1. **対象**：企業名（または業界）。複数社なら 1 社ずつ進める。
2. **調査レベル（3 段階）**：
   - **L1 クイック** — 要点だけ（汎用 8 ブロックの A・B・C・F を要約）。短時間で全体像をつかむ。
   - **L2 スタンダード** — L1 ＋ D 競合・E 主要リスク・G 選考/ES・H 接点。志望動機が書ける深さ。
   - **L3 ディープ** — 全 8 ブロック ＋ 拡張（財務/競合チャート・職種別・想定問答骨子・併願比較・選考準備チェックリスト・直近トピック）。
3. **出力形式（md / html / 両方。推奨は md）**：
   - **md のみ（推奨）** — `work/companies/<企業>.md`（業界研究は `work/companies/_industry/<業界>.md`）に構造化。
   - **html のみ** — ブラウザで開ける `work/companies/<企業>.html`。
   - **両方** — md ＋ html。

> **md を「推奨（初期選択）」として提示するが、尋ねること自体は絶対に省略しない**（自動で md にしない）。調査レベルも推奨を押し付けず L1/L2/L3 から選んでもらう。「HTML で可視化して」と明示されたときは html を初期選択にする（その場合も確認は取る）。

### Step 2: 情報収集（出典の取り方）

- **web 検索 / MCP が使える場合**: 公式採用ページ・IR・最近のニュースを取得する。**一次情報（公式採用ページ・IR）を優先**
- **使えない場合（フォールバック）**: ユーザーに採用ページ URL や説明会資料の貼り付けを依頼し、それを材料にする
- 口コミ・評判は参考に留め、**出典を併記し断定しない**

#### 出典の取り方（正確性の担保）

情報を「公式 / 非公式」で区別し、裏取りの強度を変える：

- **公式情報＝単一ソースで可**：売上・利益・従業員数・受注残などの財務指標（IR・有価証券報告書）、初任給・募集要項・求める人物像（公式採用ページ）、平均年収（有価証券報告書の記載値）。一次情報そのものなので 1 出典でよい。
- **非公式情報＝複数ソースで裏取り必須**：年代別の年収カーブ・職種別年収・残業時間・有給取得率・口コミスコア・離職率・採用大学/倍率、および**競合他社の年収など「他社」の非公式値**。集計サイト・口コミ DB（OpenWork 等）・まとめ記事が出典になるため、**2 つ以上の独立したソースで値を突き合わせて**から記載する。
  - 値が割れたら**単一値に丸めず「約 X〜Y 万」の幅**か、**年度・基準を併記**する（例:「2025/3 期有報 1,018 万、前年 965.5 万」）。出典差に見える数値が**実は年度差**のことが多いので、年度をまず疑う。
  - 口コミ由来の数値は「**クチコミ集計値**」と明示し、回答件数が分かれば添える。
  - 真に独立な 2 ソースが見つからない値は「**要確認**」とし、断定しない。

### Step 3: 汎用 8 ブロック × 調査レベルで整理

調べた内容を**汎用 8 ブロック**に整理する（企業でも業界でも同じ骨組み）：

| ブロック | 内容 |
|---|---|
| **A 基本・沿革** | 事業内容・主力製品/サービス・ビジネスモデル・沿革 |
| **B 財務・規模** | 売上・利益・従業員数・時価総額・セグメント |
| **C 戦略・競争優位** | 中期戦略・強み/弱み・競争優位の源泉 |
| **D 業界・競合** | 業界の構造・市場規模・競合比較・業界内ポジション |
| **E リスク・ガバナンス・ESG** | 事業/政策/地政学リスク・ガバナンス・ESG |
| **F 働く環境・キャリア** | 年収・残業・有給・キャリアパス・働き方 |
| **G 採用・選考** | 募集職種・求める人物像・選考フローと締切・ES 設問 |
| **H 接点・想定問答** | 自分との接点・志望動機の素材・想定問答・併願 |

調査レベルで深さを変える：

- **L1** = A・B・C・F の要約
- **L2** = L1 ＋ D・E（主要リスク）・G・H
- **L3** = 全 8 ブロック ＋ 拡張（B/D のチャート・G 職種別・H 想定問答骨子と併願表・直近トピックのタイムライン・選考準備チェックリスト）

### Step 4: md にまとめる（既定の成果物）

出力形式が **md** または **両方**なら、`work/companies/<企業名>.md`（業界研究は `work/companies/_industry/<業界名>.md`）に上の 8 ブロックを調査レベルの深さで書く。

- **冒頭に出典方針ノート**を置く：「公式情報は単一の一次出典、非公式情報は複数ソースで裏取りし幅・年度・クチコミ集計を明示」。冒頭に**調査レベル（L1/L2/L3）と取得日**も記す。
- 各ブロック末尾に**出典リンク**と**取得日**を併記（採用条件は年度で変わるため）。
- H ブロックの「自分との接点」は `caw-es`（志望動機）・自己分析部が再利用できる形で 2〜3 点まとめる。

### Step 5: HTML 可視化（出力形式が html または 両方のときだけ）

出力形式で **html** または **両方**を選んだときに実施する。md と同じ 8 ブロックの内容を、ブラウザでダブルクリックして開ける HTML に可視化する。調査レベル（L1/L2/L3）が HTML の情報量に対応する。

#### Step V0: グラフの作り方を選ぶ（`AskUserQuestion`）

```
グラフの作り方を選んでください:
  - オフライン自己完結（推奨）— ネット不要・ダブルクリックで確実に開く・CDN 切れで壊れない
  - Chart.js（リッチ）— インタラクティブだが開くときネット接続が必要
```

- **オフライン自己完結** → チャートはインライン `<svg>`（棒=`<rect>`、レーダー=`<polygon>`、散布=`<circle>`）。外部リソース 0
- **Chart.js** → `<head>` に `<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>`、`<canvas>` + JS でレーダー/棒/散布を描く

#### 共通デザイン（インライン CSS、製品 Web と統一）

白基調 + インク文字 + コーラルのアクセント、ハネ線カード、システム/Inter フォント。`<style>` に次を入れる：
`:root{--ink:#181d26;--body:#333840;--accent:#aa2d00;--line:#ddd;--bg:#fff}` ／
`body{font-family:Inter,-apple-system,'Segoe UI',sans-serif;color:var(--body);background:var(--bg);max-width:960px;margin:24px auto;padding:0 16px;line-height:1.6}` ／
カード=`border:1px solid var(--line);border-radius:10px;padding:16px`。見出しは `--ink`、強調・バッジは `--accent`。

#### 生成するビュー（依頼・調査レベルに応じて）

**A. 企業プロファイル（1社）→ `work/companies/<企業slug>.html`**
ヘッダ（社名 + 業界バッジ + 志望度 ★n/5）→ 事業概要 → 強み/弱み（2 カラムカード）→ 求める人物像 → 募集要項テーブル → 選考フロー（横並びステップ ●ES→●適性→●一次→●最終、各ノードに日付）→ 自分との接点 → フッタ（出典・取得日）。

**B. 企業比較（複数社）→ `work/companies/_compare.html`**
比較テーブル（行=社、列=規模/志望度/働き方/年収レンジ/締切 等を `work/companies/*.md` から抽出）→ 属性チャート（4〜6 軸のレーダー、または属性別の横棒）→ 選考スケジュール timeline（横軸=日付、各社の締切・選考日をマーカー、締切が近いほど色を強める）。

**C. 業界ポジショニングマップ → `work/companies/_industry/<業界slug>.html`**
2 軸の散布図（既定: 横=規模、縦=成長性。軸はユーザーに確認可）。各社を点 + 社名ラベルでプロット。四隅に象限の意味を薄く注記。

#### チャート雛形

オフライン（横棒、値は 0–100 に正規化）:
```html
<svg viewBox="0 0 320 22" width="320" height="22" role="img">
  <rect x="80" y="5" width="240" height="12" fill="#eee" rx="6"/>
  <rect x="80" y="5" width="170" height="12" fill="#aa2d00" rx="6"/>
  <text x="0" y="15" font-size="12" fill="#333840">技術力</text>
</svg>
```
レーダーは中心 (cx,cy) + 半径 × 値で各軸の点を求め `<polygon points="...">`、散布は線形スケールで `<circle>` + `<text>`（社名ラベル）。

Chart.js（CDN モード、レーダー例）:
```html
<canvas id="chRadar" width="400" height="400"></canvas>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
new Chart(document.getElementById('chRadar'),{type:'radar',
  data:{labels:['規模','成長性','志望度','働き方','年収'],
        datasets:[{label:'A社',data:[4,5,4,3,4],borderColor:'#aa2d00'}]}});
</script>
```

#### 保存と確認

- 保存先（すべて `work/` 配下）: `work/companies/<企業slug>.html` ／ `work/companies/_compare.html` ／ `work/companies/_industry/<業界slug>.html`
- 生成後にファイルパスを伝え、「ブラウザで開いてください」と案内（はじめてモードなら開き方も 1 行添える）

#### 可視化の注意

- データは `work/companies/*.md`（または収集した事実）のみ。HTML のために数値を**捏造しない**。値が無い属性は「—」やグレー表示にする
- 規模・成長性などの**推定スコアを使う場合は「推定」と明記**し、出典のある事実と区別する
- **各セクションに出典リンクを併記**する。公式（IR・採用）は単一リンク、非公式（年収・残業・有給・口コミ・競合値）は**複数リンクを並べ**、`公式 / 非公式（複数で裏取り）` のラベルで強度を区別する（Step 2「出典の取り方」と一致させる）
- **冒頭に出典方針のノートを置く**：「公式情報は単一の一次出典、非公式情報は複数ソースで裏取りし幅・年度・クチコミ集計を明示」
- 個人情報・企業の非公開情報は HTML に書かない（共有されやすい形式のため）
- グラフを使う場合、**見出しアンカー id（`<h2 id="...">`）と `<canvas id="...">` を必ず別名**にする（衝突すると `getElementById` が見出しを返しグラフが空になる）。canvas は `ch` 接頭辞推奨。Chart.js は固定サイズ、または `responsive:true`＋高さ固定コンテナで描く

### Step 6: 志望動機の素材・選考フローを秘書へ共有

- H ブロックの「自分との接点」を `caw-es`（志望動機）・自己分析部へ渡す。
- 選考フロー・締切は秘書（`secretary/todos/`）の選考スケジュールへ反映を提案する（抜け漏れ防止）。業界横断のインターン・説明会・締切は `caw-events` で集められる。

## 重要な注意事項

- **発動したら毎回必ず `AskUserQuestion` で「調査レベル」と「出力形式」を尋ねる**（企業名・業界だけ言われても自動で既定にしない・絶対）。**成果物の既定は md**（`work/companies/<企業名>.md`）で、HTML は出力形式で html / 両方 を選んだときだけ作る
- **一次情報（公式採用ページ・IR）を優先**。非公式（年収・口コミ等）は複数ソースで裏取り・断定しない
- 古い情報に注意（募集要項・採用条件は年度で変わる）。**取得日と調査レベルを併記**する
- 企業の非公開情報・個人情報はローカルに留める
- 成果物は `work/companies/`（業界研究は `work/companies/_industry/`）に置く
