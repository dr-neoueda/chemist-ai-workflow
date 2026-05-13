---
title: Skills
description: プロジェクト固有のメソッドをバージョン管理可能な単位にする
---

Skills は Claude Code に「プロジェクト固有のメソッド」を教える仕組みです。スラッシュコマンドとして手動で呼び出すことも、トリガーで自動発火させることもできます。

## Skill の最小構成

`~/.claude/skills/<skill-name>/SKILL.md`：

````md
---
name: paper-summary
description: PDF を読み込んで 200 字要約とキーワード 5 つを返す
---

# Paper Summary Skill

入力された PDF パスに対し、以下を実行：

1. `pdftotext` で本文抽出
2. 200 字以内の日本語要約を生成
3. キーワード 5 つ抽出
4. JSON で返す

## 使い方
`/paper-summary /path/to/paper.pdf`

## 出力フォーマット
```json
{ "summary": "...", "keywords": [...] }
```
````

ユーザーが `/paper-summary <path>` と打つと発火します。

## 化学者向けスキルの典型例

| スキル名 | 役割 |
|---|---|
| `gaussian-input-gen` | 化合物名 + 計算レベルから `.gjf` を生成 |
| `gromacs-mdp-template` | 系種類 + ensemble から `.mdp` テンプレを生成 |
| `paper-register` | inbox PDF を Notion + Drive に自動登録（[応用例](/claude-code/application/)で詳述） |
| `playbook-update` | 計算 log を解析して Playbook の Lessons Learned に追記 |
| `application-draft` | 申請書ドラフトを文体プロファイル + 字数制約で起案 |

## Plugin / Marketplace

スキル単体ではなく、関連スキルをまとめた「Plugin」を導入することもできます：

- **everything-claude-code**: 200+ スキルのコレクション（一般用途）
- **公式 Anthropic skills**: 公式サンプル
- **自前 Plugin 化**: ラボ内・大学内での内部配布が可能

## Skills と Hooks の連携で「自動発火」

Skill は手動発火（スラッシュコマンド）が基本ですが、Hooks と組み合わせると **ユーザー指示なしの自動発火** が組めます。著者の `~/lab/CLAUDE.md` の「ECC 自動発動プロトコル」では、12 のトリガー条件で Skill が自動起動します（例：`.py` Edit 直後の PR ループ）。

## Skill の管理ベストプラクティス

- 1 つの Skill は **1 つの役割** に絞る（DRY 違反になりがち）
- frontmatter の `description` は**他の Claude セッションが読んで「これだ」と判定できる粒度**で書く
- 入出力フォーマットを明示（JSON / Markdown / プレーンテキスト）
- 化学固有の knowledge は CLAUDE.md か別の Playbook に分離（Skill 本体は薄く保つ）

## 次のステップ

- [Hooks](/claude-code/hooks/) — Skill を自動発火させる
- [Sub-agents](/claude-code/subagents/) — 並行実行で Skill を多重化
