# Changelog

本ファイルは [Keep a Changelog](https://keepachangelog.com/) と [Semantic Versioning](https://semver.org/) に準拠。

## [1.22.1 / Codex 1.21.1 / Gemini 1.1.1] - 2026-06-17

### Changed — caw-report に提出先 Google フォーム URL を組み込み

caw-report の Step 5 を「**提出先フォームの URL をチャットに表示**」に更新。テストユーザーが `caw-report` を実行すると、生成完了後にチャットへ提出フォームの URL を表示し、「レポートの中身を貼り付けて提出してください（匿名なのでそのまま提出可）」と案内する。caw が自動送信することはなく、提出はユーザーの操作で行う。

- `caw-report/SKILL.md`（plugin + codex）・`gemini-plugin`（GEMINI.md ＋ `commands/caw-report.toml`）に提出フォーム URL を追記。
- 配布 HTML（セミナー資料・repo 外）の「報」セクションにも提出フォームのボタンリンクを追加。

### Note

- 版: plugin 1.22.0 → **1.22.1** / codex 1.21.0 → **1.21.1** / gemini 1.1.0 → **1.1.1** / copilot 1.13.0 据え置き / marketplace 同期

## [1.22.0 / Codex 1.21.0 / copilot 1.13.0 / Gemini 1.1.0] - 2026-06-17

### Added — caw-report（開発者向け匿名動作レポート）

テストユーザーの caw 環境を点検し、**開発者がレビューするための匿名レポート**を生成する新スキル。テストユーザーが利用 → 生成された `caw-report/<日付>.md` を開発者へ共有 → caw 改善に活かす、という流れ。抽出シグナル（すべて匿名）：**①環境/互換性**（version・CLI・OS・ツール有無・MCP 有無/サーバ数・利用期間/最終活動）**②オンボーディング完遂度**（scaffold 完走・不足数・モード）**③構造の健全性と逸脱**（合否・二層原則違反の種別別件数・規約外フォルダ数・不可視フォルダ検知・設定ファイル肥大）**④利用状況と完成度**（各 dir のファイル数・空/極小数・放置数・HTML/voice/profile/past-answers の有無）**⑤エラー**（スキル別×種別の件数・inbox 未処理・hook 失敗）**⑥運用エンゲージメント**（notes/todos/decisions 件数）**⑦間接検証シグナル**。

- **完全匿名（PII リスクゼロ）**：個人情報・企業名・研究テーマ・ファイル名・本文・絶対パス・研究分野/志望業界の具体名を**一切含めない**。出せるのは標準フォルダ名・件数・合否・エラー種別・version/CLI/トラック/モードのみ。生成後にスキルが**自己点検**して PII が無いことを確認してから保存。caw が自動で外部送信することはしない（共有はユーザーの手で）。
- `caw-report/SKILL.md`（plugin + codex）、`gemini-plugin`（GEMINI.md にスキル節 ＋ `commands/caw-report.toml`）。copilot は PoC のため未収載。
- `engine-validation-map.md`（3 系統 byte 一致）：主観の `feedback/` に対する**客観・匿名の構造シグナル**として caw-report を §2 に追記（§1 のエンジンパス稼働を件数・合否で裏取り）。
- caw-doctor が「ユーザー自身の修復」用なのに対し、caw-report は「開発者へ匿名フィードバック」用。

### Note — caw-report

- 版: plugin 1.21.0 → **1.22.0** / codex 1.20.0 → **1.21.0** / copilot 1.12.0 → **1.13.0** / gemini 1.0.0 → **1.1.0** / marketplace 同期

## [Gemini 1.0.0 追加 / plugin 1.21.0 / Codex 1.20.0 / copilot 1.12.0] - 2026-06-17

### Added — Gemini CLI 版 caw（`gemini-plugin/`、4 つ目の配布ターゲット）

caw を **Gemini CLI の extension** として配布開始。これで caw は **Claude Code / Codex CLI / GitHub Copilot CLI（PoC）/ Gemini CLI** の 4 CLI に対応。

- `gemini-plugin/`：`gemini-extension.json`（manifest, version 1.0.0）＋ `GEMINI.md`（常時ロードの caw 本体）＋ `commands/*.toml`（`/caw` ほか 12 個の明示コマンド）＋ `README.md`。
- Gemini CLI は「説明文で skill を自動発火」する仕組みを持たないため、caw 本体（秘書・両トラックのオンボーディング・ディスパッチ・統合 inbox 自動仕分け・各スキル手順）を**単一の `GEMINI.md`（常時ロード）に集約**。プロジェクト設定は `office/GEMINI.md`。メソッド・二層原則・統合 inbox は 4 CLI 共通。
- 導入：`gemini extensions install https://github.com/dr-neoueda/chemist-ai-workflow`。Gemini CLI には hooks（bash）が無いため Windows でも Git Bash 不要。
- `scripts/check-consistency.sh`：版表示・個人化リーク走査・隠しフォルダ走査に `gemini-plugin/` を追加。
- web `gemini-cli/index.md` を「Phase 2 執筆予定」→「対応（導入・できること）」に更新。

### Note — Gemini 追加

- 版: **gemini-plugin 1.0.0（新規）** / plugin 1.21.0・codex 1.20.0・copilot 1.12.0 は据え置き（無変更）。

## [1.21.0 / Codex 1.20.0 / copilot 1.12.0] - 2026-06-17

### Added — caw-intake を「統合 inbox の自動仕分け」＋デュアルトラック化

`caw-intake` を、**1 つの `inbox/` に何でも入れれば中身を見て自動で振り分ける**統合プロセッサに刷新。ユーザーは「どの資料をどのフォルダに入れるか」を悩まなくてよい。研究・就活の両トラックに対応（caw-doctor 同様に `> トラック: 就活` の有無で分岐）。

- **統合 inbox**：プロジェクト直下に単一の `inbox/`（両トラック共通）。研究は論文/申請書/スライド/CV/計算入出力/測定データ/外部論文、就活は ES/履歴書/企業情報など**種類を問わず投入**。旧 `documents/inbox/`・`profile/inbox/` は廃止し `inbox/` に一本化。
- **内容判定 → 振り分け**：`caw-intake/SKILL.md`（plugin + codex）を「分類表に基づく振り分け」中心に再構築。中身（著者・書式・内容）で種類を判定し処理を分岐——
  - 自分の論文/スライド/CV → 執筆スタイル(`manuscripts/_style/voice-self.md`)・研究プロファイル/知見/業績/引用/手法(`profile/*`)・図表/発表スタイル(`figures/_style.md`・`presentations/_style.md`)・CV(`profile/cv.md`)・用語辞書(`profile/glossary.md`)を抽出
  - 外部論文 → `caw-paper` で登録、計算入出力 → `caw-playbook` の `_past-data/` 取り込み、企業情報 → `caw-research` の素材、に委譲（二重処理しない）
  - ES/履歴書 → `self-analysis/*`・`documents/voice-style.md`・`documents/past-answers.md` を抽出
  - 判定不能はユーザーに確認
- 新トップレベル `profile/`（就活の `self-analysis/` に対応する研究者の自己プロファイル層）。`caw/SKILL.md` scaffold・`caw-doctor`・`engine-validation-map.md` を統合 inbox 前提に更新（検証マップは「統合 inbox の内容判定→振り分け」を 4 つ目のエンジンパターンに）。
- copilot は PoC のため caw-intake スキル本体は未収載（reference の記述のみ追従）。

### Note — caw-intake 統合 inbox

- 版: plugin 1.20.0 → **1.21.0** / codex 1.19.0 → **1.20.0** / copilot 1.11.0 → **1.12.0** / marketplace 同期

## [1.20.0 / Codex 1.19.0 / copilot 1.11.0] - 2026-06-16

### Added — caw-intake（過去書類の取り込み・自己分析ジェネレータ）

過去に書いた ES・志望動機・自己PR・履歴書（`documents/inbox/`）を取り込み、**文体・経験(STAR)・強み/弱み・ガクチカ・志望動機/就活の軸・基本プロフィール・過去回答バンク**（7 種）を抽出して、それぞれ適切なファイルに書き分けて配置する就活モードの新スキル。caw-es / caw-interview がこの出力を参照して「本人の文体・実績」で書けるようになる。

- 新スキル `caw-intake/SKILL.md`（plugin + codex。copilot は PoC 対象外）。発火＝「過去の ES を取り込んで」「inbox の文章から自己分析して」。
- 抽出 → 配置（7 種）：文体 → `documents/voice-style.md`、経験(STAR) → `self-analysis/experiences.md`、強み・弱み・価値観 → `self-analysis/strengths.md`、ガクチカ候補 → `self-analysis/gakuchika.md`、志望動機・就活の軸 → `self-analysis/motivation.md`（新規）、基本プロフィール → `self-analysis/profile.md`（新規）、過去回答バンク（設問×回答） → `documents/past-answers.md`（新規）。既存ファイルは上書きせず追記マージ、個人情報はローカル保持。caw-es / caw-interview は motivation.md・past-answers.md も参照する。
- 配線（3 系統 byte 一致）：`job-hunting-departments.md`（§D2 最初の一声・§E ディスパッチ・§B-4 inbox 説明・analysis 部署テンプレ）、`engine-validation-map.md`（4 つ目のエンジンパターン「過去データ取り込み → 個人最適化 seed」を新設、caw-playbook の `_past-data/` 取り込みと対応づけ）。
- `caw-es` に caw-intake への相互参照を追記（「文体を学習して」は文体のみの軽量版、まとめて抽出は caw-intake）。

### Note — caw-intake

- 版: plugin 1.19.0 → **1.20.0** / codex 1.18.0 → **1.19.0** / copilot 1.10.0 → **1.11.0** / marketplace 同期

## [1.19.0 / Codex 1.18.0 / copilot 1.10.0] - 2026-06-16

### Changed — 初期環境構築でモードに応じた全部署を作成＋化学者モードの質問を再設計

初期 scaffold が「ユーザーが選んだ部署だけ」を作っていたのを、**モードに応じた全部署を常に作成**に変更。これに合わせて化学者モードのオンボーディング質問を作り直した。

- **化学者モード（全 8 部署を常に作成）**：`caw/SKILL.md`（3 系統）。
  - **部署選択質問（Call 2 / Q5a・Q5b）を廃止**。「どの部署を作るか」をユーザーに尋ねない。
  - **Quick（秘書のみ）モードを廃止**。経験レベルは **はじめて / 通常 / 詳しく** の 3 段階に整理（Standard→通常、Advanced→詳しく）。どのモードでも全 8 部署（secretary / research / engineering / computation / analysis / writing / review / presentation）を作成し、モードで変わるのは personalization 質問の深さだけ。
  - 旧 Call 3（詳細プロファイル Q6〜Q9）は Call 2 に繰り上げ。scaffold 範囲・3-3・プレースホルダ説明・MCP 生成条件（Quick→はじめて）を全部署前提に更新。
- **就活モード（全 4 部署を常に作成）**：`job-hunting-departments.md`（3 系統 byte 一致）§B-3。QJ3a の悩みは「どの部署を作るか」ではなく **START HERE の最初の一歩の優先度**に使うよう役割変更（部署は秘書＋ research/analysis/writing/presentation を常に作成）。
- 付随更新：`claude-md-template.md` / `agents-md-template.md`（DEPARTMENT プレースホルダの説明を「全部署」に）、`caw-doctor/SKILL.md`（全部署前提のチェック文言）、`plugin/README.md`・`plugin/TESTING.md`。
- copilot marketplace の `metadata.version` が 1.8.0 で取り残されていたのを 1.10.0 に同期。

### Fixed — Codex CLI のインストールが失敗する問題（authentication）＋ 導入手順の是正

- **`.agents/plugins/marketplace.json` の `"authentication": "NONE"` → `"ON_INSTALL"`**。これが入っていると `codex plugin marketplace add dr-neoueda/chemist-ai-workflow`（marketplace 登録）が（特に Windows で）失敗する。`web/.../codex-cli/skills.md` のサンプルも同様に修正。
- **Codex の導入手順を実態に合わせて 2 ステップ化**：`codex plugin marketplace add ...`（marketplace 登録）→ `codex plugin add caw@chemist-ai-workflow`（プラグイン本体追加）。web 各所の「個別 install コマンドはありません」という誤記を全面修正（`plugin.md` / `codex-cli/{index,setup,skills}.md`）。Desktop 配布 HTML（repo 外）も同時修正。
- **アンインストール手順も是正**（`codex-cli/uninstall.md`）：「caw だけの個別アンインストールは無い」は誤り。実際は 2 レベル—`codex plugin remove caw@chemist-ai-workflow`（プラグイン本体のみ削除、marketplace 登録は残る）／`codex plugin marketplace remove chemist-ai-workflow`（marketplace ごと削除）。再現フロー・モード名（はじめて/通常/詳しく）も更新。

### Note

- 版: plugin 1.18.0 → **1.19.0** / codex 1.17.0 → **1.18.0** / copilot 1.9.0 → **1.10.0** / marketplace 同期

## [1.18.0 / Codex 1.17.0 / copilot 1.9.0] - 2026-06-16

### Added — 文体プロファイル（`documents/voice-style.md`）を caw-es に正式組込

「自分の文体で書く AI」を **書類部の AGENTS.md（CLAUDE.md）を書き換えずに**実現する仕組みを追加。本人の過去の文章（`documents/inbox/`）から文体（トーン・言い回し・一文の長さ・構成の癖）を抽出し、**専用ファイル `documents/voice-style.md` に書き出す**。設定（部署の AGENTS.md）と文体プロファイルを分離することで、誤って部署設定を上書きする事故を防ぐ。

- `caw-es/SKILL.md`（plugin + codex）: 「文体を学習して／私の文体を覚えて」で `documents/inbox/` を読み `documents/voice-style.md` を生成・更新するワークフローを新設。ES 生成時（Step 2）は `voice-style.md` があれば必ず読み、その文体で書く。重要な注意事項に「部署・`office/` の `AGENTS.md`（`CLAUDE.md`）は書き換えない」を明記。
- `job-hunting-departments.md`（3 系統）: §B-4 ディレクトリ表の `documents/` 行に `voice-style.md` を追記、§C 書類部テンプレの成果物に「文体プロファイル（『文体を学習して』で inbox から生成。設定ファイルは書き換えない）」を追記。

### Note

- 版: plugin 1.17.1 → **1.18.0** / codex 1.16.1 → **1.17.0** / copilot 1.8.0 → **1.9.0** / marketplace 同期

## [1.17.1 / Codex 1.16.1] - 2026-06-16

### Fixed — caw-research は発動時に必ず調査レベル/出力形式を尋ねる

テストで「○○について企業研究して」と伝えると caw-research が**尋ねずに既定（L2・md）で実行**される問題を修正。Step 1 の「既定は md・指定なければ md で進める」が「尋ねなくてよい」と解釈されていたため、**【必須・省略禁止】毎回必ず `AskUserQuestion` で調査レベルと出力形式を尋ねる**（企業名・業界だけ言われても自動で既定にしない）と明記。「既定」表現を「推奨（初期選択）」に変え、重要な注意事項にも追記。plugin + codex（copilot は caw-research 未収載で据え置き）。

### Note

- 版: plugin 1.17.0 → **1.17.1** / codex 1.16.0 → **1.16.1** / copilot 1.8.0 据え置き / marketplace 同期

## [1.17.0 / Codex 1.16.0 / copilot 1.8.0] - 2026-06-16

### Changed — 就活: 初期環境構築の後に「何をしますか？」と尋ねる

scaffold ＋ START HERE 生成の直後、**秘書がいきなり作業を始めず、まず `AskUserQuestion` で「何をしますか？」と尋ねる**ようにした（`job-hunting-departments.md` §D2 新設）。立ち上げた部署・QJ3a の悩みに合わせて、最初の一歩（自己分析／企業研究 `caw-research`／ES `caw-es`／面接 `caw-interview`／締切 `caw-events`／予定確認）を 4 つに絞って提示。冒頭の流れ説明にも反映。3 系統 byte 一致。

### Note

- 版: plugin 1.16.0 → **1.17.0** / codex 1.15.0 → **1.16.0** / copilot 1.7.0 → **1.8.0** / marketplace 同期

## [1.16.0 / Codex 1.15.0 / copilot 1.7.0] - 2026-06-16

### Changed — 就活オンボーディング: Q0（経験レベル）廃止＋志望職種の追加

- **就活トラックでは経験レベル（Q0「ターミナル/AI は初めてか」）を聞かない**ようにした。就活生は技術初心者が多いので、**常にはじめてモード（平易な日本語・用語説明）で進める**（`office` 設定に `> 運用モード: はじめて` を必ず書く。慣れた人が「もう普通でいい」と言えば外す）。
- **志望職種の質問（QJ2c）を追加**：志望業界（QJ2a/QJ2b）に加えて「気になっている職種は？」を複数選択で聞く（営業・販売／企画・管理／技術・研究／専門職・クリエイティブ ＋ Other）。
- `job-hunting-departments.md` §A（Q0 廃止・QJ2c 追加・注記更新）・§B-1（常に はじめてモード フラグ）、`caw/SKILL.md` の Call T 就活分岐を 3 系統で更新。

### Note

- 版: plugin 1.15.0 → **1.16.0** / codex 1.14.0 → **1.15.0** / copilot 1.6.0 → **1.7.0** / marketplace 同期

## [1.15.0 / Codex 1.14.0] - 2026-06-16

### Changed — caw-es / caw-interview が caw-research の md を必ず参照

`caw-es`・`caw-interview` が、企業固有の作業で **`caw-research` の出力 `companies/<企業>.md` を必ず参照**するようにした（任意 → 絶対）。企業 A の ES を書くと `companies/A.md` を踏まえて自動でより良いドラフトが書かれる。

- **caw-es**: Step 2 で企業固有の書類（志望動機・ES・自己PR）は最初に `companies/<企業>.md` を読む。研究の 8 ブロック（A 事業・C 強み・D 競合・G 求める人物像・H 接点）を志望動機・接点に反映。**未作成なら `caw-research` を先に実行/提案**してから書く。
- **caw-interview**: 想定問答（A）・逆質問（C）で `companies/<企業>.md` を必ず踏まえる。未作成なら `caw-research` を先に促す。
- 配信 plugin + codex（copilot は両スキル未収載で据え置き）。

### Note

- 版: plugin 1.14.0 → **1.15.0** / codex 1.13.0 → **1.14.0** / copilot 1.6.0 据え置き / marketplace 同期

## [1.14.0 / Codex 1.13.0 / copilot 1.6.0] - 2026-06-16

### Changed — caw-company を caw-research にリネーム＋調査レベル/出力形式の選択を追加

`caw-company`（企業・業界研究スキル）を **`caw-research`** に改名（「company」だと業界研究の面が伝わらず分かりにくいため）。あわせて発動時の選択肢と既定出力を見直した。

- **発動時に `AskUserQuestion` で 3 点を確認**：対象（企業/業界）／**調査レベル（L1 クイック / L2 スタンダード / L3 ディープ）**／**出力形式（md のみ / html のみ / 両方）**。
- **既定の成果物を md に**：何も指定しなければ `companies/<企業>.md`（業界は `companies/_industry/<業界>.md`）のみ生成。HTML は html / 両方 を選んだときだけ。
- **汎用 8 ブロック（A基本〜H接点）× 調査レベルの深さマッピング**を skill 本体に明文化（L1=A·B·C·F 要約／L2=+D·E·G·H／L3=全 8＋拡張）。出典強度ルール・HTML 可視化規約（id 衝突回避等）は継続。
- リネーム：`git mv` でスキルディレクトリ（plugin+codex、履歴保持）。参照（`caw-events` SKILL.md・`engine-validation-map.md`）も `caw-research` に更新。トリガは `/caw-research`。
- 配信 plugin + codex（copilot は caw-research スキル未収載・共有 `engine-validation-map.md` のみ同期）。LP/README 非掲載は継続。

### Note

- 版: plugin 1.13.0 → **1.14.0** / codex 1.12.0 → **1.13.0** / copilot 1.5.0 → **1.6.0** / marketplace 同期

## [1.13.0 / Codex 1.12.0 / copilot 1.5.0] - 2026-06-13

### Changed — 就活オンボーディングの質問を改善（全モードで業界・悩みを聞く）

就活トラックの初期ヒアリング（`job-hunting-departments.md` §A Call 1J）を刷新。**経験レベル（はじめて/Quick/Standard/Advanced）に関わらず QJ1〜QJ3 を全モードで聞く**ようにした（区分・志望業界・悩みは「プログラミング/AI が初心者か」とは無関係なため、はじめてモードでも省略しない）。

- **QJ2 志望業界を 2 段階の詳細分類に**：QJ2a（大分類 4 つ multiSelect＝メーカー／商社・流通・小売・不動産・運輸／IT・通信・メディア／金融・コンサル・インフラ・公共）→ QJ2b（選んだ大分類ごとに中分類を確認、代表 4 つ＋Other）。
- **QJ3 を「悩み」型の複数選択に**：QJ3a（テーマ別の悩み multiSelect＝自己分析／業界・企業研究／ES・書類／面接）＋ QJ3b（進め方・状況 multiSelect＝何から始めれば／複数社の締切管理／モチベ・メンタル）。
- **部署の立ち上げを QJ3a の悩みに連動**（§B-3 を更新）：選んだ悩み → 対応部署（analysis/research/writing/presentation）。何も選ばない／「何から始めれば」→ research＋analysis を既定。「締切管理」→ 秘書のスケジュール強化、「メンタル」→ 秘書が寄り添い。
- 3 系統 byte 一致（plugin の CLI 差分は注記の CLAUDE/AGENTS のみ）。LP/README 非掲載は継続。

### Note

- 版: plugin 1.12.0 → **1.13.0** / codex 1.11.0 → **1.12.0** / copilot 1.4.0 → **1.5.0** / marketplace 同期

## [1.12.0 / Codex 1.11.0 / copilot 1.4.0] - 2026-06-13

### Changed — 運営フォルダを可視化（`.company/` → `office/`）【絶対ルール】

**caw は環境構築でユーザーのプロジェクトに先頭ドット（`.`）始まりの Finder/Explorer 不可視フォルダを作らない**を絶対ルール化。IDE を導入しないユーザーが運営フォルダを確認できないのは不便なため。

- **運営フォルダ `.company/` → 可視の `office/` に全面改名**（製品リポジトリ全体 約290 箇所、plugin/codex/copilot/web/docs/hooks/README/RESUME）。成果物は従来どおり top-level（**二層原則は不変**、運営層の名前だけ可視化）。
- 二層原則の説明文（旧「ドット始まりなので非表示」）を「先頭ドットなしの可視フォルダ」に修正し、絶対ルールを `caw/SKILL.md`・ルート設定テンプレ（`claude-md-template` / `agents-md-template`）・README・`output-location-check` フックに明記。
- **`check-consistency.sh` に回帰防止ガード**を追加（配布ツリーに `.company` が再混入したら BAD で落とす）。
- ユーザー個人の既存 `~/lab/.company/`（著者の実運用環境）は製品とは別物のため不変。`~/.claude` など CLI 自身の設定ディレクトリは対象外（必須）。

### Note

- 版: plugin 1.11.0 → **1.12.0** / codex 1.10.0 → **1.11.0** / copilot 1.3.0 → **1.4.0** / marketplace 同期

## [1.11.0 / Codex 1.10.0 / copilot 1.3.0] - 2026-06-13

### Changed — 就活部署フォルダを化学トラックと統一

就活トラックが作る部署フォルダ名を化学トラックと**共通化**（中身〔CLAUDE.md / AGENTS.md〕は就活向けで別物のまま）。これにより就活 scaffold が化学と同じ部署パスを通り、間接テストハーネス（v1.10.0）の scaffold 検証がより厳密になる。

- **部署フォルダの対応**：`secretary`（窓口/選考スケ）・`research`（企業・業界研究）・`analysis`（自己分析）・`writing`（応募書類）・`presentation`（面接対策）＝化学 8 部署のサブセット。`engineering`/`computation`/`review` は化学専用で就活では作らない。
- **成果物フォルダ（top-level）は据え置き**：`companies/`・`recruit/`（research）／`self-analysis/`（analysis）／`documents/`（writing）／`interview-prep/`（presentation）。部署フォルダ名 ≠ 成果物フォルダ名（化学の `writing`→`manuscripts/` と同じ流儀）。
- 反映：`job-hunting-departments.md`（§B-3 部署表＋対応表新設・§B-4 関連部署列・§C テンプレ見出し・§E ディスパッチ、3 系統 byte 一致）、`caw-doctor` §J（就活診断の期待部署・成果物表、plugin+codex）、`engine-validation-map.md`（部署統一の注記、3 系統）。
- 就活はテストユーザー向けサブ機能のため LP/README 非掲載を継続。

### Note

- 版: plugin 1.10.0 → **1.11.0** / codex 1.9.0 → **1.10.0** / copilot 1.2.0 → **1.3.0** / marketplace 同期

## [1.10.0 / Codex 1.9.0 / copilot 1.2.0] - 2026-06-13

### Added — 就活＝化学の「間接テストハーネス」構造

就活トラックを**化学者向け本機能のテストハーネス**として明示する構造を追加。就活と化学は**同一のドメイン非依存エンジン**（オンボ → 部署 scaffold → 秘書ゲートウェイ/dispatch → スキル3パターン → HTML可視化 → memory → caw-doctor）を共有するため、**就活テストユーザーの利用が、対応する化学機能の間接検証**になる。

- **新リファレンス `skills/caw/references/engine-validation-map.md`**（3系統 byte 一致）：共有エンジン7要素の定義／**検証マップ表**（化学↔就活↔エンジンパス↔就活で検証されること、エンジンパス単位で1対1）／テストユーザー・フィードバック構造（`feedback/` ＋雛形）／著者の照合手順／構造を壊さないルール。
- **就活 scaffold に `feedback/`（top-level）を追加**：`job-hunting-departments.md` の作業ディレクトリ表に `feedback/` を、§F「テストユーザー・フィードバック（化学機能の間接検証）」を新設。秘書が節目に軽くフィードバックを促し、著者が回収して検証マップで化学側エンジンパスの signal に翻訳する。
- フィードバックは**ツールの使い勝手のみ**（個人情報・企業の非公開情報は書かせない・ローカル完結）。
- `check-consistency.sh` の codex↔copilot byte 検査に `engine-validation-map.md` を追加。
- 就活はテストユーザー向けサブ機能のため LP/README 非掲載を継続。

### Note

- 版: plugin 1.9.0 → **1.10.0** / codex 1.8.0 → **1.9.0** / copilot 1.1.2 → **1.2.0** / marketplace 同期

## [1.9.0 / Codex 1.8.0 / copilot 1.1.2] - 2026-06-13

### Added — caw-events（就活イベント・募集情報カタログ スキル）

就活トラックに、**業界横断で多数企業のインターン・企業説明会・座談会・選考イベント・締切を「詳細に」収集**する新スキル `caw-events` を追加。当初追加した締切特化の caw-deadlines を昇華し、締切だけでなくイベントの中身まで集める上位版に統合（caw-deadlines は本リリースで caw-events に置き換え）。

- 業界 or 企業リストを受け、**インターン/オープンカンパニー/説明会/座談会/本選考**を、各イベントの中身（テーマ・職種別コース・形式・対象・締切・実施日・優遇/早期選考・本選考直結・報酬・選考有無・口コミ/倍率）まで収集 → `recruit/<業界>.md`（1 イベント=1 ブロックのカタログ）と `recruit/<業界>.html`（**①イベントカタログ ②締切カレンダー ③企業×イベント比較表** の 3 ビュー）にまとめ、`secretary/todos/` の選考スケジュールへ連携。
- **出典方針**：公式採用ページを一次情報に、ナビ/就活サイトは出典併記の補助。**口コミ・倍率などの非公式は複数ソースで裏取り**。**ログイン必須・未公表は捏造せず「要確認」に分離**、締切は**取得日を併記**し「最新は公式で確認」、**カバレッジ（取得イベント数・N/M 社・未取得社一覧）を honest に報告**。
- HTML は `caw-company` の可視化規約を継承（オフライン SVG / Chart.js 選択・見出し id と canvas id 別名・各カード/行に出典＋取得日・要確認は視覚区別）。
- 就活トラック専用（LP/README の公開スキル一覧には**非掲載**）。`job-hunting-departments.md` の作業ディレクトリ表・運営ディスパッチに `recruit/`・`caw-events` を登録（3 系統 byte 一致）。
- 配信：plugin + codex（copilot は caw-events スキル未収載・共有リファレンスのみ同期）。

### Note

- 版: plugin 1.8.1 → **1.9.0** / codex 1.7.1 → **1.8.0** / copilot 1.1.1 → **1.1.2**（参照同期）/ marketplace 同期。1.9.0 は未リリースのため、当初の caw-deadlines は本エントリで caw-events に統合し版番号は据え置き。

## [1.8.1 / Codex 1.7.1] - 2026-06-13

### Changed — caw-company の出典・正確性ルール強化

企業研究の情報の正確性を担保するため、`caw-company` に**出典強度の使い分け**を明文化した。

- **Step 2「出典の取り方」を追加**：情報を公式／非公式で区別。**公式情報（IR・有価証券報告書・採用ページ＝財務指標・初任給・募集要項・平均年収の有報記載値）は単一の一次出典で可**。**非公式情報（年代別年収カーブ・職種別年収・残業・有給取得率・口コミスコア・離職率・採用大学/倍率、競合他社の年収など「他社」の非公式値）は 2 つ以上の独立ソースで突き合わせて裏取り**する。
- 値が割れたら単一値に丸めず**幅（約 X〜Y）／年度・基準を併記**（出典差に見えて実は年度差のことが多い）。口コミ由来は「**クチコミ集計値**」と明示。独立 2 ソースが取れなければ「**要確認**」。
- **HTML 可視化の注意も更新**：各セクションに出典リンクを併記し、公式は単一・非公式は複数リンクを `公式 / 非公式（複数で裏取り）` ラベルで区別。冒頭に出典方針ノートを置く。グラフは**見出しアンカー id と `<canvas id>` を別名**にする（衝突でグラフが空になる罠を明記、canvas は `ch` 接頭辞推奨）。
- plugin + codex 両配信に同一反映（copilot は caw-company 未収載のため据え置き）。

### Note

- 版: plugin 1.8.0 → **1.8.1** / codex 1.7.0 → **1.7.1** / marketplace 同期（copilot 1.1.1 据え置き）

## [1.8.0 / Codex 1.7.0] - 2026-06-12

### Added — caw-company に HTML 可視化

`caw-company`（企業・業界研究）を拡張し、`companies/*.md` に集めた情報を **ブラウザで開ける HTML** に可視化できるようにした。

- **3 ビュー**: 企業プロファイル（1社、`companies/<企業>.html`）／企業比較（複数社、`companies/_compare.html`、比較テーブル + 属性チャート + 選考スケジュール timeline）／業界ポジショニングマップ（`companies/_industry/<業界>.html`、2 軸散布図）
- **チャートは 2 方式に対応し、実行時に `AskUserQuestion` で選択**: ①オフライン自己完結（インライン SVG + CSS、ネット不要・ダブルクリックで確実に開く・推奨）②Chart.js（CDN、リッチだがネット必要）
- 製品 Web と統一したクリーンな配色（白基調 + インク + コーラル）。雛形（SVG 横棒・Chart.js レーダー）を skill に同梱
- ガードレール: `companies/*.md` の事実のみ・数値の捏造禁止・推定値は「推定」明記・個人情報/非公開情報は HTML に書かない
- caw-company は plugin + codex 配信（copilot は PoC で未収載）

### Note

- 版: plugin 1.7.1 → **1.8.0** / codex 1.6.1 → **1.7.0** / marketplace 同期（copilot 1.1.1 据え置き）

## [1.7.1 / Codex 1.6.1 / copilot 1.1.1] - 2026-06-12

### Added — caw-doctor の就活トラック診断

- **就活ルート設定に `> トラック: 就活` マーカー**を書くようにし（`job-hunting-departments.md` §B-1）、`caw-doctor` がこれを読んでトラックを自動判定するようにした
- **`caw-doctor` に §0 トラック判定 + §J 就活トラックの検査**を追加：就活なら研究向けの §5（Playbook）・§6/§6b（計算ソフト・研究成果物）をスキップし、就活部署（company-research / self-analysis / documents / interview）の設定ファイル、成果物フォルダ（`companies/` `documents/` `self-analysis/` `interview-prep/`）、`documents/inbox/`・START HERE の存在を点検
- caw-doctor は plugin + codex 配信（copilot は PoC で caw-doctor 未収載）。`> トラック` マーカーは 3 系統の job-hunting テンプレに追加

### Note

- 版: plugin 1.7.0 → **1.7.1** / codex 1.6.0 → **1.6.1** / copilot 1.1.0 → **1.1.1** / marketplace 同期

## [1.7.0 / Codex 1.6.0] - 2026-06-12

### Added — 就活専用スキル 3 本

就活モードの高頻度・多段タスクを専用スキル化（部署 + 運営モードでも動くが、一定品質で回すため）。

- **`/caw-es`** — ES・履歴書・職務経歴書・志望動機・自己PR ジェネレータ。企業の設問＋文字数を受け、
  `self-analysis/` の素材と `companies/` の志望理由から **文字数厳守・結論先出し・STAR 構造**のドラフトを生成。
  設問タイプ別の型（ガクチカ／志望動機／自己PR／強み弱み）を内蔵、`documents/inbox/` の過去 ES で文体を踏襲
- **`/caw-interview`** — 面接対策・模擬面接。想定問答生成 →「質問→回答→深掘り→改善フィードバック」の模擬面接
  ループ → 逆質問準備 → `interview-prep/<企業>.md` への振り返り記録（次回へ学びを引き継ぐ）
- **`/caw-company`** — 企業・業界研究。採用ページ・IR・ニュースを調べ `companies/<企業>.md` に構造化
  （web 検索／MCP 前提、無ければ貼り付けフォールバック）。志望動機の素材を抽出して caw-es に橋渡し

各スキルは **はじめてモード**を尊重（用語に 1 行説明・次の 1 手提示）し、**文字数厳守・誇張/虚偽禁止・
個人情報のローカル保持**を遵守。成果物は top-level（`documents/` `interview-prep/` `companies/`）に置く。

### Note

- 配信は **plugin + codex**（就活モードの主軸）。copilot（PoC）への追加は後追い（据え置き 1.1.0）
- 版: plugin 1.6.0 → **1.7.0** / codex 1.5.0 → **1.6.0** / marketplace 同期
- 就活はテストユーザー専用のため、**LP・plugin README の公開スキル一覧には掲載しない**（研究プロダクトのブランドを維持）

## [1.6.0 / Codex 1.5.0 / copilot 1.1.0] - 2026-06-12

### Added — 就活モード（テストユーザー拡大）

caw に **就活トラック**を追加。研究プロジェクトと並ぶ第 2 トラックとして、新卒就活生（学部・修士・博士・既卒）が
自己分析・企業研究・ES・面接準備・選考スケジュール管理に使えるようにした。

- **オンボーディングにトラック選択（Call T）を追加**: 起動時に「研究プロジェクト / 就活」を選ぶ。就活を選ぶと
  就活専用のオンボーディング・scaffold・運営モードに分岐（研究フローは無変更）
- **就活モードの全仕様を 1 参照ファイルに集約**（`references/job-hunting-departments.md`）: 就活プロファイルのヒアリング
  （区分・志望業界・就活フェーズ）／5 部署テンプレ（秘書〔選考スケジュール管理〕・企業/業界研究部・自己分析部・
  書類部〔ES/履歴書〕・面接対策部）／就活の作業ディレクトリ（`companies/` `documents/` `self-analysis/`
  `interview-prep/`）／START HERE（就活版）／運営モードの就活ディスパッチ
- 文字数制約厳守・誇張禁止・個人情報のローカル保持・はじめてモードでの用語説明を就活モードの遵守事項に明記
- plugin / codex / copilot の 3 系統に配信（codex/copilot は AGENTS.md 表記）

### Note

- plugin 1.5.3 → **1.6.0** / codex 1.4.3 → **1.5.0** / copilot 1.0.1 → **1.1.0** / marketplace 同期
- 研究トラックは無変更。Web LP への就活モード掲載は、化学ブランド（SPRING）の位置づけ判断が絡むため保留（テスターには直接案内）
- 次の拡張候補: 就活専用スキル（ES ドラフト `caw-es`）、caw-doctor の就活構造診断、過去 ES 取り込み（`documents/inbox/`）

## [1.5.3 / Codex 1.4.3 / copilot 1.0.1] - 2026-06-12

プロジェクト全体監査（4 観点並列）で見つかった不整合・陳腐化の一括修正。

### Fixed

- **スライド出力パスの矛盾を解消（実害バグ）**: `caw/SKILL.md` だけが `slides/` を案内し、生成側 `caw-slides` と部署テンプレ `chemistry-departments` は `presentations/slides/` を使っていた。outlier の `caw/SKILL.md` を多数派（`presentations/slides/` + スクリプトは `.company/presentation/scripts/`）に統一（plugin / codex / copilot の 3 系統）。`caw-doctor` の期待パス・旧構造移行先も追従
- **`plugin/README.md` の版数 v1.3.1 → v1.5.2 表記、`caw-slides` の記載漏れを修正**（スキル一覧とプラグイン構成ツリーに追加）
- **Web `plugin.md` の陳腐化を修正**: 「現バージョン v1.1.0」→ CLI 別の版テーブル（1.5.2 / 1.4.2 / 1.0.0）、Skills 7 件を完全列挙（caw-doctor / caw-setup / caw-slides を追加）、Hooks に PostToolUse 追記、Phase 表の同日重複を修正、ステータス更新

### Changed

- **Web に GitHub Copilot CLI を反映**: `requirements.md`・`beginner.md` の対応 CLI に追加、インストール手順に `npm install -g @github/copilot`（Node 22+）を併記、関連リンク追加
- **codex / copilot の `chemistry-departments.md` を `CLAUDE.md` → `AGENTS.md` に統一**（AGENTS.md ターゲットとの不一致を解消。plugin 版は CLAUDE.md のまま）
- **「はじめてモード」を `caw-paper` / `caw-input` / `caw-playbook` でも尊重**（plugin / codex）: 各スキル冒頭で `> 運用モード: はじめて` フラグを読み、平易な日本語・用語の 1 行説明・次の 1 手提示を適用
- **`caw-doctor` の診断を拡充**: 初心者向け投入フォルダ（`inbox/` / `_past-data/` / `papers/inbox/`）と START HERE 文書の存在チェックを追加
- **setup スクリプト（`.sh` / `.ps1`）に代替 AI CLI の案内を追加**: Claude Code を既定（Tier 1）のまま、Codex CLI / GitHub Copilot CLI の検出と導入コマンドを表示

### Infra

- **`scripts/check-consistency.sh`**: codex↔copilot の共有テンプレ（`agents-md-template.md` / `playbook-starters.md`）の byte 一致検査を追加
- **GitHub Actions CI を追加**（`.github/workflows/consistency.yml`）: push / PR で `check-consistency.sh` と Web ビルドを自動実行

### Note

- plugin 1.5.2 → **1.5.3** / codex 1.4.2 → **1.4.3** / copilot 1.0.0 → **1.0.1** / marketplace 同期

## [copilot-plugin 1.0.0 + Web] - 2026-06-04

### Added — GitHub Copilot CLI 対応（PoC）

- `copilot-plugin/` 新設：GitHub Copilot CLI 版 caw（`plugin.json` + 2 スキル `caw` / `caw-setup`、`caw` は `references/` 同梱）。Codex CLI 版（AGENTS.md ターゲット）から **CLI 固有箇所のみ**翻訳（起動コマンド `copilot`、MCP は `.mcp.json` 標準 `mcpServers` 形式）
- `.github/plugin/marketplace.json`：Copilot マーケットプレイス定義（`source: ./copilot-plugin`、登録は `copilot plugin marketplace add dr-neoueda/chemist-ai-workflow`）
- `docs/copilot-compatibility.md`：互換性アセスメント。GitHub Copilot CLI が caw のプリミティブ（AGENTS.md/CLAUDE.md 読込・`SKILL.md`・custom agents・**hooks は同名ライフサイクル**・MCP・plugin+marketplace 配布）を同型サポートする根拠と出典、移植コスト、対象外（M365 / Copilot Studio / 消費者 Copilot）を整理
- Web：補助ティアに「GitHub Copilot CLI（PoC 実証済）」を追加（`web/src/content/docs/copilot-cli/`、sidebar、splash の LinkCard + CLI 中立セクションの文言を補助 3 本に更新）
- `scripts/check-consistency.sh`：copilot-plugin の版表示 + 個人化リークスキャン対象に `copilot-plugin` / `.github/plugin` を追加

### Note

- plugin（Claude）1.5.2 / codex-plugin 1.4.2 は**無変更**。本リリースは新トラック **copilot-plugin 1.0.0** + Web + docs の追加
- PoC 簡略化：部署テンプレ見出しの `CLAUDE.md` 表記は据え置き（Copilot は `AGENTS.md`/`CLAUDE.md` 両読みのため機能上問題なし）。フルポート（残りスキル `caw-slides`/`caw-paper` 等・`hooks.json`・`.mcp.json`・実機動作確認）は Phase 2 検討

## [1.5.2 / Codex 1.4.2] - 2026-05-29

### Added — 初回ツアーの「サンプル PDF」フォールバック

- 初回ツアーの論文登録ステップで、手元に PDF が無いユーザー向けに **matplotlib で 1 枚のラベル付きサンプル PDF を生成**（`papers/inbox/caw-sample.pdf`、先頭に「練習用サンプル（削除可）」明記）→ 登録フローを体験 → 確認のうえ削除、という導線を追加。偽の論文をリポジトリに同梱せず、その場で生成して環境を汚さない。plugin / codex 両方
- バージョン: plugin 1.5.1 → 1.5.2 / codex-plugin 1.4.1 → 1.4.2 / marketplace 同期

### Web — Airtable テーマの仕上げ

- splash hero タイトルが白地に白文字で消えていた不具合を修正（`--sl-color-white` / `--sl-color-black` の上書きを削除。Starlight ではこれらは「高/低コントラスト」セマンティクスで literal 色ではない）
- favicon を Airtable パレットの化学フラスコアイコンに刷新（`web/public/favicon.svg`）
- ソーシャルカード（OGP）を追加：`web/public/og-default.png`（1200×630、白キャンバス + インク見出し + コーラルのフラスコ）と `og:image` / `twitter:card=summary_large_image` メタ

### Repo — 整合性チェックスクリプト

- `scripts/check-consistency.sh` を追加：plugin↔marketplace のバージョン一致、plugin↔codex の `caw-slides` references/templates の byte 一致、配布ツリーの個人化リーク（固有名詞）を一括検査。手作業ミラーの取りこぼし防止（CI 利用可）

## [1.5.1 / Codex 1.4.1] - 2026-05-27

### Changed — オンボーディング最初の質問を「経験レベルを率直に尋ねる」形に

- Q0（セットアップモード選択）を「どこまで詳しくやりますか？」から **「パソコンのターミナルや AI エージェントを使うのは初めてですか？」** へ言い換え。「はい、初めて」を先頭に強調し、Quick/Standard/Advanced の語が分からない初心者を取りこぼさないようにした（内部モード名は不変）。plugin / codex 両方
- バージョン: plugin 1.5.0 → 1.5.1 / codex-plugin 1.4.0 → 1.4.1 / marketplace 同期

## [1.5.0 / Codex 1.4.0] - 2026-05-27

### Added — 初心者向け初期環境（投入フォルダ・過去データ取り込み・自動インストーラ）

パソコン操作初心者に寄り添うオンボーディングへ拡張。

- **投入フォルダの自動生成**（caw scaffold）: 各計算ソフトディレクトリに `inbox/`（これから計算する入力の置き場）と `_past-data/`（過去の入出力の置き場）、research に `papers/inbox/`（PDF の置き場）を、平易な README 付きで生成。「どこに何を置くか」で迷わせない
- **過去データ一括取り込み**（caw-playbook 拡張）: `_past-data/` の過去入出力を解析し、よく使う汎関数・基底・収束設定・頻出エラーを Playbook の `## Lessons Learned` に初期 seed → その人向けに最適化
- **`caw-setup` スキル（新規）**: 外部ツール（Python・poppler・python-pptx 等）の不足を検出し、計画提示 → 一度の承認 → 順番にインストール（macOS / Windows、冪等、sudo 不使用、失敗継続）
- **bootstrap スクリプト（新規）**: `setup/caw-setup.sh`（macOS / Homebrew）・`setup/caw-setup.ps1`（Windows / winget + Scoop）。CLI・Node・git まで含めて導入（鶏卵問題対応）。同じ「計画提示 → 一括」方式
- README（plugin / codex）に caw-setup と過去データ取り込みを追記

### Added — 初心者を強めに誘導する仕組み

ターミナル・IDE・AI が初めての人を最初は強めに手引きする。

- **「はじめて」モード**（onboarding Call 0 の 4 つ目）: `.company/CLAUDE.md`（codex は AGENTS.md）に `> 運用モード: はじめて` を記録。運営モードが平易語・専門用語の 1 行説明・毎回「次はこれ」提示・不可逆操作の事前確認・コピペコマンド明示を全応答で適用
- **ガイド付き初回ツアー**（scaffold 後）: 「一緒に最初の 1 件をやってみましょう」で TODO / 論文登録 / 計算入力のいずれかを手取り足取り
- **START HERE 文書**: プロジェクト直下に `はじめにお読みください.md` を生成（これは何 / まず何をするか / 言い方早見表 / フォルダの意味 / 用語ミニ辞典 / 困ったとき）
- **用語ヘルプ + ターミナル/IDE 導入案内**: 「〇〇って何?」に平易に即答する運営ルール + Web 新ページ「はじめての方へ（ターミナル・IDE の基本）」（VS Code 導入・ターミナルの開き方・最初の起動・用語表）
- バージョン: plugin 1.4.5 → 1.5.0 / codex-plugin 1.3.5 → 1.4.0 / marketplace 同期（新スキル追加のため minor）

## [1.4.5 / Codex 1.3.5] - 2026-05-21

### Added — showcase（宣伝・紹介・募集）variant（実デッキ添削からの学び）

ユーザーが手で添削した宣伝デッキを手本に、研究発表用 4 variant とは設計思想の異なる
「実スクリーンショット主役のコラージュ型」を 5 つ目の用途バリアントとして追加。

- **`templates/generate_showcase.py`**（新規・5-8 枚）: 概念（プログラムヘッダ + ツール名サブ行 + ヒーロー図 + 説明カード2枚 + 動作環境ロゴ）／メイン機能（俯瞰図 + カード + 機能図2枚）／使用例（スクショ・コラージュ + キャプション画像上 + アプリロゴクラスタ）／募集（CTA）。個人化なし・全 `<...>` プレースホルダ。画像未挿入でもラベル箱で実行可
- **`pptx_helpers.py` に showcase helper 3 種**: `add_context_header`（プログラムヘッダ + ツール名サブ行）／`add_collage_caption`（画像上 2 行キャプション）／`add_logo_cluster`（アプリロゴを小さく等間隔・空リストは無描画）。いずれも `assert_no_overlap` 用 rect を返す
- **style-guide §15**（showcase レイアウト）: 研究発表 variant との差分表（タイトル＝プログラム名／実スクショ主役／コラージュ密度／キャプション画像上／アプリロゴ／§0 緩和／用語一般化）、helper 早見、配布物の個人化禁止
- **SKILL.md**: 用途バリアント 4→5、同梱資産に generate_showcase.py を追記（plugin / codex 両 SKILL.md）
- PR ループ: python-reviewer → codex（記録: `~/lab/.company/review/code-reviews/2026-05-21-showcase-template.md`）
- バージョン: plugin 1.4.4 → 1.4.5 / codex-plugin 1.3.4 → 1.3.5 / marketplace 同期

## [1.4.4 / Codex 1.3.4] - 2026-05-21

### Changed — フォント階層の固定化 + イラスト文字の本文スケール化（蛍デッキ反復の学び）

子供実験教室「ホタルの発光」デッキをイラスト主体で作る一連の添削から、3 つの調整を caw-slides に恒久反映。

- **フォント階層を 3 段に固定**（style-guide §2 / §14-2 / §14-3）: タイトル 28pt / 強調=L1=重要本文 24pt / 本文 20pt。**key-message band（L1）は常に 24pt**。色も役割分担（navy=見出し / dark=本文 / blue=要点 / red=注意 / grey=補足）。§14-3 がこれまで header 21・body 16 で §2 と矛盾していたのを統一
- **4 テンプレ**（generate_conference/journal_club/lab_report/lecture）の font を新階層に: ▸ヘッダー 21→24 / 本文 16→20 / L1 band 20→24
- **`research_icons` のイラスト内文字を本文スケールに拡大 + アイコンへ近接**: `label` 既定 12→17 / `sublabel` 9→13、3 ビルダーの node/center ラベルも 17–18 に、ラベル位置をアイコン直下へ寄せた（離れた配置の「スカスカ感」を解消）
- **style-guide §11bis 品質ルール拡張**: 「アイコンとラベルは近接」「イラスト内文字も本文サイズ目安（fontsize 主 16–19 / 強調 22–24 / 補助 13–15）」「ドメイン特有アイコンは patches で自作可（材料＝登場人物）」を追加
- PR: python-reviewer（constant-tuning、回帰なし APPROVE。figure-lifecycle/guards 健在）。research_icons は 1.4.3 で codex 二段済・本変更は定数のみのため codex 再実行なし。記録: `~/lab/.company/review/code-reviews/2026-05-21-firefly-deck-and-falsepositive.md`
- バージョン: plugin 1.4.3 → 1.4.4 / codex-plugin 1.3.3 → 1.3.4 / marketplace 同期

## [1.4.3 / Codex 1.3.3] - 2026-05-20

### Added — 概念イラストモジュール `research_icons`

caw 宣伝デッキ等のイラスト作成を重ねて確立したノウハウを、再利用可能な配布
モジュールとして恒久化（references 層、`pptx_helpers` と同階層）。任意テーマの
スライドで同等品質の概念イラストを量産できる。

- **線画アイコン 10 種**（`icon_researcher` / `icon_flask` / `icon_molecule` /
  `icon_document` / `icon_chart` / `icon_slides` / `icon_gear` / `icon_magnifier` /
  `icon_laptop` / `icon_sparkle`）。共通シグネチャ `icon(ax, x, y, s=1.0, color=)`、
  同縮尺で混在可。`ICONS` 名前レジストリ付き。配色は `CATEGORICAL_HEX` に整合
- **構図ビルダー 3 種**（PNG パスを返す → `add_picture_fit` に渡す）:
  - `hub_diagram` — 中心 + 放射（部署図・構成要素）
  - `cycle_diagram` — 円環 + 駅間の隙間に弧矢印（研究サイクル。駅を貫かない）
  - `converging_diagram` — 周辺要素が中心へ収束（負荷が押し寄せる課題図。矢じりはリム着地）
- ヘルパ `label` / `sublabel` / `new_figure` / `save_figure`（ビルダーに無い構図を自作する用）
- **style-guide.md §11bis「概念イラスト（schematic）作成」を新設**: イラスト vs チャートの
  題材判断表（規模・桁比較は定量チャート、構成・サイクルはイラスト）、アイコンカタログ、
  3 ビルダーの使い方、品質ルール（矢印はリム/隙間着地・サブラベルで密度・等間隔等縮尺・
  背景は白基調で過度な装飾を避ける）。§14-6 早見表と SKILL.md にも追記
- PR ループ: python-reviewer（HIGH 1 = Figure リーク + MEDIUM 5 + LOW 2）→ codex-rescue
  二段（MEDIUM 2 = 高密度サイクルの弧反転・save 時クリーンアップ順序 + LOW 2）。全件対応。
  記録: `~/lab/.company/review/code-reviews/2026-05-20-research-icons.md`
- バージョン: plugin 1.4.2 → 1.4.3 / codex-plugin 1.3.2 → 1.3.3 / marketplace 同期

## [1.4.2 / Codex 1.3.2] - 2026-05-20

### Changed — カテゴリカル配色（青一色の解消）

CP2K 初学者向けデッキ生成の添削で「全体が青中心で単調」と判明。図表・グラフに識別・対比・強調のための複数色を導入。

- **`CATEGORICAL_HEX` / `CATEGORICAL_RGB`**: 青→橙→緑→赤→シアン→紫→アンバーの 7 色パレット
- **`add_bar_chart` / `add_scatter_line_chart`**: 系列をパレットで自動色分け（線 + マーカー）。マーカー着色は `show_markers` 時のみ
- **`add_data_table(highlight_row=N)`**: 推奨案 / hero 行を淡アンバー（`COLOR_ROW_HIGHLIGHT_FILL` #FFF2CC）で塗る。範囲外は ValueError
- **`add_energy_diagram`**: 状態を役割色（始=青 / 終=緑 / TS・中間体=赤）、connector はグレー。位置（山/谷）が意味を担うため赤緑 CVD でも判別可
- **style-guide.md §0 に「図表・グラフは青一色を避け、カテゴリカル配色」節**を追加（多系列はパレット巡回、テーブルは highlight_row、対比の鉄則は維持）
- PR ループ: python-reviewer（HIGH 1 + MEDIUM 1 + LOW 2 修正、show_markers ガード等）。codex-rescue は背景継続が時間内未完のため Claude + 自己評価で補完
- バージョン: plugin 1.4.1 → 1.4.2 / codex-plugin 1.3.1 → 1.3.2 / marketplace 同期

## [1.4.1 / Codex 1.3.1] - 2026-05-20

### Changed — caw-slides の「AI 作成感」除去（実デッキ添削 fb 反映）

MLIP 研究紹介デッキを caw-slides で生成し、その添削から得た改善を `pptx_helpers.py` と `style-guide.md` に反映。

- **表の空白圧縮（`add_data_table`）**: デフォルト `word_wrap=False`、header 行 = `header_size × 2.0` / body 行 = `font_size × 2.0` に分離（CJK headroom）、セル上下余白 3pt、`row_height=Emu(0)` を auto 扱い。4 行表が 0.9"/行(3.6") → 0.44"/行(1.78") に圧縮。`row_height` / `cell_margin` / `word_wrap` パラメータ追加（後方互換）
- **style-guide.md §0 に「表とまとめスライドの作り込み（AI 作成感の除去）」節を新設**:
  - 表は内容に密着（tight 行・全幅に伸ばさず中央寄せ）。埋めたいなら空白でなく情報を足す
  - まとめ/結語スライドにも必ず図を置く（positioning 図等）
  - **コンテンツスライドは「図・表・グラフ + L1 + 支持本文」を基本構成に**（図 + L1 だけのスパース構成を避ける。視覚要素が幅を埋めないなら左に視覚・右に支持本文の 2 ゾーン、横長テーブルは上に視覚・下に支持本文）
  - **「箱に文字を詰めた」text-box フロー図（`add_flow_box` × N）は原則作らない**。第一選択はプロセスの効果をグラフで示す（例 active learning → 学習曲線）、第二選択はイラスト/アイコン + 最小ラベル
  - 図表構成要素（フロー box・テーブル・split_2col）は §0 文字数上限の対象外（`assert_text_minimal` の override 指針）
- PR ループ: python-reviewer + codex-rescue。`add_data_table` 改修で HIGH 1（行高さ × word_wrap）+ MEDIUM 2（header/body 分離・CJK 余裕）+ LOW 2 を修正
- バージョン: plugin 1.4.0 → 1.4.1 / codex-plugin 1.3.0 → 1.3.1 / marketplace 同期

## [1.4.0 / Codex 1.3.0] - 2026-05-15

### Added — `caw-slides` Skill（PowerPoint スライド生成）

化学研究発表用 PowerPoint スライドを python-pptx ベースで生成する専用 Skill。実運用された 12 件のスライドから抽出したスタイルガイドを内蔵し、4 用途バリアントで「学会発表 / 論文紹介 / 報告会 / 講義」に対応する。

- **発火**: 自然言語マッチ（「スライド作って」「パワポ」「学会発表」「論文紹介」「報告会」「講義スライド」等）
- **同梱資産**（plugin / codex-plugin 並列配信）:
  - `references/pptx_helpers.py`（1000+ 行）: `add_slide_chrome` / `add_key_message_band` / `mixed_runs` / `assert_no_overlap` / `add_bar_chart` / `add_scatter_line_chart` / `add_flow_box` / `add_data_table` 等のヘルパ。MS Gothic のクロスプラットフォーム探索（macOS / Windows / Linux、`CAW_SLIDES_MSGOTHIC` 環境変数で override 可）
  - `references/style-guide.md`: 14 セクション + canonical 実装パターン（**§0 絶対ルール = 文字数を極限まで減らし図表で直感的に伝える**、16:9、フォント混在、L1 強調 1 個ルール、3 層 y 座標構造（chrome / 本文 / key-message band）、3 tier 強調 L1/L2/L4（L2 = 影なし・枠線あり・塗りなしの透明箱）、native chart 強制、座標 hygiene、出典は用途別に任意で `add_source_line`）
  - **§0 強制ヘルパ（実装済み）**: `assert_text_minimal(slide)` でテキストボックス数 ≤ 5 / 本文総行数 ≤ 12 / 1 ボックス内 ≤ 120 字を自動検証（違反は ValueError）; `assert_title_assertive(title)` で「結果」「考察」「方法」「目的」等の無味な見出しを lint（22 ワードの blacklist 内蔵）
  - **化学特化ヘルパ**: `add_molecule(slide, smiles)` — SMILES → RDKit Draw → PNG embed (lazy import); `add_reaction_scheme(slide, reactants, products, conditions)` — 反応式の横並び合成（reactant + reactant → product, conditions ラベル付き）; `add_energy_diagram(slide, levels, labels)` — 反応座標 vs エネルギーの 1 ライン図（matplotlib smoothstep、TS は短い dash で sharp peak 表現）
  - **レイアウトパターン**: `split_2col(slide, left_paragraphs, right_paragraphs)` — 2 カラム比較（Form I/II・before/after 等の概念対比受け皿）; `add_timeline(slide, milestones=[(date, event), ...])` — 横軸時系列バー（≤ 8 milestones、衝突 guard 付き）
  - **クロスプラットフォーム / 安全性**: matplotlib 日本語 lazy auto-config（`_ensure_matplotlib_japanese`、未検出時は `RuntimeWarning` で診断）; PNG temp file は `try/finally + os.unlink` で確実 cleanup（Windows の PIL 再オープン bug 対策含む）
  - `references/codex-exec-templates.md`: Codex 委譲 v2（完全お任せ）プロンプトテンプレ集
  - `templates/generate_conference.py`: 学会発表 variant（口頭・ポスター、20-50 枚）
  - `templates/generate_journal_club.py`: 論文紹介 variant（6-12 枚、pdftoppm + crop ワークフロー）
  - `templates/generate_lab_report.py`: 研究室報告会 variant（6-15 枚、native chart + table）
  - `templates/generate_lecture.py`: 講義・チュートリアル variant（15-30 枚、概念フロー図）
- **品質ゲート**: `assert_no_overlap` で shape 矩形交差を物理的に禁止（ValueError raise）、L1 1 個ルール、Excel-editable native chart のみ
- **動作確認**: 4 templates 全て smoke test 成功（標準的な 4 枚のデモ .pptx を生成、`assert_no_overlap` pass）

### Changed

- **`plugin/skills/caw/references/chemistry-departments.md`**: presentation 部の説明を caw-slides skill 利用前提に更新。サブディレクトリ列挙に `scripts/`, `notes/`, `references/` を追加、成果物パスを `slides/` → `presentations/slides/` に統一
- **`plugin/skills/caw/references/playbook-starters.md`**: 「計算外ソフトの Playbook」セクションを追加し、caw-slides との関係を明示
- **`web/src/content/docs/claude-code/application.md`**: §5 を caw-slides skill ベースに改稿（4 用途バリアント、共通スタイルガイド、`assert_no_overlap` 保証）
- `plugin/.claude-plugin/plugin.json` version 1.3.1 → 1.4.0
- `codex-plugin/.codex-plugin/plugin.json` version 1.2.1 → 1.3.0
- `.claude-plugin/marketplace.json` plugin 列挙の version 同期

### Notes

- スライド生成システムは元々ユーザーの `.company/presentation/` で実運用されていた成熟資産を caw plugin 化したもの。新規開発ではなく **配信パッケージング**として実装。個人情報（著者名・研究室名・特定研究テーマ・機器型番）はすべて除去済み
- Codex CLI 版（codex-plugin）も同一資産を並列配信。両 CLI で完全機能パリティ
- python-pptx の依存（`python-pptx`、`matplotlib`、`Pillow`）はユーザーが事前にインストール
- スタイルガイド本体（`references/style-guide.md`）はプラグイン更新で上書きされる。プロジェクト固有のオーバーライドは `.company/presentation/CLAUDE.md` (or AGENTS.md) に追加

## [1.3.1 / Codex 1.2.1] - 2026-05-14

### Fixed（B16 — Windows / Linux 対応）

- **`plugin/hooks/load-playbooks.sh`**：mtime 降順ソートを BSD/macOS 専用の `xargs -0 stat -f "%m %N"` から `ls -t`（macOS / Linux / WSL / Git Bash 共通の POSIX）に置換。これまで macOS 以外（Linux 含む）で直近ノートの注入が動いていなかったのを修正
- **`plugin/skills/caw-doctor/SKILL.md` / `codex-plugin/skills/caw-doctor/SKILL.md`**：Playbook の `last_updated` 経過日数計算を BSD/macOS 専用の `date -j -f` から、GNU `date -d` → BSD `date -j` フォールバックの `to_epoch` ヘルパーに置換。macOS 以外でも動作するように

### Changed

- **`.company/` の可視性に関する説明を OS 別に正確化**：「Finder / Explorer から不可視」という macOS/Linux 前提の表現を「macOS Finder / Linux のファイルマネージャでは標準で非表示、Windows Explorer では表示される（いずれの OS でも運営情報専用エリアという位置づけは同じ）」に修正。SKILL.md / claude-md-template / agents-md-template / chemistry-departments / output-location-check.sh / README
- **`plugin/README.md`**：「動作環境」節を追加（OS × コア/Hooks の対応表、Windows は WSL / Git Bash 必須の旨）。v1.1.0 のまま古かった Skills / Hooks / Playbook / プラグイン構造の記述を v1.3.1 の実態に更新
- `plugin/.claude-plugin/plugin.json` version 1.3.0 → 1.3.1
- `codex-plugin/.codex-plugin/plugin.json` version 1.2.0 → 1.2.1
- `.claude-plugin/marketplace.json` version 同期

### Notes

- caw のコア（オンボーディング・部署スキャフォールド・5 Skills のワークフロー）は元々 OS 非依存。今回の修正は **hooks と caw-doctor の bash スニペットに混入していた macOS 専用構文**（`stat -f` / `date -j`）の除去で、これらは Windows のみならず Linux でも壊れていた
- Windows でネイティブに hooks を動かすには WSL または Git Bash が必要（`hooks.json` が `bash` を呼ぶため）。コア機能は Windows ネイティブでも動作

## [1.3.0 / Codex 1.2.0] - 2026-05-14

### Added

- **B1 — Codex 版の Skills 機能パリティ**：`caw-paper` / `caw-input` / `caw-playbook` を `codex-plugin/skills/` に移植。Codex 流に合わせ `trigger:` フィールドを削除し、自然言語マッチで発火。CLAUDE.md → AGENTS.md 表記に変換。これで両プラグインとも 5 Skills（caw / caw-doctor / caw-paper / caw-input / caw-playbook）で揃った
- **B2 — `caw-doctor` Skill 新規追加**（Claude / Codex 両版）：`.company/` 構造の健全性チェック。ルート CLAUDE.md・秘書部・各部署 CLAUDE.md の存在確認、旧構造（成果物が `.company/<dept>/X/` に残存）の検出、Playbook 更新滞り、同日ファイル重複、inbox 孤立ファイルを総点検し、レポート + 修復コマンドを提示
- **B7 — Playbook 雛形を 8 件拡充**（Claude / Codex 両版）：計算ソフト 4 件（Psi4 / NAMD / LAMMPS / OpenMM）+ Python ライブラリ 4 件（RDKit / ASE / MDAnalysis / pymatgen）を `playbook-starters.md` に追加。Python ライブラリ Playbook は API quirks・version 依存挙動・よくある罠を体系化
- **B8 — MCP 自動セットアップ案内**（Claude / Codex 両版）：オンボーディング Step 3-5 で Q3（ナレッジベース）/ Q4（クラウドストレージ）の選択に応じて `.company/.mcp-setup.md` を生成。Notion / Obsidian / Logseq / Google Drive / Dropbox / OneDrive / Gmail の MCP 設定手順 + API key の環境変数管理ガイド。`references/mcp-setup-templates.md` を新規追加。**鍵そのものは書かず手順書のみ**
- **B10 — オンボーディングの 3 段階化**（Claude / Codex 両版）：Step 2 に「セットアップモード」選択（Call 0）を追加。Quick（1 問・秘書のみ即起動）/ Standard（現行 6 問）/ Advanced（10+ 問、HPC・研究体制・申請書予定・論文ステータスまでヒアリング）
- **B11 — PostToolUse hook で二層原則違反を検出**（Claude Code 版のみ）：`plugin/hooks/output-location-check.sh` を追加。Edit/Write/MultiEdit が `.company/<dept>/<旧パス>/` に書き込んだ時に警告 + 修復コマンドを提示（block はしない warn-only）。`hooks.json` に PostToolUse エントリを追加。Codex 版は hook framework が未整備のため未対応

### Changed

- **`plugin/skills/caw/SKILL.md` / `codex-plugin/skills/caw/SKILL.md`**：Step 2 を 3 段階モード化、Step 3 に MCP セットアップ生成（3-5）を追加し完了メッセージを 3-6 にリネーム、「ファイル参照」に `mcp-setup-templates.md` を追加
- **`plugin/skills/caw/SKILL.md` / `codex-plugin/skills/caw/SKILL.md`**：オンボーディング Q2（計算ソフト）の古典 MD 例示に NAMD / OpenMM を追記（B7 と整合）
- `plugin/.claude-plugin/plugin.json` version 1.2.0 → 1.3.0
- `codex-plugin/.codex-plugin/plugin.json` version 1.1.0 → 1.2.0
- `.claude-plugin/marketplace.json` version 同期

### Notes

- Codex 版は hooks 非対応（B11 のみ Claude Code 限定）。それ以外（B1/B2/B7/B8/B10）は両プラグインで機能等価
- caw-doctor は v1.2 の二層原則 migration 状況の点検にも使える（旧構造を検出して移行コマンドを提示）

## [1.2.0 / Codex 1.1.0] - 2026-05-14

### Added

- **成果物配置の二層原則（CRITICAL）**：caw の出力ファイルを `.company/` 配下（運営情報）と project root 直下（成果物）に明確に二層化
  - 第 1 層 `.company/<dept>/` = 運営情報のみ（TODO・意思決定・学び・Playbook・内部レビュー）
  - 第 2 層 project root = 成果物（`papers/`, `topics/`, `manuscripts/`, `slides/`, `analyses/`, `notebooks/`, `figures/`, `scripts/`, `tools/`, `reports/`, `experiments/`, `gaussian/` 等）
  - `.company/` は dotfile で Finder / Explorer から不可視。AI が生成した md / pptx / docx / png / ipynb 等を `.company/<dept>/` に置くと **ユーザーがファイラーで見つけられない** という v1.0 / v1.1 の構造的問題を解消

### Changed

- **`plugin/skills/caw/SKILL.md`**：「成果物配置の二層原則」セクションを追加。Step 3-4 の作業ディレクトリ生成リストを拡張（research → `papers/` + `topics/`、analysis → `analyses/` + `notebooks/` + `figures/`、engineering → `scripts/` + `tools/`、presentation → `slides/`）
- **`plugin/skills/caw/references/chemistry-departments.md`**：research / engineering / analysis / writing / presentation の各 CLAUDE.md テンプレで出力パスを `.company/<dept>/X/` から `{{PROJECT_ROOT}}/X/` に変更
- **`plugin/skills/caw/references/claude-md-template.md`**：ルート CLAUDE.md にも二層原則を明文化
- **`codex-plugin/skills/caw/SKILL.md`**：同上（AGENTS.md 表記）
- **`codex-plugin/skills/caw/references/agents-md-template.md`**：同上
- **`codex-plugin/skills/caw/references/chemistry-departments.md`**：同上
- `plugin/.claude-plugin/plugin.json` version 1.1.0 → 1.2.0
- `codex-plugin/.codex-plugin/plugin.json` version 1.0.0 → 1.1.0
- `marketplace.json` version 同期

### Migration（v1.0 / v1.1 → v1.2 / Codex 1.0 → 1.1）

既存ユーザーが旧構造（`.company/research/papers/`, `.company/writing/manuscripts/`, `.company/analysis/results/`, `.company/presentation/slides/`）に成果物を蓄積している場合、以下を手動で実施：

```bash
# 移動例（既存ファイルがある場合のみ実行）
mv .company/research/papers/* papers/ 2>/dev/null
mv .company/research/topics/* topics/ 2>/dev/null
mv .company/writing/manuscripts/* manuscripts/ 2>/dev/null
mv .company/analysis/results/* analyses/ 2>/dev/null
mv .company/analysis/figures/* figures/ 2>/dev/null
mv .company/analysis/notebooks/* notebooks/ 2>/dev/null
mv .company/presentation/slides/* slides/ 2>/dev/null
```

`.company/<dept>/` 配下に残った空ディレクトリ（`papers/` `manuscripts/` 等）は削除して構わない。残しても害は無い（caw が読みに行かなくなるだけ）。

将来 v1.3 で `caw-migrate` Skill を追加予定（自動移動 + 衝突解決 + dry-run）。

## [Codex 1.0.0] - 2026-05-13

### Added (Codex CLI 版)

- **codex-plugin/**：Codex CLI 用 caw プラグイン（v1.0.0）を新規追加
  - `codex-plugin/.codex-plugin/plugin.json` — Codex 用プラグインマニフェスト
  - `codex-plugin/skills/caw/SKILL.md` — `/caw` スキル本体（CLAUDE.md → AGENTS.md ターゲットに変換）
  - `codex-plugin/skills/caw/references/{agents-md-template, chemistry-departments, playbook-starters}.md`
- **`.agents/plugins/marketplace.json`**：Codex 用マーケットプレイス manifest（同リポジトリから並列配信）
- **LP**：`/codex-cli/` セクションを placeholder から実装に書き換え、`/codex-cli/setup/` 環境構築ページを新規作成
- **plugin.md**：両環境のインストール手順（Claude Code / Codex CLI）を併記

研究室で Claude Code 派と Codex CLI 派が混在しても、同じ caw メソッドで `.company/` を運用できる構成。

## [1.1.0] - 2026-05-13

### Added

- **Hooks**：SessionStart で `.company/secretary/notes` の直近 3 件と利用可能 Playbook をコンテキスト自動注入、Stop で今日の活動があるのに learnings.md が無い場合にリマインド。
- **`/caw-paper` スキル**：論文検索（arXiv / Crossref / Semantic Scholar / OpenAlex / PubMed）と入手済み PDF の自動メタデータ抽出 → ナレッジベース（Notion / Obsidian / Logseq 等）+ クラウドストレージ（Google Drive 他）への登録。バッチ処理対応。
- **`/caw-input` スキル**：6 ソフト（Gaussian / ORCA / CP2K / GROMACS / VASP / Quantum ESPRESSO）の入力ファイル雛形生成。Playbook デフォルト推奨値を起点に対話的に系・目的・計算条件を確定、`<tool>/<system>_<purpose>_<YYYYMMDD>/` 配下に配置 + ジョブ記録自動生成。
- **`/caw-playbook` スキル**：計算 log の自動解析（収束 / エラー / 異常パターン）→ Lessons Learned エントリ起案 → Playbook への末尾追記。memory feedback への昇格判定も含む。

### Changed

- `plugin.json` version 1.0.0 → 1.1.0（後方互換のスキル追加）。
- `marketplace.json` version 同期。

## [1.0.0] - 2026-05-13

### Added

- 初回公開。caw プラグイン（Chemist's AI Workflow）。
- `/caw` スキル：オンボーディング → 自動スキャフォールド → 運営モードの一連を実装。
- 化学者向け 8 部署 CLAUDE.md テンプレート（secretary / research / engineering / computation / analysis / writing / review / presentation）。
- 計算ソフト Playbook 雛形：Gaussian / GROMACS / CP2K / ORCA / VASP / Quantum ESPRESSO + 汎用。
- 作業ディレクトリの自動生成：選択した計算ソフトに応じて `gaussian/` / `orca/` 等、選択した部署に応じて `papers/` / `manuscripts/` / `slides/`。
- ローカル marketplace 経由の開発・テスト環境。
- 4 つのテストプロファイルでの実機検証完了。

### Documentation

- 配布マーケットプレイスの `.claude-plugin/marketplace.json` を整備。
- MIT ライセンス採用。
- Chemist's AI Workflow LP（Astro Starlight）。
