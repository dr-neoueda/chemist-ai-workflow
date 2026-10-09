---
name: caw-intake
description: >
  プロジェクト直下の単一の inbox/ に入れた「あらゆる過去資料」を、内容ごとに種類を自動判定して適切に処理・振り分けるスキル（研究・就活の両トラック対応）。
  自分の論文/申請書/スライド/CV → プロファイル・文体を抽出（work/profile/・work/manuscripts/_style/・work/self-analysis/ 等）。外部論文 → caw-register で登録。計算入出力 → caw-playbook へ。ES/履歴書 → 自己分析・文体を抽出。
  ユーザーは「どのフォルダに何を入れるか」を悩まなくてよい。
---

# caw-intake — 統合 inbox の自動仕分け・取り込み

過去資料を**1 つの `inbox/`** にまとめて入れておけば、発火時に**中身を見て種類を自動判定**し、適切な処理に振り分けるスキル。研究トラック（化学者向け）・就活トラックの両方に対応する。**ユーザーは「どのフォルダに何を入れるか」を悩まなくてよい**——迷ったら全部 `inbox/` に入れて「処理して」と言えばよい。

## いつ使うか

- `/caw-intake` を実行したとき
- 「inbox を処理して」「（資料を）取り込んで」「この資料を整理して」「過去の論文 / ES を取り込んで」と言われたとき
- オンボーディング直後で、過去に書いた資料・集めた資料が手元にあるとき

`office/` が無ければ `/caw` でセットアップを促す。

## はじめてモードを尊重する

このスキルを実行する前に `office/AGENTS.md`（Claude Code では `CLAUDE.md`）を読み、冒頭に `> 運用モード: はじめて` があれば、`caw` skill の「はじめてモードの挙動」を全応答に適用する：**平易な日本語**で話し、専門用語（voice プロファイル・STAR・汎関数 等）は初出で 1 行説明を添え、各ステップの最後に**「次はこれをしましょう」を 1 つ**だけ提示する。

## 統合 inbox（迷ったらここ）

- 置き場所：プロジェクト直下の **`inbox/`**（両トラック共通・可視フォルダ）。**種類を問わず何でも入れてよい**。
  - 研究：自分の論文・申請書・要旨・学会スライド/ポスター・CV/業績リスト・計算入出力（gjf/log・inp/out）・測定データ・外部論文 PDF
  - 就活：ES・志望動機・自己PR・ガクチカ・履歴書・職務経歴書・企業情報/求人票
- `inbox/` が無ければ作成する。**ユーザーに「どこに入れるか」を選ばせない**のが本スキルの目的。

## トラック判定

`office/AGENTS.md`（`CLAUDE.md`）の冒頭を読み、`> トラック:` が `就活` なら**就活トラック**、`研究` なら**研究トラック**。**行が無い（旧 office）場合は `work/companies/` があれば就活、`work/papers/`・`work/topics/` があれば研究と推定し、判別できなければ 1 問尋ねる**。判定後、下記の分類表を使う。

## ワークフロー

### Step 1: inbox を一覧し、各ファイルを内容で分類する

`inbox/` の各ファイルを**開いて中身を確認**し、下の分類表で種類を判定する。**拡張子だけで決めず内容も見る**（例: PDF は外部論文かも自分の論文かもしれない＝著者と内容で判断）。空なら「資料を `inbox/` に入れてから『処理して』と言ってください」と促して終了。最初に**何件・ざっとどんな資料か**を報告する。

#### 研究トラックの分類 → 処理

| 種類 | 判定の手がかり | 処理（行き先） |
|---|---|---|
| 外部の論文（他者の文献） | 著者が本人でない・DOI・書誌情報 | **caw-register で登録** → `work/papers/md/<著者-年>.md`（書誌付き要約） |
| 自分の論文・申請書・要旨 | 著者に本人・自分の研究内容 | §研究抽出 → `work/manuscripts/_style/voice-self.md`・`work/profile/{research-profile,key-findings,publications}.md` |
| 自分のスライド・ポスター | `.pptx`・発表資料 | §研究抽出 → `work/presentations/_style.md`（＋研究プロファイル） |
| CV・業績リスト | 経歴・publication list・受賞/グラント | §研究抽出 → `work/profile/cv.md`・`work/profile/publications.md` |
| 計算入出力 | `.gjf`/`.log`/`.com`/`.inp`/`.out` 等・計算ソフト書式 | **caw-playbook の `_past-data/` 取り込みへ委譲**（汎関数・基底・収束傾向を Playbook に seed） |
| 測定データ（NMR/XRD/IR/DSC の raw） | 装置出力形式 | `work/analyses/` に整理を提案 ＋ 手法傾向を `work/profile/methods.md` に記録 |
| 判定できない | — | ユーザーに「これは何の資料ですか？」と確認 |

#### 就活トラックの分類 → 処理

| 種類 | 判定の手がかり | 処理（行き先） |
|---|---|---|
| ES・志望動機・自己PR・ガクチカ | 設問・志望理由・「学生時代に…」 | §就活抽出 → `work/self-analysis/*`・`work/documents/voice-style.md`・`work/documents/past-answers.md` |
| 履歴書・職務経歴書 | 氏名/学歴/職歴の定型 | §就活抽出 → `work/self-analysis/profile.md`（＋文体） |
| 企業情報・求人票・IR | 企業名・募集要項・事業内容 | **caw-research の素材**として案内（`work/companies/<企業>.md` へ。未取得なら caw-research を促す） |
| 判定できない | — | ユーザーに確認 |

### Step 2: 振り分けて処理する

分類に従って処理する：

- **自分で抽出する分**（自分の論文/スライド/CV → 研究抽出、ES/履歴書 → 就活抽出）は、§研究抽出 / §就活抽出 の書き分け表に従ってその場で実行する。
- **専門スキルに渡す分**は、そのスキルの処理に回す：外部論文 → `caw-register`、計算入出力 → `caw-playbook`、企業情報 → `caw-research`。はじめてモードでは、ユーザーに「外部論文は登録、計算は Playbook 取り込みに回します」と平易に伝えてから実行/提案する。
- 1 つのファイルが複数に該当する場合（例: 自分の論文＝文体素材かつ業績）、**両方に反映**する。

### Step 3: 報告と次の一歩

- **何を・どう判定し・どこに処理したか**をファイルごとに一覧で報告する（種類／行き先／要点）。
- **処理が成功した原本は、種類ごとに `work/.../_source/` へ `mv`（移動）して `inbox/` を空にする**（`rm` は使わない＝可逆）。これで「inbox＝未処理の置き場」が常にクリーンになり、原本も後から探しやすい。移動先は下表。**判定できなかった／要確認のファイルは `inbox/` に残す**（移動しない）。完了時に「N 件処理 → 各 `_source/` へ移動、inbox は空（残 M 件は要確認）」と報告する。移動先フォルダ（`_source/` 等）が無ければ作成する。

**原本の移動先（種類別）**：

| 種類 | 原本の移動先 |
|---|---|
| 外部論文 PDF | `work/papers/pdf/`（`caw-register` が登録、要約は `work/papers/md/`） |
| 自分の ES・志望動機・自己PR・履歴書 | `work/documents/_source/` |
| 自分の論文・申請書・要旨 | `work/manuscripts/_source/` |
| 自分のスライド・ポスター | `work/presentations/_source/` |
| CV・業績リスト | `work/profile/_source/` |
| 計算入出力 | `work/<ソフト>/_past-data/`（`caw-playbook` が傾向を取り込み） |
| 測定 raw（NMR/XRD/IR/DSC 等） | `work/analyses/<topic>/_source/` |
| 判定不能・要確認 | `inbox/` に残す（移動しない） |
- 判定に迷った分はまとめて確認する。
- 次の一歩を 1 つ提示（研究例「これで caw-write が本人の文体・文脈で論文・申請書を書けます」／就活例「caw-es が本人の文体・実績で ES を書けます」）。

---

## §就活抽出（自分の応募書類 → 自己分析・文体）

分類で「自分の ES・履歴書」と判定したものから次を抽出し、**それぞれ適切なファイルに追記マージ**する（既存は上書きせず統合）。`work/self-analysis/` が無ければ作成する。

| 抽出するもの | 書き出し先 | 中身 |
|---|---|---|
| 文体プロファイル | `work/documents/voice-style.md` | トーン・一文の長さ・よく使う語彙と言い回し・論理展開・構成の癖・避ける表現 |
| 経験（STAR 化） | `work/self-analysis/experiences.md` | 1 経験 1 ブロックで「状況 / 課題 / 行動 / 結果」。数値・固有名詞も拾う |
| 強み・弱み・価値観 | `work/self-analysis/strengths.md` | 繰り返し現れる強み、弱み（短所）＋改善努力、価値観・モチベーションの源 |
| ガクチカ候補 | `work/self-analysis/gakuchika.md` | 「学生時代に力を入れたこと」の核になる題材 |
| 志望動機・就活の軸 | `work/self-analysis/motivation.md` | なぜこの業界/職種か・就活の軸・will/can/must・キャリアビジョン・原体験 |
| 基本プロフィール | `work/self-analysis/profile.md` | 氏名・連絡先・学歴・専攻/研究・資格・語学スコア・スキル・趣味/特技・課外活動 |
| 過去回答バンク | `work/documents/past-answers.md` | 過去に書いた「設問 × 完成回答」を設問タイプ別にカタログ化（流用・参考用） |

caw-es / caw-interview がこの出力を読んで本人の文体・実績で書く。

## §研究抽出（自分の論文・申請書・スライド・CV → 執筆スタイル・研究プロファイル）

分類で「自分の資料」と判定したものから次を抽出し、**それぞれ適切なファイルに追記マージ**する。`work/profile/` が無ければ作成する。

| 抽出するもの | 書き出し先 | 中身 |
|---|---|---|
| 執筆スタイル（文体） | `work/manuscripts/_style/voice-self.md` | 英語論文・日本語申請書の voice／hedging の癖／接続表現／定型表現／構成の癖 |
| 研究プロファイル | `work/profile/research-profile.md` | 研究テーマ・専門領域・主要な研究対象（化合物系/反応系/手法）＝キーワード辞書・novelty/意義の語り口 |
| 過去知見・主張 | `work/profile/key-findings.md` | 過去論文の主要な結論・主張リスト |
| 自分の業績 | `work/profile/publications.md` | publication 一覧＋各要点（タイトル・誌・年・一言要約） |
| よく引用する文献 | `work/profile/citations.md` | 頻出の文献・著者（self-citation 含む）・分野の重要文献 |
| 実験・解析手法の傾向 | `work/profile/methods.md` | よく使う測定手法・標準条件・試料調製/合成の定型・解析手順 |
| 作図スタイル | `work/figures/_style.md` | 配色・図のスタイル・キャプションの書き方 |
| スライド/発表スタイル | `work/presentations/_style.md` | 配色・フォント階層・レイアウト・発表ストーリーの型 |
| CV・メタ情報 | `work/profile/cv.md` | 所属・経歴・受賞・グラント・共著者ネットワーク・ORCID/researchmap 等 ID |
| 専門用語・略号辞書 | `work/profile/glossary.md` | よく使う略号・系の略称・装置略称（表記の一貫性確保） |

caw-write・caw-slides・caw-input がこの出力を読んで本人の文体・文脈で書く。文体は既存規約 `work/manuscripts/_style/voice-<name>.md` に乗せ、本人ぶんを `voice-self.md` とする。

---

## 他スキルとの関係

- **caw-intake は統合 inbox の「振り分け役」＋「自分プロファイルの抽出役」**。外部論文は `caw-register`、計算入出力は `caw-playbook`、企業情報は `caw-research` に渡し、**二重処理しない**。
- 整備した `work/profile/`・`work/self-analysis/`・各 `_style` を、研究は `caw-write`・`caw-slides`・`caw-input` が、就活は `caw-es`・`caw-interview` が読む。
- caw-es の「文体を学習して」は `work/documents/voice-style.md` だけを作る軽量版。まとめて取り込むなら caw-intake。

## 重要な注意事項

- **内容で判定する**。拡張子・ファイル名だけで決めず中身を確認する。曖昧なものは勝手に処理せずユーザーに確認する。
- **個人情報・未公開情報・他者の未公開データはローカルに留める**。`work/profile/cv.md`・`work/self-analysis/profile.md` 等を外部サービスへ送る前に必ず確認する。
- **既存ファイルは上書きしない**。追記マージし、重複・矛盾は統合またはユーザー確認で解消する。
- **事実を歪めない**。原資料の記述をそのまま素材化し、誇張・捏造を足さない。
- **抽出結果は専用ファイルに書き出す**。部署や `office/` の `AGENTS.md`（`CLAUDE.md`）は**書き換えない**。
- 原本は**種類別 `_source/` へ `mv`**（Step 3 の表。外部論文は `work/papers/pdf/`、計算は `_past-data/`）して `inbox/` を空にする（`rm` しない＝可逆・判定不能は残す）。抽出した成果物（`work/profile/`・`work/self-analysis/`・`work/manuscripts/_style/` 等）は `work/` 配下 に置く（`office/` 配下に書かない）。
