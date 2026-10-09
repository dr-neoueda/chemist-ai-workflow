# Chemist's AI Workflow（caw）

> **化学者のための AI エージェント導入伴走** — 電気通信大学 SPRING リカレント・リスキリング商品

**配布版：plugin 1.75.0 / Codex 1.74.0 / Copilot 1.43.0 / Gemini 1.49.0**
現状と次の一手は [`RESUME.md`](./RESUME.md)、変更の全履歴は [`CHANGELOG.md`](./CHANGELOG.md) を参照。

> **プラグイン `caw` は無料です。** 商品はプラグインそのものではなく、化学者が自分の研究に合わせて
> 立ち上げ、使い続けられる状態まで持っていく **マンツーマンの導入伴走** です。
> 詳細は [`docs/concept.md`](./docs/concept.md)。

## これは何か

化学研究プロジェクトのルートで `/caw` と打つと、**9 つの「AI 部署」からなる運営フォルダ（`office/`）と作業フォルダ（`work/`）を対話的に構築**し、以後その構造の上で研究支援を回す **CLI プラグイン**です。

- **秘書部** が TODO・意思決定・学びを 1 日 1 ファイルで蓄積する
- **計算管理部** が Gaussian / ORCA / CP2K / GROMACS 等の入力生成・ジョブ記録・log 解析を担い、罠と処方を **Playbook** に貯めていく
- **文献部** が論文を検索・登録し、**論文執筆部** がそれを引用源に本人の文体で書く
- **プレゼン部** が手描き SVG から**編集可能な PowerPoint** を生成する

単発のチャットではなく、**ファイルシステム上に状態を持つ組織**として AI を運用するのが中核アイデアです。

## インストール

```bash
# Claude Code
> /plugin marketplace add dr-neoueda/chemist-ai-workflow
> /plugin install caw

# 使う
cd ~/your-research-project && claude
> /caw
```

**前提**：`git` と Node.js（LTS）。`marketplace add` は配布元 GitHub を clone するため git が必須です
（macOS は `xcode-select --install`、Windows は Git for Windows）。

対応 OS は **macOS / Windows** を同列にサポート（Hooks のみ Windows では Git Bash / WSL2 を併用）。

## 対応 CLI

| CLI | 位置づけ | 状態 |
|---|---|---|
| **Codex CLI** | **Tier 1（本命）** | 15 スキル。Hooks は移植予定 |
| **Claude Code** | Tier 2 | 15 スキル ＋ Hooks 3 本（Codex 版と byte 一致ミラー） |
| **Gemini CLI** | 参考 | 15 コマンド。**実地検証で「無料枠では初期構築すら完了不可」と判明**（有料 API 前提） |
| **Copilot CLI** | PoC | 2 スキル（`caw` / `caw-setup`）で停止中 |

ベンダーロックインを避ける設計だが、**実用度には明確な差がある**ことを正直に記載しています。

## スキル一覧（15）

### 研究トラック（12）

| スキル | 役割 |
|---|---|
| `/caw` | オンボーディング（研究プロファイル聴取 → 9 部署 + `work/` を一括生成）→ 以後は運営モード |
| `/caw-research` | 関心テーマの論文検索（arXiv / Crossref / Semantic Scholar / OpenAlex / PubMed）→ クリック可能な HTML リスト |
| `/caw-register` | 入手済み PDF → 書誌付き要約 md → ナレッジベース（Notion / Obsidian 等）+ クラウドストレージへ登録 |
| `/caw-write` | 登録済み文献を引用源に、論文・申請書・学会要旨を**本人の文体**で執筆 |
| `/caw-input` | 7 ソフト（Gaussian / ORCA / CP2K / GROMACS / VASP / Quantum ESPRESSO / ChimeraX）の入力雛形 + ジョブ記録 |
| `/caw-playbook` | 計算 log の解析 → Lessons Learned 起案 → Playbook 追記。過去データの一括取り込みにも対応 |
| `/caw-analyze` | 手法非依存の解析コンパニオン（raw → 数値化後の下流定量解析） |
| `/caw-slides` | 発表資料を **SVG-first**（手描き SVG → native DrawingML pptx）で生成。図形・表・数式が PowerPoint で編集可能 |
| `/caw-setup` | 不足している外部ツールを検出し、**1 つずつ理由を説明しながら**導入 |
| `/caw-doctor` | `office/` 構造の健全性チェックと修復提示 |
| `/caw-intake` | 統合 inbox に投げ込まれたものを自動仕分け |
| `/caw-report` | 開発者向けの匿名動作レポート |

### 就活トラック（3）

`/caw-es`（エントリーシート）・`/caw-interview`（面接対策）・`/caw-events`（企業イベント調査）

## リポジトリ構成

```
chemist-ai-workflow/
├── RESUME.md              ← 現状と次の一手（再開時に最初に読む）
├── CHANGELOG.md           ← 変更の全履歴（実質の正典）
├── TESTING.md             ← 第 1 回テスト会の手順書
├── TESTING-slides-handson.md ← 第 2 回（スライド・Windows）の手順書
├── .claude-plugin/        ← marketplace.json（配布エントリ）
├── plugin/                ← Claude Code 版（skills/ 15 + hooks/ 3）
├── codex-plugin/          ← Codex CLI 版（skills/ 15）
├── copilot-plugin/        ← Copilot CLI 版（PoC・skills/ 2）
├── gemini-plugin/         ← Gemini CLI 版（commands/ 15 の .toml + GEMINI.md）
├── docs/                  ← 企画ドキュメント（concept / roadmap / 監査）
├── scripts/               ← check-consistency.sh（配布物の整合性検査）
├── setup/                 ← CLI 自体の導入スクリプト（.sh / .ps1）
├── presentations/         ← caw-slides のテンプレ pptx
└── web/                   ← Astro Starlight ドキュメントサイト（未デプロイ）
```

## 開発

```bash
bash scripts/check-consistency.sh                      # 版一致・mirror byte 一致・個人化リーク検査
uv run --with pytest --with pillow python -m pytest \
  plugin/skills/caw-slides/tests plugin/skills/caw/tests -q   # 125 passed / 4 skipped
```

配布物（`plugin/` `codex-plugin/` `copilot-plugin/` `gemini-plugin/`）を変更したら**該当系統の版を上げ**、
`check-consistency.sh` を通すこと。CI（`.github/workflows/consistency.yml`）が push / PR で同じ検査と Web ビルドを強制します。

## プロジェクト背景

電気通信大学 SPRING（戦略的研究人材育成事業）に採択された博士課程院生は、リカレント・リスキリングに資するツールを各自開発・販売する義務があります。本プロジェクトはその成果物です。

- **対象**：化学・材料・実験系研究者（D 生・PD・若手 PI）
- **差別化**：化学特化の事例 ／ 作者自身が日常運用している 9 部署システムの実物由来 ／ ベンダーロックイン回避 ／ 品質ゲート内蔵
- **役割境界**：組織運営・下流定量解析・執筆/文献/Playbook を担う。**ベンダー GUI 専用ソフトでの対話的な raw データ還元（SCXRD 精密化・XPS 定量・EPR シミュ等）は代替せず外部連携に委ねる**（[`docs/chemistry-coverage-audit.md`](./docs/chemistry-coverage-audit.md)）

詳細は [`docs/concept.md`](./docs/concept.md)、進行状況は [`docs/roadmap.md`](./docs/roadmap.md)。

## ステータス

- **作成日**：2026-04-29
- **現フェーズ**：プラグイン実装は稼働中（テストユーザー会 2 回実施済）。**商品モデルと商品名は 2026-08-21 に確定**、価格・販売チャネル・Web 公開は未着手
- **オーナー**：上田（電気通信大学 SPRING）

## ライセンス

MIT License（[LICENSE](./LICENSE)）
