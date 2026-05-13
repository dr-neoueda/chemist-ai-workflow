---
title: "Tier 2: Codex CLI（次点）"
description: OpenAI 派の選択肢。AGENTS.md ベースで Claude Code 同等のワークフローを再現
---

## なぜ Codex CLI を次点に置くか

- OpenAI のフラッグシップモデル（GPT-5 系）を活用できる
- **AGENTS.md** という標準でプロジェクトルールを記述
- Claude Code とは違うレビュー観点が得られる（**Claude = 構文 / DRY、Codex = 物理意味論** という棲み分けの実例あり）
- Anthropic 単独依存リスクの回避策として最有力

## 章立て（執筆中）

1. Codex CLI セットアップ
2. `AGENTS.md` の書き方 — Claude Code の `CLAUDE.md` との対応
3. ルールの記述方法と粒度
4. Claude Code との二段レビュー連携（応用編）
5. `.company/` テンプレートを Codex 用に書き換える
6. 強み・弱み（Claude Code との比較）

## 著者メモ（応用編）

実例：MD 自由エネルギー計算で Widom 式の `-RT` 項抜けを Codex が検出し、ナレッジベース登録前に補正（著者環境では Notion）。構文・DRY は Claude が、物理意味論は Codex が拾うという役割分担が有効。

詳細は [Claude + Codex 二段レビュー（応用編）](/claude-code/two-stage-review/) を参照。AI エージェント運用に慣れてからの導入を推奨します。

## ステータス

**Phase 2（2026-06）執筆予定**。
