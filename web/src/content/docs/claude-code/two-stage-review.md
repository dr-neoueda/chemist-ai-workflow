---
title: Claude + Codex 二段レビュー（応用編）
description: 構文・DRY と物理意味論の役割分担 ── AI エージェント運用に慣れてきたら
---

:::caution[応用編]
本ページは **AI エージェント運用にある程度慣れた読者向け**です。Claude Code 初心者は最初は読み飛ばして、日常運用が定着してから戻ってきてください。複数の AI を組み合わせる前に、まずは Claude Code 単独での部署運用に慣れることを優先します。
:::

AI エージェントの分業運用にある程度慣れてきた段階で取り入れたいのが、**Claude と Codex の二段レビュー**パターンです。両 AI のレビュー観点が異なるため、片方だけでは検出できないバグが補完されます。

## なぜ二段か

| AI | 得意なレビュー観点 |
|---|---|
| **Claude python-reviewer** | PEP 8、型ヒント、DRY、構文、セキュリティ、コード品質 |
| **Codex review** | 物理化学の意味論、計算スキームの整合性、数式の項抜け、化学構造の正しさ |

両者は実質「異なる訓練データ + 異なる reasoning patterns」を持っているため、**独立した目** として機能します。片方が見逃したものをもう片方が拾う、という補完関係が経験的に成立。

## 実例 1：Widom 式の `-RT` 項抜け（Codex が検出）

paper-register skill で生成した md 要約に、Widom 自由エネルギー式 `[Σ ΔEi exp(-ΔEi/RT)] / [Σ exp(-ΔEi/RT)]` から末尾 `-RT` 項が抜けていることを **Codex が検出**。Claude python-reviewer は構文上の問題なしと判定していた。Notion 登録前に補正できた。

## 実例 2：双極子方向反転（Claude python-reviewer が検出）

教育スライド生成で `fig_bonds()` の O-H 結合の δ+/δ- ラベル方向が反転（O が δ+、矢印が O→H）。**Claude python-reviewer がロジックバグとして検出**。Codex は構造的には問題なしと判定していた。

## 実例 3：Gaussian SCF の盲点（Codex が検出）

Gaussian biradical TS opt の input に対して、Claude は構文的に妥当と判定。**Codex が「`opt=(ts,...)` と `stable=opt` を同一ジョブにすると l1.exe で即 Error termination する」と物理的妥当性を指摘**。

## 標準フロー

```
Python ファイル Edit
  ↓
Claude python-reviewer
  ↓ HIGH/CRITICAL があれば修正
Codex review（codex exec で起動）
  ↓ HIGH/CRITICAL があれば修正
記録: ~/lab/.company/review/code-reviews/YYYY-MM-DD-<target>.md
```

著者環境では `~/lab/CLAUDE.md` の「ECC 自動発動プロトコル」で `.py` Edit 直後に PR ループが自動起動するように設定。

## セットアップ

- **Claude reviewer**: `~/.claude/agents/python-reviewer.md` を配置
- **Codex CLI**: 別途インストール、`codex exec` で起動
- **Hook**: PostToolUse で Edit を検出 → 二段レビュー起動（[Hooks](/claude-code/hooks/) 参照）

## 役割分担の典型パターン

複数のレビュー結果を集約した時、以下のような役割分担が浮かび上がる：

| カテゴリ | 検出主体 | 例 |
|---|---|---|
| 構文・コード品質 | Claude python-reviewer | PEP 8 違反、型ヒント不足、DRY 違反 |
| ロジックバグ | Claude python-reviewer | 座標計算の方向反転、boundary 条件 |
| 化学物理意味論 | Codex | 数式の項抜け、規約矛盾、計算スキーム不整合 |
| 視覚的妥当性 | Claude（PNG 視覚確認） | 描画された分子構造の正しさ |

→ 3 者すべて（Claude reviewer / Codex / Claude 視覚確認）を経て、初めて教育的・科学的に正しい状態に到達する場面もある。

## 詳細

各レビュアーの prompt 設計、レビュー結果の記録フォーマット、HIGH 残しでの完了禁止ルールなどは **Phase 2 教材本編**で配布予定。

## 次のステップ

- [Tier 2: Codex CLI](/codex-cli/) — 二段レビューの相方となる実装
