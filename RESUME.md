# 再開ポイント — 2026-05-09 凍結解除

> 次回このプロジェクトを再開するときは、まずこのファイルを読んでください。

## 現在のステータス

- **フェーズ**: Phase 1（MVP 検証）に移行
- **凍結期間**: 2026-04-29 〜 2026-05-09（**ユーザー判断で前倒し解除**、DC2 提出は 2026-05-13 のまま並走）
- **直近の作業**: 専用 Web ページ（Astro Starlight）構築開始

## ここまでに決まったこと（2026-05-09 更新）

1. **商品コンセプト**：化学者向けの AI エージェント活用法商材「Chemist AI Workflow」（仮）
2. **ターゲット顧客**：化学・材料・実験系研究者（D 生・PD・若手 PI）
3. **設計方針**：**Claude Code 重視 + CLI 中立**。優先順位を明示：
   - **Tier 1（premium・最重要）**: Claude Code（Skills/Hooks/Sub-agents/MCP フル活用）
   - **Tier 2（次点）**: Codex CLI（OpenAI 派・AGENTS.md ベース）
   - **Tier 3（無料枠アピール）**: Gemini CLI（OSS / Apache 2.0 / 個人 Google アカウント連携で大幅な無料枠）★ 2026-05-09 追加
   - **Tier 4（最小）**: ChatGPT / Gemini Web 版（ブラウザのみ、CLI 中立性担保のため残す）
4. **差別化**：化学特化（Gaussian/GROMACS/IR/NMR 等）＋ ユーザー自身が日常運用している `.company/` 8 部署の実働システムをテンプレート化
5. **Web ページ**：Astro + Starlight で `~/lab/spring/chemist-ai-workflow/web/` に構築。LP + ドキュメントの統合サイト
6. **棚上げ中の論点**：価格、販売チャネル（note / Zenn Book / 自前 Stripe）、商品名は仮、デプロイ先（Cloudflare Pages / Vercel / GitHub Pages）

## Google 系 AI エージェントの調査結果（2026-05-09）

| 製品 | ポジション |
|---|---|
| Gemini CLI | OSS のターミナル native エージェント。**Claude Code / Codex CLI の直接対抗**。無料枠厚い（個人 Google アカウントで Gemini 2.5 Pro / 60 rpm / 1000 rpd 程度） |
| Jules | GitHub 連携の async coding agent。Codex web 相当 |
| Gemini Code Assist | IDE 拡張。Copilot 寄り |

→ 教材は **Claude Code / Codex CLI / Gemini CLI の御三家 + Web 最小版** で構成。

## 再開時にまず確認すべきファイル

| ファイル | 役割 |
|----------|------|
| `~/lab/spring/chemist-ai-workflow/README.md` | プロジェクト全体像・ポジショニング |
| `~/lab/spring/chemist-ai-workflow/docs/concept.md` | 設計方針・差別化・やらないこと |
| `~/lab/spring/chemist-ai-workflow/docs/roadmap.md` | Phase 0〜4 の詳細 |
| `~/lab/.company/CLAUDE.md` | 「主要プロジェクト」テーブルに登録済み |
| `~/lab/.company/secretary/notes/2026-04-29-decisions.md` | 立ち上げ意思決定ログ |
| `~/.claude/projects/-Users-neoueda-lab/memory/project_spring_chemist_ai_workflow.md` | auto-memory 子ファイル（次セッション自動参照） |

## 再開時の最初の 4 アクション（Phase 1 起動チェックリスト）

DC2 提出が確定したら、以下を順に着手：

1. **顧客ヒアリング 3〜5 名**（化学系 D 生・PD・若手 PI に「研究で AI どう使ってる？」「論文 DB と計算管理が AI で回ったらいくら払う？」を聞く）
2. **競合調査**（note / Zenn / Udemy / 海外）— `search-first` スキルで実施
3. **自分の時短ログ取得**：`.company/` 運用での実時短を case-studies/ に記録開始
4. **章立てラフ**を `content/core/outline.md` に起こす

期限はいずれも 2026-05-末。

## 凍結中の運用ルール

- 本プロジェクトに関する**新規作業は行わない**
- アイデアが出たら `~/lab/.company/secretary/inbox/YYYY-MM-DD.md` に投げ込むだけ
- 関連ファイルの編集はしない（誤って章立てを書き始めない）

## 関連メモリ

- `MEMORY.md` のインデックスから `project_spring_chemist_ai_workflow.md` を辿れる
- 学振 DC2 の最優先タスクは `~/lab/.company/secretary/todos/YYYY-MM-DD.md` に常駐
