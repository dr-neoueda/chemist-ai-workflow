---
title: プロジェクト概要
description: Chemist's AI Workflow の背景・ポジショニング・差別化・やらないこと
---

## 商品の核

**研究業務を「AI 部署」に分割し、ファイルベースで状態管理する**方法論。

AI エージェントを単発のチャットツールとして使うのではなく、研究プロセス全体を支える基盤として運用するための、化学者向けの体系的メソッドです。

## 設計方針：CLI 中立 + 主軸 2 本柱

| レイヤ | 中立性 | 内容 |
|--------|--------|------|
| 核：方法論 | OS / CLI 中立 | 部署設計、ファイル構造、運用ルール、品質ゲート |
| 主軸 A：Claude Code 版 | Anthropic 専用 | Skills / Hooks / Sub-agents / MCP フル活用。著者の常用環境で検証密度が最も高い |
| 主軸 B：Codex CLI 版 | OpenAI 専用 | Skills（自然言語マッチ）/ Commands / Sub-agents / MCP に対応。AGENTS.md ベースで Claude Code 版と機能パリティ |
| 補助 C：Gemini CLI 版 | Google 専用 | OSS / Apache 2.0、個人アカウントで無料枠 |
| 補助 D：ChatGPT/Gemini Web 版 | ブラウザのみ | 単一プロンプトに圧縮した最小版 |

→ Claude Code と Codex CLI を **同格の主軸** として並列配信。研究室で派閥が分かれても共通の `office/` メソッドで運用でき、ベンダーロックインリスクを回避。

## 差別化ポイント

1. **化学者特化の事例**：量子化学計算（Gaussian, ORCA, Psi4 等）、古典 MD（GROMACS, AMBER, LAMMPS 等）、周期系 DFT（CP2K, VASP, Quantum ESPRESSO 等）、IR / NMR / XRD 解析、結晶相反応、論文執筆を実例で扱う
2. **計算ソフトに依存しない方法論**：著者の使用ソフトは Gaussian / GROMACS / CP2K だが、Playbook と部署設計は**任意の計算化学ソフトに対応可能**な抽象度で設計
3. **実働システム由来**：著者が 2026 年から日常運用している `office/`（現在 8 部署）の実物を再現可能テンプレートとして提供。部署は固定ではなく、研究テーマや業務に応じて**追加・分割・統合**できる設計
4. **ベンダーロックインを避ける設計**：Anthropic でも OpenAI でも Google でも回せる
5. **段階的に学べる構成**：Claude Code 未経験者向けのセットアップから、AI エージェント分業運用に慣れた読者向けの応用編まで、章を追って深められる構成。TDD・search-first・段階的検証など実運用ノウハウを含む

## 競合・隣接商品との棲み分け

- **Anthropic 公式 docs / Claude Code skills repo**：無料・汎用。差別化＝化学特化＋方法論統合
- **note / Zenn の "Claude Code 活用法" 記事群**：単発 Tips が多い。差別化＝体系化された方法論
- **Andrej Karpathy 等の海外 AI tutorial**：英語・ソフトウェアエンジニア向け。差別化＝日本語・実験系研究者向け
- **ChemBERTa / DeepChem 等の AI for Chemistry**：研究内容の AI 化（物性予測等）。本商品は **業務プロセスの AI 化** で完全棲み分け

## やらないこと（YAGNI）

- 自前 LLM の学習・ファインチューニング
- 化学分野固有の AI モデル比較・性能評価
- IDE プラグインや GUI ツールの開発
- 一般プログラマ向けへの拡張（化学者特化を維持）

## 運営

- **オーナー**：上田（電気通信大学 SPRING）
- **設置場所**：`~/lab/spring/chemist-ai-workflow/`
- **ステータス**：Phase 1（MVP 検証）2026-05-09 〜
