---
title: Sub-agents
description: Codex CLI の sub-agent 機能。並列調査・並列レビューの組み方、Claude Code Sub-agents との対応、化学研究での活用例
---

Codex CLI も **sub-agent**（子エージェント）を起動でき、調査・コード生成・レビューを並列で分担できます。Claude Code の Sub-agents と概念は似ていますが、エコシステムの厚みと UI 統合度に違いがあります。本ページでは Codex の sub-agent の使い方、並列実行パターン、Claude Code Sub-agents との対応を整理します。

## Sub-agent とは

Codex における sub-agent は、**親エージェントとは独立した context window** で動く子プロセス。親が「調べ物を 2 件並列で投げる」「コード生成と review を分担させる」といった用途で使えます。

主な特徴：

- 親 context を圧迫せず、結果サマリだけが親に返る
- 複数 sub-agent を並列起動できる
- 子は独立した system prompt / instruction で起動できる
- 完了後に親が結果を集約

## いつ Sub-agent を使うか

1. **長い調査結果が context を圧迫しそうな時** — 子に投げてサマリだけ受け取る
2. **独立した複数タスクを並列化したい時** — 例：論文 A の要約と論文 B の要約を同時に
3. **役割を分けたい時** — 例：generator と reviewer
4. **重い処理を非同期化したい時** — 親は別作業を続けつつ子の完了を待つ

## 並列調査の実例

著者環境（2026-05-14 検証）：Codex CLI で 2 つの sub-agent を並列起動し、別々の調査トピックを処理。両方の結果サマリが親 context に返り、context window を圧迫せずに統合議論が可能でした。

具体例（プロンプト擬似コード）：

```
codex
> 以下の 2 つを並列で調査して、それぞれサマリを返してほしい：
>   1. MACE-OFF foundation model の最新バージョンと特徴
>   2. CP2K の MLIP integration の現状

> 2 つの sub-agent を起動して結果をマージ
```

Codex は内部で 2 つの子エージェントを spawn し、それぞれが独立に web 検索・要約を実行。完了後にサマリが親 context に返ります。

## Claude Code Sub-agents との対応

| 観点 | Claude Code | Codex CLI |
|---|---|---|
| 専用 context window | あり | あり |
| 並列起動 | あり（Task tool で複数同時呼び出し） | あり |
| 役割の事前定義 | `~/.claude/agents/<name>.md` で定義可能、コミュニティ製プリセット豊富 | プロンプトで動的に役割指定。プリセット集は Claude Code エコシステム（`everything-claude-code` 等）と比べて少ない |
| 専用 tool 制限 | agent ごとに使える tool を絞れる | 同等の細粒度制限は弱め |
| エコシステム規模 | `code-reviewer` / `tdd-guide` / `planner` / 言語別 reviewer など 30+ 種類が流通 | 公式 + 少数 OSS |

**実用上の差**：

- 入門〜中級の研究者運用（並列調査・並列要約・並列レビュー）では **ほぼ同等**
- ECC の `python-reviewer` + `codex:review` 二段レビューのような **役割を細かく分担した自動パイプライン** を組む場合は、Claude Code の方が既製プリセットの厚みで有利
- ただし Codex 側でも `caw-review` / `caw-search` のような sub-agent をプラグイン経由で配信することは可能（[配布プラグイン（caw）](/plugin/)）

## 化学研究での活用パターン

### パターン 1: 文献の並列要約

```
> 以下 3 本の論文を別々の sub-agent で要約して：
>   - papers/wang-2024.pdf
>   - papers/zhao-2025.pdf
>   - papers/lin-2025.pdf
> それぞれ <title / authors / key finding / 自分のテーマとの関連> を md で返す
```

各 PDF を子エージェントが独立に処理。親 context は要約 3 件分のみで済む。

### パターン 2: 計算ログの並列解析

```
> 並列で：
>   - sub-agent A: Gaussian log（job_001.log）の SCF 収束 + 振動数解析
>   - sub-agent B: ORCA out（job_002.out）の同等項目
> 両者の比較表を最後に作って
```

異なる計算ソフトの出力を独立に解析させ、最後に親で merge。

### パターン 3: コード生成 + レビュー（二段レビューの Codex 内完結版）

```
> sub-agent A に MDAnalysis で trajectory 解析スクリプトを書かせて、
> sub-agent B（reviewer 役）に物理意味論レビューさせる。
> 両者の出力を親で受けて、reviewer 指摘を generator に反映
```

Claude + Codex 二段レビューを Codex 単体で簡易に再現できます（ただし観点の独立性は両 CLI 併用の方が高い。詳細は [Claude + Codex 二段レビュー（応用編）](/claude-code/two-stage-review/)）。

### パターン 4: 並列文献探索

```
> 並列で異なる検索エンジンに投げて：
>   - sub-agent A: arXiv で "MACE force field" 最近 30 日
>   - sub-agent B: Crossref で同キーワード
>   - sub-agent C: Semantic Scholar で同キーワード
> 重複を除いて統合リストを作って
```

検索ソース別の差分を効率的に把握できる。

## Sub-agent を効果的に使うコツ

### 子に渡すタスクは独立であること

並列化のメリットは「依存しない」タスクで最大化される。A の結果を B が使う場合は **直列実行**が正しい（並列にすると B は A の結果を待てない）。

### 子に与える指示は self-contained

子は親の会話履歴を見られない。**必要なファイルパス・前提・期待する出力フォーマットを明示**して渡す。

```
# 悪い例
> サブエージェント A：例の log を解析して

# 良い例
> サブエージェント A：~/lab/cp2k/aabradox/run01/out.log を読み、
> SCF 収束ステップ数 + 最終エネルギー（kJ/mol）+ 警告メッセージ を md で返して
```

### 結果サマリのフォーマットを指定する

子の出力フォーマットが揃っていないと親側でのマージが面倒。**結果は md table で / 結果は JSON で** など明示する。

## 注意事項

- **Sub-agent が独自に MCP 接続を持つ場合**：認証情報の経路が親と異なることがある。`~/.codex/config.toml` の `[mcp.servers]` 設定は子にも継承される
- **API コスト**：sub-agent も親と同じく LLM 呼び出しを発生させる。並列度を増やすほどトークン消費は線形に増える
- **失敗時の reporting**：子のエラーは親に伝わるが、詳細スタックトレースは省略されることがある。重要な処理は子内部で try/except + 詳細ログ保存を仕込む

## 次のステップ

- [Skills](/codex-cli/skills/) — sub-agent の発火を Skills 内に組み込む
- [Commands](/codex-cli/commands/) — sub-agent 起動を明示的な Command として運用する
- [Claude + Codex 二段レビュー（応用編）](/claude-code/two-stage-review/) — Codex sub-agent と Claude Code sub-agent を CLI 横断で組み合わせる上級パターン
