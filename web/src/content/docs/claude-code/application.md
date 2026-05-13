---
title: 応用：化学研究での実例
description: 文献管理・計算ジョブ・申請書・論文執筆・スライド生成の実運用例
---

著者が `.company/` 部署システム + Claude Code で日常的に運用している実例の概要です。各実例の詳細スクリプト・テンプレ・運用手順は **Phase 2 教材本編**で配布予定。

## 1. 文献管理パイプライン（PDF → md → Drive → Notion DB）

- **入力**: `~/lab/papers/inbox/` に PDF を投げる
- **処理**: paper-register skill が pdftotext / GROBID で本文・メタデータ抽出 → 200 字要約 → タグ付け
- **出力**: Google Drive に PDF アップロード、Notion DB に property（著者・年・誌名・URL・要約・引用関係）登録
- **品質ゲート**：登録前に AI で誤要約・ページ範囲ミスを補正（応用編で詳述）
- **実績**: 2026-04 までで累計 200+ 本、ゼロ失敗で運用

```
inbox/paper.pdf
  ↓ paper-register skill
md/paper.md  +  クラウド upload  +  ナレッジベース登録
```

→ ナレッジベース・クラウドストレージは [対応ツール一覧](/tools/) のマトリクスに従って差し替え可能（Notion → Obsidian + Filesystem MCP など）。

## 2. 計算ジョブ管理（CLI ベースの量子化学・MD・DFT）

- **入力**: 化合物 / 計算レベル / 系の指定
- **処理**: 入力テンプレ + 過去 Playbook（既知の罠と処方）を参照して `.gjf` / `.mdp` / `.inp` 生成
- **submission**: ローカル or HPC（豊橋技科大 SQUID）に bash + qsub
- **解析**: log の Stationary point / 振動モード / SCF 収束 / drift を自動抽出
- **学び循環**: 失敗ジョブは `playbooks/<tool>.md` の Lessons Learned に追記、次回以降の生成テンプレに反映

著者環境は Gaussian / GROMACS / CP2K だが、**CLI ベースの他ソフト**（ORCA, AMBER, LAMMPS, VASP, Quantum ESPRESSO 等）にも同じ Playbook 構造で展開可能（[対応ツール一覧](/tools/)）。

## 3. 学振 DC2 申請書ワークフロー

- **下書き**: 平易な日本語ルール（feedback memory）に従って AI が起案
- **校閲**: 事実整合 / 表現の控えめさ / 引用形式を AI に確認させる（より厳密な確認は応用編の二段レビューパターンで）
- **指導教員添削**: 添削を memory に取り込み、次稿に反映
- **電子申請欄圧縮**: 100 字 / 300 字 / 400 字の文字数制約に再投影

文体プロファイル（指導教員の文体・ターゲット誌のスタイル）を memory に保持して、毎回ゼロから書かない。

## 4. 論文ドラフト編集（LaTeX / Word 両対応）

- **LaTeX 派**: `.tex` / `.bib` を AI と直接編集、git で diff 管理
- **Word 派**: Pandoc 経由で推敲（`.docx` → md → AI → `.docx`）、または python-docx で書式保持して直接編集、Microsoft Graph API でクラウド共著
- **スタイルガイド**: 指導教員の文体プロファイル + 投稿先誌のスタイルを 50 本の参考論文から自動抽出
- 詳細な実装パスは [対応ツール一覧](/tools/)

## 5. プレゼン部のスライド生成（Codex 委譲）

- **Claude が source 設計**（教えたい順序・L1 案・視覚要素・禁止事項）
- **Codex が実装**（python-pptx スクリプト、matplotlib 図、レイアウト調整）
- **Claude が独立検証**（shape 矩形交差ゼロ、フォント統一、L1 各 1 個）
- **PNG 視覚確認**で化学物理の意味論バグも検出（実例：水分子の中央元素が H/O 入れ替わって描画されたケース）

## 6. 高校生向け教育コンテンツ生成

授業向けの「分子の極性 → 溶媒 → TLC・カラム」までの教育スライド生成にも同じ部署システムが応用可能。教育的に正しい図表を生成するための視覚的検証を組み込みます。

## 各実例の詳細

各パイプラインの完全なスクリプト・テンプレ・運用手順は **Phase 2（2026-06 開始）の教材本編**で配布予定です。

## 次のステップ

- [Claude + Codex 二段レビュー（応用編）](/claude-code/two-stage-review/) — AI エージェント運用に慣れてきたら取り入れたい品質ゲート
