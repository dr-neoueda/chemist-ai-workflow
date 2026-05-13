---
title: 対応ツール一覧
description: ナレッジベース・クラウドストレージの API / MCP 対応状況、アーキテクチャ別の実装パス、推奨組み合わせ
---

## このページの目的

LP では「お使いのナレッジベース + クラウドストレージに自動登録」と書いていますが、**実際にはツールごとに API / MCP の成熟度・アーキテクチャが大きく異なり、すべての組み合わせが同じ自動化レベルになるわけではありません**。

このページでは、著者が **Notion + Google Drive** で組んでいる文献管理パイプライン（PDF → Markdown → Drive アップロード → Notion DB 登録）と同等のことが、各組み合わせでどこまで実現できるかを honest にまとめます。

## アーキテクチャは大きく 2 系統

文献管理パイプラインのアーキテクチャは大別して 2 つあります。**どちらの系統を選ぶかで、選べるツールと実装パスが変わります**。

### 系統 A：DB ベース + クラウドストレージ（Notion 型）

- メタデータ（著者・誌名・年・要約・タグ）を DB に格納し、PDF は別のクラウドストレージに置く
- DB 側に「PDF へのリンク」を property として持たせる
- 著者の現運用がこの系統

```
PDF (inbox)
  ├─ → Markdown 抽出 → DB レコード作成（メタデータ + 要約 + タグ）
  └─ → クラウドストレージへアップロード → DB に URL 登録
```

### 系統 B：ファイルベース vault + sync（Obsidian 型）

- vault フォルダに .md ファイル（メタデータは frontmatter）と PDF を一緒に置く
- vault 全体をクラウドストレージで sync
- DB 表現力は Dataview プラグイン等で擬似する

```
PDF (inbox)
  └─ → vault フォルダにコピー（attachments/）
       + Markdown ノート作成（frontmatter にメタデータ）
       → クラウドストレージで vault 全体 sync
```

## ナレッジベース対応状況

| ツール | API / MCP | アーキテクチャ | DB 表現力 | 自動化成熟度 | コメント |
|---|---|---|---|---|---|
| **Notion** | Anthropic 公式 MCP + 安定 REST API | DB 系統 A | ◎（property + relation） | ★★★ | 著者の現運用。フル自動化が最も組みやすい |
| **Obsidian** | Filesystem MCP 経由 + Local REST API プラグイン（コミュニティ） | ファイル系統 B | ◯（Dataview / Bases plugin） | ★★ | ローカル前提。vault sync でクラウド連携。frontmatter で構造化 |
| **Logseq** | HTTP API（限定的）+ Filesystem MCP 経由 | ファイル系統 B | ◯（block 構造） | ★★ | 自動化は Obsidian と同等の手法 |
| **Joplin** | REST API（Web Clipper service） | ファイル系統 B | △ | ★★ | OSS、自前 sync 設定が必要 |
| **Roam Research** | Backend API（要 Research プラン） | DB 系統 A | ◎（networked thought） | ★ | API 制限・有料プラン要件で自動化コスト高 |
| **Bear / Apple Notes** | x-callback-url のみ | クローズド | ✕ | ✕ | 自動化は事実上不可。本書の対象外 |
| **Anytype** | API（β） | P2P | △ | ✕ | 成熟度低、推奨せず |

## クラウドストレージ対応状況

| ツール | API / MCP | 自動化成熟度 | コメント |
|---|---|---|---|
| **Google Drive** | Anthropic 公式 MCP + REST API | ★★★ | 著者の現運用。共有・権限管理・URL 安定 |
| **Dropbox** | コミュニティ MCP + REST API | ★★★ | API 安定、共有リンクも扱いやすい |
| **OneDrive** | コミュニティ MCP + Microsoft Graph API | ★★ | Microsoft アカウント前提、Graph API は仕様がやや複雑 |
| **Box** | REST API | ★★ | 個人ユーザーには稀、研究機関契約で使われる |
| **iCloud Drive** | 公式 API なし（macOS ファイルシステム経由のみ） | ★ | Mac ローカルでは Filesystem MCP 経由可。cross-device 自動化は困難 |

## 推奨組み合わせ

### 第一級（フル自動化が最も簡単）

| 組み合わせ | 系統 | 理由 |
|---|---|---|
| **Notion + Google Drive** ★ 著者環境 | A | 両者 Anthropic 公式 MCP、API 完備、最も検証が深い |
| Notion + Dropbox | A | Notion 公式 MCP + Dropbox API。Drive をストレージのみ差し替え |
| Notion + OneDrive | A | 同上、Microsoft 系を主に使う研究室向け |

### 第二級（ファイル系統 B、ローカル中心）

| 組み合わせ | 系統 | 理由 |
|---|---|---|
| **Obsidian + Google Drive / Dropbox** | B | vault を sync。最も人気のローカルナレッジベース |
| Obsidian + iCloud Drive | B | Mac/iOS で完結、cross-device 自動化なし |
| Logseq + Google Drive / Dropbox | B | Obsidian と同パターン、block 派向け |

### 非推奨 / 自動化困難

| ツール | 理由 |
|---|---|
| Bear / Apple Notes | 公開 API なし、自動化基盤が組めない |
| Roam Research（Research プラン以外） | API 制限多く、自動化に不向き |
| Anytype | β API、成熟度不足 |

## 実装パスの比較

### パス 1：MCP（Claude Code 経由が最も簡単）

- **ナレッジベース**: Notion 公式 MCP、Filesystem MCP（Obsidian / Logseq vault）
- **クラウドストレージ**: Google Drive 公式 MCP、Dropbox / OneDrive コミュニティ MCP
- 認証は MCP サーバー側で扱われる

### パス 2：REST API 直接（任意の CLI / スクリプト）

- 各ツールの SDK / API キーを使って Python / TypeScript で直接実装
- Notion / Drive / Dropbox / OneDrive / Joplin: 公式 SDK または HTTP クライアント
- Obsidian: Local REST API プラグイン（コミュニティ）経由

### パス 3：Filesystem-based（最もシンプル）

- vault / 同期フォルダにファイルを置くだけ
- ツール側がそれを認識する（Obsidian / Logseq の場合）
- クラウドストレージは sync を担当
- API / MCP 不要だが、メタデータ構造化は frontmatter で自前管理

## 実装上の留意点

### 認証情報の管理

- Notion: Internal Integration Token、scope を文献 DB に絞る
- Google Drive: OAuth 2.0、refresh token を `.env` で管理
- Dropbox: App key、長期トークン
- OneDrive: Microsoft Graph、tenant 設定が必要な場合あり

すべての公式 SDK / MCP サーバーは認証情報をローカルまたはツール内で扱うため、**ノートブック・LP・公開リポジトリにキーを直接書かない**ことを徹底します（本書の品質ゲートでも検出可能）。

### DB 表現力のギャップ

- Notion の relation / rollup は**他ツールでは frontmatter + 自前検索で擬似する**ことになります
- Dataview（Obsidian）は強力だが、cross-vault クエリは制限がある
- 「論文 → 著者 → ラボ」のようなネットワーク構造を厳密に表現するなら Notion / Roam が向く

### 同期の信頼性

- Google Drive: ファイル衝突の検出と解決が比較的安定
- Dropbox: 大容量同期に強い
- iCloud Drive: macOS のキャッシュ挙動でズレが出ることがある（運用注意）

## 著者の実装メモ（参考）

著者は以下の構成で 200+ 本の論文を運用しています：

```
~/lab/papers/
  ├─ inbox/        ← PDF を一旦ここに
  ├─ md/           ← 抽出した Markdown
  └─ scripts/      ← パイプライン（PDF → md → Drive → Notion）

連携先：
  - Google Drive: PDF 本体、共有 URL 管理
  - Notion DB: メタデータ・要約・タグ・引用関係（property + relation）
```

詳細な実装は教材本編（claude-code 版）で配布予定です。Obsidian / Logseq 版の対応パイプラインも Phase 2 で執筆します。

---

## 計算化学ソフト対応状況

文献管理と同様、**「ChatGPT を超える」のような誇張をせず、実装可能性を honest に示す**ことを優先します。

### 大原則：CLI ベースであれば方法論が転用できる

著者環境（Gaussian / GROMACS / CP2K）はすべて **CLI ベース**：

- 入力ファイル: テキスト（`.gjf` / `.mdp` / `.inp`）
- log: テキスト
- ジョブ submission: shell コマンド（bash / qsub / sbatch）

AI 部署が**読み書き・編集・提出・log 解析・Playbook 蓄積**をすべてテキストで扱えるため、方法論は他の CLI ベースソフトにそのまま転用できます。

逆に **GUI 必須のソフト**は AI エージェントで自動化が困難で、本書の対象外です。

### CLI ベース：自動化可能 ★★★

| カテゴリ | ツール | 入力形式 | コメント |
|---|---|---|---|
| 量子化学 | **Gaussian** ★ 著者環境 | `.gjf`（テキスト） | GaussView は補助、本体は CLI |
| 量子化学 | **ORCA** | `.inp`（テキスト） | 学術無料、人気急上昇 |
| 量子化学 | **Q-Chem** | `.in`（テキスト） | IQmol GUI は任意 |
| 量子化学 | **Psi4** | Python script / `.dat` | OSS、Python API も充実 |
| 量子化学 | **GAMESS** | `.inp`（テキスト） | OSS、伝統的 |
| 量子化学 | **NWChem** | `.nw`（テキスト） | OSS、HPC 向け |
| 量子化学 | Molpro / TURBOMOLE | テキスト | 商用、CLI 中心 |
| 古典 MD | **GROMACS** ★ 著者環境 | `.mdp` / `.gro` / `.top` | 完全 CLI |
| 古典 MD | **AMBER** | `.in` / `.prmtop` / `.rst` | 完全 CLI |
| 古典 MD | **NAMD** | `.conf` / `.psf` / `.pdb` | 完全 CLI |
| 古典 MD | **LAMMPS** | `.in`（コマンドスクリプト） | OSS、材料系で人気 |
| 古典 MD | **OpenMM** | Python script | OSS、Python API |
| 古典 MD | CHARMM / Tinker | テキスト | CLI |
| 周期系 DFT | **CP2K** ★ 著者環境 | `.inp`（テキスト） | OSS、AIMD/Quickstep |
| 周期系 DFT | **VASP** | `INCAR` + `POSCAR` + `KPOINTS` + `POTCAR` | 商用、材料系で標準的 |
| 周期系 DFT | **Quantum ESPRESSO** | `.in`（テキスト） | OSS、人気 |
| 周期系 DFT | CASTEP / SIESTA / ABINIT / CRYSTAL | テキスト | CLI |
| Python ライブラリ | ASE / pymatgen / cclib / MDAnalysis / RDKit / Open Babel | Python script | 自動化最適 |

**Playbook は各ソフト固有**だが、書式・運用パターンは Gaussian / GROMACS / CP2K の Playbook をテンプレートに作れます。

### CLI + GUI 並存：CLI モードで自動化可能 ★★

| ツール | コメント |
|---|---|
| **PyMol** | Python script で描画自動化可（GUI なしで PNG / 動画生成可） |
| **VMD** | Tcl スクリプトで自動化可 |
| **CASTEP / WIEN2k** | GUI もあるが CLI で完結可 |
| Avogadro / Chemcraft | 主に可視化、自動化は限定的 |

### ハイブリッド：一部のみ自動化可 ★

| ツール | コメント |
|---|---|
| **Schrödinger Maestro + DESMOND** | 構造構築は GUI 想定、DESMOND の MD 実行は CLI。**MD 部分のみ自動化可**、setup は GUI 操作前提 |
| GaussView | Gaussian の GUI フロントエンド。本体は CLI なので使わなくても運用可 |

### GUI 必須：自動化対象外 ✕

| ツール | 理由 |
|---|---|
| **Materials Studio（BIOVIA）** | 全工程 GUI、scripting API も GUI 起動前提 |
| **Discovery Studio** | 同上 |
| **ChemDraw** | 構造描画専用 GUI（ただし RDKit で SMILES → 構造図は代替可能） |
| **Maestro の GUI workflow** | 構造構築・パラメータ設定が GUI 前提 |

これらを主に使う読者は本書の対象外です。代替として **CLI ベースの同等ツール**（例：Materials Studio → VASP / Quantum ESPRESSO、Maestro → AMBER / GROMACS）への移行を検討すると、方法論を活かせます。

### Playbook 構築の典型パターン

著者の Gaussian / GROMACS / CP2K Playbook で蓄積している知見の例：

- **Gaussian**: `opt=(ts,calcfc,recalcfc=20,maxstep=6)` の Hessian 陳腐化対策、`stable=opt` の別ジョブ分離、modredundant freeze の書式
- **CP2K**: `EPS_SCF` と `MAX_SCF` の経験則、`NVT NOSE` thermostat の周波数設定、`EXT_RESTART` の chk 復元
- **GROMACS**: `mdp` の cutoff scheme、温度制御、ensemble 設定

これらと**同じ書式・運用パターン**で ORCA / VASP / LAMMPS 用の Playbook を構築できます。Phase 2（2026-06）以降、読者と共同で各ツールの Playbook を育てる予定です。

---

## 論文執筆環境対応状況

論文執筆環境の二大巨頭は **LaTeX** と **Word**。AI 共著（推敲・引用整合性・用語統一・査読対応）の実装パスは大きく異なります。

### 環境別の自動化適性

| 環境 | AI 共著の実装パス | 自動化適性 | コメント |
|---|---|---|---|
| **LaTeX**（.tex + BibTeX）★ 著者環境 | テキスト直接編集 | ★★★ | AI 共著に最適。git で diff/merge も自然 |
| **Word**（.docx） | Pandoc 経由 / python-docx 直接 / Microsoft Graph API | ★★ | 3 つの実装パス。用途で使い分け |
| **Google Docs** | Drive API / Docs API | ★★ | クラウド共同編集の延長で AI 取り込み |
| **Markdown ハブ** | Pandoc / Quarto で出力時に LaTeX or Word 変換 | ★★★ | 中立フォーマット、両ジャーナル投稿規定に対応 |

### LaTeX が AI 共著に最適な理由

- すべてプレーンテキスト（`.tex` / `.bib` / `.cls`）
- git で diff / merge / blame ができる
- AI が直接編集・推敲・引用挿入・スタイル調整を扱える
- 投稿先ごとの class file（cls/sty）も AI が解析・対応可能

### Word での AI 共著：3 つの実装パス

#### パス 1：Pandoc 経由（最も汎用）

```
.docx ──pandoc──→ markdown ──AI が編集──→ markdown ──pandoc──→ .docx
```

- **利点**: 任意の AI CLI / 環境で使える、シンプル
- **制約**: 複雑な書式・脚注位置・コメント・トラック変更は変換時に失われる
- **推奨**: 文章本体の**推敲・構造編集**。最終フォーマットは Word 側で仕上げる運用

#### パス 2：python-docx 直接操作

- AI に Python スクリプトを書かせて `.docx` を直接読み書き
- **利点**: 書式・スタイル保持、コメント追加、トラック変更も扱える
- **制約**: 各操作にスクリプトを書く必要、Pandoc 経由より工程多
- **推奨**: **査読対応・ツール化・定型処理**（用語統一の一括置換、フォーマット強制など）

#### パス 3：Microsoft Graph API + Office Scripts

- クラウド OneDrive 上の `.docx` を AI から直接編集
- **利点**: 共同編集中の AI 介入、最も「共著」に近い体験
- **制約**: Microsoft 365 サブスクリプション + OAuth セットアップが必要
- **推奨**: 真のリアルタイム AI 共著、共著者が複数いる原稿

### 引用管理ツールの対応

| ツール | LaTeX | Word | AI 連携 |
|---|---|---|---|
| **BibTeX / BibLaTeX** | ◎ 標準 | △ Pandoc 経由 | ★★★ プレーンテキスト、AI が直接読み書き |
| **Zotero**（+ Better BibTeX） | ◎ | ◎ プラグイン | ★★ API + Web Library |
| **Mendeley** | ◯ プラグイン | ◎ プラグイン | ★★ API あり |
| **EndNote** | △ BibTeX 出力可 | ◎ 標準 | ★★ レガシーだが Word ユーザーに普及 |

### 推奨フロー

| パターン | 構成 | 向いている読者 |
|---|---|---|
| **LaTeX 派** | .tex を AI と直接編集 + BibTeX | 物理化学・理論化学・材料科学・計算化学系 |
| **Word 派（推敲中心）** | .docx → md（Pandoc）→ AI 推敲 → .docx | 文章の論理構成・パラグラフ推敲が主目的 |
| **Word 派（書式保持）** | python-docx で AI に編集スクリプト書かせる | 査読対応、用語統一、定型処理が必要な時 |
| **Markdown ハブ** | AI と md で書き Pandoc / Quarto で出力 | 投稿先未定、または LaTeX / Word 両ジャーナルに投稿候補 |

### 結論

**Word 環境は対応可能**ですが、LaTeX より一段手間が増えます。それぞれの実装パスを Phase 2 で章立てて配布する予定（Pandoc 経由のサンプルスクリプト、python-docx の典型レシピ、Microsoft Graph API のセットアップ手順など）。

---

## ステータス

**Phase 1（2026-05-10）作成**。各ツールの最新仕様は Phase 2 開始時（2026-06）に再 verify します。
