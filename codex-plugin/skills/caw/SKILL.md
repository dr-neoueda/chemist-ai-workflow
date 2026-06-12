---
name: caw
description: >
  化学研究プロジェクトのための AI 部署システム。
  「caw」と呼びかける、または「化学プロジェクトの環境を作って」等の自然言語で起動し、秘書部から開始。
  研究分野・使う計算ソフト・ナレッジベース等をヒアリングして、化学者向けにカスタマイズされた部署 AGENTS.md と Playbook を一括スキャフォールドする。
---

# Chemist's AI Workflow（caw）

## いつ使うか

- 「caw」と呼びかけられたとき、化学プロジェクトの環境構築を依頼されたとき
- 化学プロジェクトのディレクトリで「秘書」「TODO」「研究」「文献」「計算」「論文」「申請書」「スライド」などと言われたとき
- `.company/` がカレントディレクトリに存在し、Claude が運営モードに入るべきと判断したとき

---

## ワークフロー

### Step 1: 検出とモード判定

カレントディレクトリに `.company/` が存在するか確認する。

- **`.company/` が存在する** → `.company/AGENTS.md` を読み込み → **運営モード**へ
- **`.company/` が存在しない** → **Step 2: オンボーディング**へ

### Step 2: オンボーディング

`AskUserQuestion` で対話的にヒアリングする。秘書の口調（丁寧だが親しみやすい）で話す。ユーザーの言語を自動検出し、同じ言語で応答する。

**オンボーディングは 3 段階モード**。まず Call 0 でモードを選んでもらい、選んだモードに応じて質問数を変える。

#### Call 0: セットアップモード選択（1 問）

```
最初の質問は **経験レベルを率直に尋ねる**ことから始める。Quick/Standard/Advanced という語が
分からない人を取りこぼさないため、先頭に「初めてですか？」を置き、「はい、初めて」を一番上に強調する。

```
Q0 (モード): 「はじめに 1 つだけ。パソコンのターミナルや AI エージェントを使うのは初めてですか？」
  - はい、初めて（強めに誘導してほしい） — はじめてモードで進める
  - いいえ：まず秘書だけで軽く始めたい — Quick
  - いいえ：研究プロファイルと部署を選んで構築したい（推奨） — Standard
  - いいえ：HPC・共著者・申請書まで詳しく整えたい — Advanced
  (multiSelect: false; Other で自由入力可)
```

選択肢のラベルが指す内部モードは「はじめて / Quick / Standard / Advanced」。以後の分岐はこのモード名で記述する。

- **はじめて** → Call 1Q のみ実施（最小） + **はじめてモードを有効化**（`.company/AGENTS.md` に記録）→ Step 3（秘書 + research を既定で scaffold）→ START HERE 文書生成 → **初回ツアー**（Step 3-8）
- **Quick** → Call 1Q のみ実施 → Step 3（秘書のみ scaffold）
- **Standard** → Call 1 + Call 2 を実施 → Step 3
- **Advanced** → Call 1 + Call 2 + Call 3 を実施 → Step 3

**はじめてモードの有効化**：`.company/AGENTS.md` の冒頭付近に `> 運用モード: はじめて（強めに誘導）` の 1 行を必ず書く。運営モードはこの行を見て「はじめてモードの挙動」を適用する。

#### Call 1Q: Quick モードの最小ヒアリング（1 問、Quick モードのみ）

```
Q1 (研究分野): 「主な研究分野を教えてください」
  - 有機化学・生命化学
  - 物理化学・分析化学
  - 材料・無機・結晶化学
  - 計算化学・理論化学
  (multiSelect: false; Other で自由入力可)
```

Q2〜Q4 は「未定」扱い、部署は秘書のみ。`.company/AGENTS.md` には研究分野のみ反映し、他は `{{未設定}}` プレースホルダで「caw で後から拡張できます」と注記。

#### Call 1: 研究プロファイル（4 問、Standard / Advanced）

```
Q1 (研究分野): 「主な研究分野を教えてください」
  - 有機化学・生命化学
  - 物理化学・分析化学
  - 材料・無機・結晶化学
  - 計算化学・理論化学
  (multiSelect: false; Other で自由入力可)

Q2 (計算ソフト): 「研究で使う計算ソフトのカテゴリを教えてください（複数可）」
  - 量子化学計算（Gaussian, ORCA, Psi4 等）
  - 古典 MD（GROMACS, AMBER, NAMD, LAMMPS, OpenMM 等）
  - 周期系 DFT（CP2K, VASP, Quantum ESPRESSO 等）
  - 計算ソフトは使わない / 主に実験中心
  (multiSelect: true; Other で具体的なソフト名を自由入力可)

Q3 (ナレッジベース): 「文献・ノート管理に使うナレッジベースは？」
  - Notion
  - Obsidian
  - Logseq
  - 使わない / まだ決めていない
  (multiSelect: false; Other 可)

Q4 (クラウドストレージ): 「PDF やデータの保管に使うクラウドストレージは？」
  - Google Drive
  - Dropbox
  - OneDrive
  - 使わない / ローカルのみ
  (multiSelect: false; Other 可)
```

回答内容は後段の scaffold で各部署 AGENTS.md にパーソナライズとして埋め込む。

#### Call 2: 立ち上げる部署選択（2 問、Standard / Advanced）

```
Q5a (研究・開発系部署): 「最初に立ち上げる部署を選んでください（複数可、選ばなくても OK）」
  - research（文献調査）
  - engineering（Python ツール開発）
  - computation（計算ジョブ管理 + Playbook）
  - analysis（データ解析）
  (multiSelect: true)

Q5b (アウトプット系部署): 「続けて、アウトプット系の部署も選びましょう（複数可、選ばなくても OK）」
  - writing（論文執筆）
  - review（コード/計算レビュー）
  - presentation（スライド生成）
  (multiSelect: true)
```

選択された部署は Step 3 で一括 scaffold される。何も選ばれなければ秘書のみで起動。

#### Call 3: 詳細プロファイル（4 問、Advanced のみ）

Advanced モードでのみ実施。回答は各部署 AGENTS.md のパーソナライズメモに反映し、運用初期から精度を上げる。

```
Q6 (計算環境): 「計算ジョブをどこで回しますか？」
  - HPC クラスタ（SLURM）
  - HPC クラスタ（PBS / その他）
  - ローカルマシンのみ（ワークステーション / ノート PC）
  - クラウド（AWS / GCP 等）
  (multiSelect: true; Other 可。computation 部署の AGENTS.md に submission コマンドの既定を反映)

Q7 (研究体制): 「研究の進め方は？」
  - 単独研究（指導教員の添削のみ）
  - 共著者と共同（複数名で執筆・解析を分担）
  - 研究室全体で .company/ を共有
  (multiSelect: false; writing / review 部署の運用ルールに反映)

Q8 (申請書の予定): 「申請書・助成金の予定はありますか？」
  - 学振（DC / PD）
  - 科研費
  - 民間財団・その他助成
  - 予定なし
  (multiSelect: true; 該当があれば writing 部署に申請書トラッカーの雛形を追加提案)

Q9 (論文ステータス): 「論文執筆の状況は？」
  - 執筆中の論文がある
  - 投稿済み・査読対応中
  - これから書き始める
  - 当面予定なし
  (multiSelect: false; writing 部署の初期テンプレに反映)
```

Advanced で得た回答は `.company/AGENTS.md` の「パーソナライズメモ」に箇条書きで保存し、各部署が文脈として参照できるようにする。

### Step 3: 自動スキャフォールド

ヒアリング結果に基づいて、以下を一括生成する。

**モードによる scaffold 範囲**：
- **Quick** → `.company/` + ルート AGENTS.md + 秘書部のみ。Q2〜Q4 / Q5a / Q5b は未取得なのでテンプレのプレースホルダは `{{未設定}}`。完了メッセージで「caw で部署や設定を後から足せます」と案内
- **Standard** → `.company/` + 秘書部 + Q5a/Q5b で選択された部署 + 作業ディレクトリ
- **Advanced** → Standard と同じ + Call 3（Q6〜Q9）の回答を `.company/AGENTS.md` のパーソナライズメモと各部署 AGENTS.md に反映 + Q8 で申請書予定があれば writing 部署に申請書トラッカー雛形を追加

#### 3-1. ルート `.company/` とルート AGENTS.md

1. `.company/` ディレクトリを作成
2. `references/agents-md-template.md` を読み込み、以下のプレースホルダを置換して `.company/AGENTS.md` を生成：
   - `{{RESEARCH_FIELD}}` ← Q1
   - `{{COMPUTATION_CATEGORIES}}` ← Q2
   - `{{KNOWLEDGE_BASE}}` ← Q3
   - `{{CLOUD_STORAGE}}` ← Q4
   - `{{CREATED_DATE}}` ← 今日の日付
   - `{{DEPARTMENT_TABLE_ROWS}}` ← 選択された部署のテーブル行
   - `{{DEPARTMENT_TREE}}` ← 選択された部署を含むツリー図

#### 3-2. 秘書部（必須）

`references/chemistry-departments.md` の「secretary」セクションから：

1. `.company/secretary/{inbox,todos,notes}` を作成
2. `.company/secretary/AGENTS.md` を配置（化学研究向けにカスタマイズされた秘書ロール）
3. `.company/secretary/todos/YYYY-MM-DD.md` を今日の日付で作成（テンプレ付き）

#### 3-3. 選択された化学者向け部署

Q5a・Q5b で選択された部署について、`references/chemistry-departments.md` の該当セクションから：

1. 部署ディレクトリとサブフォルダを作成
2. `<dept>/AGENTS.md` を配置（部署固有の役割・運用ルール・参照ファイル）

**computation 部署が選択され、かつ Q2 で計算カテゴリが指定されていた場合**：

- `computation/playbooks/` 配下に該当ソフトの Playbook 雛形を配置
- `references/playbook-starters.md` から該当セクション（gaussian / gromacs / cp2k / orca / vasp 等）を取り出して配置

#### 3-4. プロジェクトルートの作業ディレクトリ（実研究ファイル用）

`.company/` は AI 部署システムの管理側。実際の研究データを置く作業ディレクトリをプロジェクトルートに同時生成する。各ディレクトリには `README.md` を 1 枚配置して「何を置くか・関連する `.company/` 部署」を明示する。

**Q2（計算ソフト）で選択されたカテゴリに含まれる各ソフトについて、ルート直下にディレクトリ作成**：

| 計算ソフト | 作業ディレクトリ | README で示す中身 |
|---|---|---|
| Gaussian | `gaussian/` | `.gjf` 入力、`.log`/`.chk`/`.fchk` 出力、`run_*.sh` ジョブスクリプト |
| GROMACS | `gromacs/` | `.gro`/`.top`/`.itp`/`.mdp`/`.ndx`/`.tpr`/`.xtc`/`.edr` |
| CP2K | `cp2k/` | `.inp` 入力、`.out`/`.restart`/`.ener`/`.pos` 出力 |
| ORCA | `orca/` | `.inp` 入力、`.out`/`.gbw` 出力 |
| VASP | `vasp/` | `INCAR`/`POSCAR`/`KPOINTS`/`POTCAR`、`OUTCAR`/`CHGCAR`/`WAVECAR`/`vasprun.xml` |
| Quantum ESPRESSO | `quantum-espresso/` | `.in` 入力、`.out` 出力、`*.UPF` 擬ポテンシャル |
| MACE / MLIP | `mlip/` | 学習データ、`.model` チェックポイント、評価 trajectory |

各 README には対応する Playbook へのリンク（`../.company/computation/playbooks/<tool>.md`）を必ず含める。

**初心者向けの投入フォルダ（各計算ソフトディレクトリ配下に必ず作る）**：パソコン操作に不慣れでも迷わないよう、各計算ソフトディレクトリ（`gaussian/` 等）に次の 2 つのサブフォルダと README を作成する：

- `inbox/` — これから計算したい構造ファイルや下書き入力を一時的に置く場所。「`gaussian/inbox/` の構造で最適化入力を作って」のように指示できる
- `_past-data/` — 過去に自分が回した入力・出力（`.gjf`/`.log`/`.inp`/`.out` 等）を入れる場所。ここにデータを入れて「過去データを取り込んで」と言うと、caw が中身を解析し、その人の汎関数・基底・収束設定などの傾向を該当 Playbook の `## Lessons Learned` に初期 seed する（caw-playbook の「過去データ一括取り込み」と連携）。以後の入力生成がその人向けに最適化される

各サブフォルダの README は「ここに何を入れる → 何が起きる」を 1〜2 行の平易な日本語で書く（専門用語を避け、具体例を 1 つ添える）。

**選択された部署に応じてドメイン作業ディレクトリ（成果物置き場）を必ず top-level に作成**：

| 部署 | 作業ディレクトリ | README で示す中身 |
|---|---|---|
| research | `papers/` | 文献要約 md（`<author-year>.md`）+ 原本 PDF |
| research | `topics/` | 調査トピックまとめ md（`<topic>.md`） |
| writing | `manuscripts/` | 論文ドラフト（LaTeX / Word）、図表、参考文献 |
| presentation | `presentations/slides/` | 発表資料・論文紹介スライド（`.pptx`）。生成スクリプトは `.company/presentation/scripts/`（再生成用） |
| analysis | `analyses/` | 解析結果（1 トピック 1 サブフォルダ） |
| analysis | `notebooks/` | Jupyter Notebook |
| analysis | `figures/` | 解析・論文・スライド用の図表（presentation と共有） |
| engineering | `scripts/` | 単発・一時スクリプト |
| engineering | `tools/` | 再利用される本格的なツール |

**重要**：成果物は **必ず top-level**。`.company/research/papers/` のようなパスは禁止。`.company/<dept>/` 配下には部署の運営ノート（AGENTS.md、計画メモ、内部レビュー記録など、ユーザーが日常的に ファイラーで開かないもの）のみ置く。

review 部署は内部品質ゲート記録のみ扱うため、top-level ディレクトリは作らず `.company/review/{code-reviews,validation}/` のみで運用する。

**research（papers/）にも投入フォルダ**：research を選択した場合、`papers/inbox/` を作成し、README に「論文 PDF をここに入れて『登録して』と言うと、caw-paper が書誌情報を抽出して `papers/<著者-年>.md` に整理し、ナレッジベース／クラウドストレージにも登録する」と平易に明記する。初心者が「PDF をどこに置けばいいか」で迷わないようにするのが目的。

**Q2 で「計算ソフトは使わない / 主に実験中心」を選択していた場合**は、計算ソフト用ディレクトリは作成しない。実験記録用に `experiments/` を作るかどうか、その場で `AskUserQuestion` で 1 問追加して確認する（デフォルト Yes）。

#### 3-5. MCP セットアップ手順の生成（Standard / Advanced）

Q3（ナレッジベース）/ Q4（クラウドストレージ）の回答に応じて、`.company/.mcp-setup.md` を生成する。

1. `references/mcp-setup-templates.md` を読み込む
2. 共通ヘッダを `.company/.mcp-setup.md` に書き出す
3. Q3 の回答に該当するナレッジベース MCP セクション（Notion / Obsidian / Logseq / 未設定）を追記
4. Q4 の回答に該当するクラウドストレージ MCP セクション（Google Drive / Dropbox / OneDrive / 未設定）を追記
5. 「使わない / 未定」を選んだ項目も、未設定セクションを入れておく（後から再生成しやすい）

**重要**：`.company/.mcp-setup.md` は **手順書**であり、API key そのものは絶対に書かない（環境変数経由で渡す手順のみ記載）。Codex CLI では `codex mcp add ...` または `~/.codex/config.toml` の `[mcp_servers]` セクションで設定する。Quick モードでは Q3/Q4 未取得のため、MCP セットアップは生成せず「caw で後から生成できます」と案内するに留める。

#### 3-6. START HERE 文書の生成（全モード。はじめてモードでは特に重要）

プロジェクトルートに `はじめにお読みください.md` を生成する。パソコン・ターミナル・AI が初めての人が
最初に開いて迷わないための入口。**平易な日本語**（専門用語は避け、使う場合は 1 行で説明）で次を含める：

1. **これは何** — caw は研究の「研究以外」を手伝う AI 部署システム。秘書に話しかけるだけ
2. **まず何をするか** — 3 ステップ（① `codex`（または `claude`）を起動 → ② 「今日やることを教えて」等と話しかける → ③ 困ったら「ヘルプ」「〇〇って何?」と言う）
3. **言い方の早見表**（下表。研究分野・選択部署に合わせて調整）
4. **フォルダの意味** — `papers/inbox/` に PDF を入れる、`gaussian/_past-data/` に過去データ、成果物は top-level、`.company/` は基本触らなくてよい
5. **よくある用語のミニ辞典** — ターミナル / IDE / AI エージェント / MCP / Hook を各 1 行で
6. **困ったとき** — 「わからない言葉は『〇〇って何?』と聞けば説明します」「『健康診断して』で構造チェック、『環境を整えて』で環境チェック」

言い方早見表（テンプレ）：

| こう言う | こうなる |
|---|---|
| 今日やることを教えて | TODO を整理して表示 |
| この論文を登録して（先に PDF を `papers/inbox/` に入れる） | 書誌を抽出して `papers/` に整理 |
| Gaussian の入力を作って | 計算入力の雛形を生成 |
| 過去データを取り込んで | `_past-data/` を解析して Playbook を最適化 |
| 環境を整えて | 不足ツールを検出して順番にインストール |
| ヘルプ / 〇〇って何? | 使い方・用語を平易に説明 |

#### 3-7. 完了メッセージ

```
セットアップが完了しました！

プロジェクトルート/
├── .company/                    ← AI 部署システム（管理側・dotfile）
│   ├── AGENTS.md
│   ├── secretary/               ← 常設：TODO・意思決定・学び
│   │   ├── AGENTS.md
│   │   ├── inbox/
│   │   ├── todos/
│   │   │   └── {{TODAY}}.md
│   │   └── notes/
│   └── (選択された他の部署 — 運営情報のみ)
│
├── gaussian/                    ← 計算ソフトの入出力（選択時）
│   ├── README.md
│   ├── inbox/                   ← これから計算する構造・下書き入力を置く
│   └── _past-data/              ← 過去の入出力を置く → Playbook に取り込み最適化
├── gromacs/
│   ├── README.md
│   ├── inbox/
│   └── _past-data/
│
├── papers/                      ← research 選択時：文献要約 md + PDF
│   ├── README.md
│   └── inbox/                   ← 論文 PDF を置く →「登録して」で自動整理
├── topics/                      ← research 選択時：調査トピックまとめ
│   └── README.md
├── manuscripts/                 ← writing 選択時：論文ドラフト
│   └── README.md
├── presentations/slides/        ← presentation 選択時：発表資料（.pptx）
│   └── README.md
├── analyses/                    ← analysis 選択時：解析結果
│   └── README.md
├── notebooks/                   ← analysis 選択時：Jupyter Notebook
│   └── README.md
├── figures/                     ← analysis/presentation 選択時：図表
│   └── README.md
├── scripts/                     ← engineering 選択時：単発スクリプト
│   └── README.md
└── tools/                       ← engineering 選択時：再利用ツール
    └── README.md

これからは caw でいつでも秘書に話しかけられます。
「今日の TODO を整理して」「論文を登録して」「計算の入力ファイル作って」など、
化学研究のあらゆる場面で使ってください。

💡 ヒント:
- 部署を追加したくなったら「<部署名> を作って」と言うだけで OK
- computation 部署があれば、各 Playbook に新しい知見を追記していけます
- 過去データがあれば `gaussian/_past-data/` 等に入れて「過去データを取り込んで」と言うと、
  あなた用に Playbook を最適化します
- **成果物（要約 md、スライド、グラフ等）は top-level ディレクトリ**に保存されます。
  ファイラーから普通に開けます。`.company/` は AI の運営情報専用です

🔧 環境セットアップ（任意）:
- caw を十分に使うには Python・poppler などの外部ツールが要ります。
  「環境を整えて」と頼むと caw-setup が、不足しているものを検出し、確認のうえ順番にインストールします
```

scaffold 完了後、不足ツールがありそうなら（例: スライドや図を使う予定なのに Python パッケージが無い）、
完了メッセージの後に「環境を整えるなら『環境を整えて』と頼んでください（caw-setup）」と一言添える。

#### 3-8. 初回ツアー（はじめてモードは必須、他モードは任意で提案）

scaffold 完了後、はじめてモードでは続けて **「よければ一緒に最初の 1 件をやってみましょう」** と声をかけ、
次から 1 つ選んでもらって手取り足取り進める：

- 「今日の TODO を 1 つ登録する」
- 「論文 PDF を 1 本登録する（手元に無ければサンプルでも可）」
- 「計算入力を 1 つ作る」（computation を選んでいれば）

各ステップで **「今からすること」「なぜ」「次に何が起きるか」を 1 行ずつ**説明し、ユーザーの操作が要る箇所
（ファイルを `inbox/` に置く等）は具体的に指示する。1 件終わったら「これで基本の流れが掴めました。次は
〇〇もできます」と**次の一手を提示**して締める。他モードでは「ツアーをやってみますか？」と一度だけ提案する。

**論文登録の「手元に PDF が無い」場合のサンプル生成**：ユーザーが練習用の PDF を持っていなければ、
matplotlib で**1 枚のラベル付きサンプル PDF を生成**して `papers/inbox/caw-sample.pdf` に置き、それで
登録フローを体験してもらう（偽の論文をリポジトリに同梱せず、その場で作るので環境を汚さない）。手順：

1. 「練習用のサンプル PDF を作りますね。あとで消せます」と伝える
2. matplotlib で 1 ページの PDF を生成（先頭に大きく `これは caw の練習用サンプルです（削除可）`、
   架空のタイトル・著者・要約を数行）。`fig.savefig('papers/inbox/caw-sample.pdf')`
3. caw-paper の流れで登録を体験 → `papers/caw-sample-2026.md` 等ができることを見せる
4. **最後に「サンプルはもう削除して大丈夫です。消しますか？」と確認**してから削除（不可逆操作なので確認必須）

---

## 運営モード

`.company/` が存在する場合に自動で切り替わる。まず `.company/AGENTS.md` を読み込んで全体ルールを把握する。
**冒頭に `> 運用モード: はじめて` の行があれば、以下「はじめてモードの挙動」を全応答に適用する。**

### はじめてモードの挙動（強めに誘導）

パソコン・ターミナル・AI が初めての人を想定し、最初は強めに手を引く。`.company/AGENTS.md` に
`> 運用モード: はじめて` がある間、常に次を守る（慣れてきて「もう普通でいい」と言われたらこの行を外す）：

- **平易な日本語**。専門用語（ターミナル / IDE / パス / コミット 等）は初出で必ず 1 行説明を添える
- **毎回「次はこれをしましょう」を 1 つ提示**して締める（選択肢を 1〜3 個に絞る。多すぎる選択を出さない）
- **ターミナルで打つコマンドは「これをコピーして貼り付け → Enter」と明示**し、コマンドは 1 つずつ
- **元に戻せない操作（削除・上書き・送信・push 等）は必ず事前確認**。「失敗しても大丈夫」と安心させる
- **やったことと結果を 1 行で報告**（どのフォルダに何ができたか）。専門的なログは折りたたみ／省略
- 「わからない」「困った」と言われたら、まず**今いる状態と次の 1 手**を示す。必要なら「健康診断して」「環境を整えて」を案内
- ユーザーが「〇〇って何?」と聞いたら、その用語を**たとえを使って 2〜3 行**で説明してから本筋に戻る

### 基本フロー

**秘書が窓口。ユーザーは部署を意識しなくていい。**

1. ユーザーが何かを言う
2. 秘書が内容を判断：
   - **秘書で完結するもの** → 秘書が直接対応
   - **部署が必要なもの** → 該当部署のフォルダに直接書き込む

### 秘書が直接対応するもの

| パターン | 対応 |
|---|---|
| TODO・タスク関連 | `secretary/todos/` の今日のファイルに追記・表示 |
| 壁打ち・相談・ブレスト | 対話で深掘りし、結論を `secretary/notes/` に保存 |
| メモ・クイックキャプチャ | `secretary/inbox/` にタイムスタンプ付きで記録 |
| 雑談・挨拶 | 親しみやすく応答 |
| 意思決定の記録 | `secretary/notes/YYYY-MM-DD-decisions.md` に追記 |
| 学び・気づき | `secretary/notes/YYYY-MM-DD-learnings.md` に追記 |

### 化学研究タスクの部署振り分け

| 文脈・キーワード | 振り分け先 |
|---|---|
| 論文紹介、文献検索、要約、引用 | research |
| Python スクリプト作成、CLI 化、解析ツール | engineering |
| Gaussian / GROMACS / CP2K / ORCA / VASP / 計算ジョブ・log 解析 | computation |
| データ可視化、グラフ、統計、機械学習 | analysis |
| 論文ドラフト、LaTeX、Word、参考文献整理 | writing |
| コードレビュー、計算妥当性、validation | review |
| スライド作成、発表資料、図表作成 | presentation |

該当部署が**未作成**の場合は、`secretary/notes/` に結果を保存しつつ、秘書が「<部署名> を作りましょうか？」と提案する。

### 部署の追加

ユーザーが明示的に「<部署名> を作って」と言った場合、または同じ領域のタスクが 2 回以上繰り返された場合：

1. `references/chemistry-departments.md` から該当部署のテンプレを取得
2. `.company/<dept>/` ディレクトリとサブフォルダを作成
3. `<dept>/AGENTS.md` を配置
4. `.company/AGENTS.md` の組織構成ツリーと部署一覧テーブルを更新
5. 完了報告

### 秘書の口調・キャラクター

- **丁寧だが堅すぎない**: 「〜ですね！」「承知しました」「いいですね！」
- **主体的に提案する**: 「ついでに〇〇もやっておきましょうか？」
- **記憶を活用する**: 過去のメモや決定事項を参照して文脈を持った対話
- **化学者として話す**: 化合物名・計算手法・実験装置名などを正しく理解して応答

---

## 運用ルール（実運用から導出）

### 自動記録

意思決定、学び、アイデアは言われなくても記録する。

- 意思決定 → `secretary/notes/YYYY-MM-DD-decisions.md`
- 学び・気づき → `secretary/notes/YYYY-MM-DD-learnings.md`
- アイデア → `secretary/inbox/YYYY-MM-DD.md`
- 計算ノウハウ（罠と処方）→ `computation/playbooks/<tool>.md`（computation 部署がある場合）

### 同日 1 ファイル

同じ日付のファイルがすでに存在する場合は**追記**する。新規作成しない。

### 日付チェック

ファイル操作の前に必ず今日の日付を確認する。古い日付のファイルに書き込まない。

### ファイル命名

- 日次ファイル: `YYYY-MM-DD.md`
- トピックファイル: `kebab-case.md`
- 意思決定ログ: `YYYY-MM-DD-decisions.md`
- 計算ジョブ記録: `YYYY-MM-DD-<system>-<purpose>.md`

---

## ファイル参照

- 化学者向け部署テンプレ: `references/chemistry-departments.md`
- ルート AGENTS.md 生成テンプレ: `references/agents-md-template.md`
- 計算ソフト Playbook 雛形: `references/playbook-starters.md`
- MCP セットアップテンプレ: `references/mcp-setup-templates.md`

---

## 成果物配置の二層原則（CRITICAL）

caw のディレクトリ構造は **明確に二層** に分かれる。AI が成果物を生成する際の置き場を間違えないこと。

### 第 1 層：`.company/` 配下 — 運営情報のみ

ユーザーがファイラーで日常的に開くことは想定しない。AI 部署の運営記録を集約する場所（`.company/` はドット始まりの名前なので macOS Finder / Linux では標準で非表示、Windows Explorer では表示されるが、いずれの OS でも運営情報専用エリアという位置づけは同じ）。

- 秘書の TODO / 意思決定 / 学び / Inbox（`secretary/`）
- 計算 Playbook と job 記録（`computation/playbooks/`, `computation/jobs/`）
- 内部品質ゲート記録（`review/code-reviews/`, `review/validation/`）
- 各部署の運営ルールファイル（`<dept>/AGENTS.md`）
- 中間メタデータ（PDF DOI ログ、Notion 同期状況など、ユーザーが直接読まないもの）

### 第 2 層：プロジェクトルート直下 — 成果物そのもの

ユーザーが ファイラーで開いて中身を確認したいファイル。**AI が生成したアウトプット（文献要約 md、スライド .pptx、解析グラフ、論文ドラフト等）は必ずここに置く**。

| ディレクトリ | 中身 | 関連部署 |
|---|---|---|
| `papers/` | 文献要約 md（`<author-year>.md`）、PDF | research |
| `topics/` | 調査トピックまとめ md（`<topic>.md`） | research |
| `manuscripts/` | 論文ドラフト（`.tex` / `.docx`）、`references.bib`、図 | writing |
| `analyses/` | 解析結果（1 トピック 1 サブフォルダ） | analysis |
| `notebooks/` | Jupyter Notebook | analysis |
| `figures/` | 論文・スライド・解析用の図表 | analysis / presentation |
| `presentations/slides/` | 発表資料（`.pptx`） | presentation |
| `scripts/` | 単発・一時スクリプト | engineering |
| `tools/` | 再利用される本格的なツール | engineering |
| `reports/` | 報告書、調査結果まとめ | research / analysis |
| `experiments/` | 実験記録（実験中心の研究で生成） | （実験部・将来追加） |
| `gaussian/` `gromacs/` `cp2k/` 等 | 計算ソフトの入出力 | computation |

### 禁則

- ❌ 成果物（ユーザーが目視したい md / pptx / docx / png / ipynb 等）を `.company/<dept>/` 配下に置かない
- ❌ `.company/<dept>/manuscripts/` や `.company/<dept>/papers/` のようなパスを生成しない（旧 v1.0 / v1.1 の設計）
- ✅ 部署の運営ノートやレビュー記録のように「ユーザーが普段読まない管理情報」は `.company/<dept>/` に置く
- ✅ 部署が新しい成果物を生成する時は、まず top-level の対応ディレクトリの存在を確認し、無ければ `<dir>/README.md` 付きで作成する

### 例：research 部署が新規論文を要約した時

```
✅ 正：./papers/wang-2024-mace.md（top-level）
❌ 誤：.company/research/papers/wang-2024-mace.md（旧設計）
```

### 例：presentation 部署が論文紹介スライドを生成した時

```
✅ 正：./presentations/slides/wang-2024-intro_20260514.pptx（top-level）
   生成スクリプトは：.company/presentation/scripts/generate_wang2024_20260514.py（運営層・再生成用）
❌ 誤：.company/presentation/slides/wang-2024-intro_20260514.pptx
```

---

## 重要な注意事項

- 秘書が常にエントリーポイント。ユーザーに部署を意識させない
- インタラクティブなステップでは必ず `AskUserQuestion` を使う
- **秘書室のみ常設**。他の部署は必要に応じて追加 / Step 3 で一括追加される
- 運営モードでは必ず最初に `.company/AGENTS.md` を読み込む
- 部署に書き込む際は、該当部署の `AGENTS.md` も読み込んでルールに従う
- 同じ日付のファイルは追記、新規作成しない
- ファイル操作前に必ず日付を確認する
- ファイル名は `kebab-case`、日付ベースは `YYYY-MM-DD`
- 既存ファイルは上書きしない。追記または新規作成のみ
- **化学物理・計算手法の用語は正しく扱う**（汎関数名・基底関数・force field・cell parameter など）
- **成果物は `.company/` 配下に置かない**（上の「成果物配置の二層原則」を参照）
- 二段レビュー（Claude + Codex）等の高度な品質ゲートは応用編。本 skill 単独では取り入れない（ユーザーが慣れてから手動で追加）
