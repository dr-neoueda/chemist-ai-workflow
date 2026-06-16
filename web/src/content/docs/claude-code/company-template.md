---
title: office/ 部署テンプレート
description: 著者の実働システムを再現可能なテンプレートとして配布
---

著者が日常運用している `office/` 部署システムの構造を、再現可能なテンプレートとして提供します。

## 部署構造の概要

```
office/
├── CLAUDE.md             ← 全部署共通のルール
├── secretary/            ← 窓口・TODO・壁打ち・意思決定
│   ├── CLAUDE.md
│   ├── inbox/
│   ├── todos/
│   └── notes/
├── research/             ← 文献調査
├── engineering/          ← Python ツール開発
├── computation/          ← 計算ジョブ管理 + Playbook
│   ├── jobs/
│   ├── parameters/
│   └── playbooks/
├── analysis/             ← データ解析
├── writing/              ← 論文執筆
├── review/               ← コード/計算レビュー
└── presentation/         ← スライド生成
```

著者は現在 8 部署で運用していますが、**これは固定スキーマではなく一例**。最小 1〜2 部署から始めて段階的に増やすことも、最初から多部署で運用することもできます。

## 部署 CLAUDE.md の典型構造

各部署は独立した `CLAUDE.md` を持ち、自部署の運用ルール・参照ファイル・出力先を明示します：

```md
# 計算管理部

## 役割
量子化学計算（Gaussian / ORCA など）、古典 MD（GROMACS / AMBER など）、
周期系 DFT（CP2K / VASP など）のジョブ管理と Playbook 蓄積。

## 自動運用ルール
- 計算 log を解析したら必ず playbooks/<tool>.md に Lessons Learned を追記
- 失敗ジョブは jobs/YYYY-MM-DD-*.md に記録
- 入力テンプレ生成時は最新 Playbook を参照

## 参照ファイル
- ../secretary/notes/ ← 直近の意思決定
- ./parameters/ ← 計算パラメータの集約
- ./playbooks/ ← ツール別ノウハウ
```

## 部署間連携

- **窓口は秘書部のみ**：ユーザーは secretary に話しかけ、secretary が他部署に振り分ける
- **状態はファイルベース**：意思決定は `notes/`、TODO は `todos/`、ノウハウは `playbooks/` に蓄積
- **同日 1 ファイル**：`YYYY-MM-DD.md` を Read → Edit append（並行セッションでの上書きを防ぐ）

## 拡張可能性

新設・分割・統合の判断基準（Phase 2 で詳述予定）：

- 同種のタスクが 2 回以上繰り返されたら部署候補
- 1 部署が 3 種以上のタスクを抱えたら分割候補
- 部署間の依存が強すぎたら統合候補
- 新しい研究テーマ（例：MLIP 部、結晶解析部）が立ち上がったら必要に応じて新設

## 配布物（Phase 2 以降）

- `office/` テンプレートリポジトリ（git clone で即運用開始）
- 部署別 CLAUDE.md のサンプル集
- 部署追加・分割の判断フローチャート
- 自動運用ルールのレシピ集

## 次のステップ

- [応用：化学研究での実例](/claude-code/application/) — 部署システムの実運用例
- [Claude + Codex 二段レビュー（応用編）](/claude-code/two-stage-review/) — AI エージェント運用に慣れてからの上級パターン
