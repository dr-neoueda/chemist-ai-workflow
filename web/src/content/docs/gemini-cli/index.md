---
title: "Gemini CLI（OSS・caw 対応）"
description: OSS / Apache 2.0 のターミナル native エージェント。caw 利用には有料 API キーが前提（無料枠は限定的）
---

:::caution[実地での注意（テスト運用で判明）]
Gemini CLI の**無料枠は caw を動かすには不十分**でした — API キーが必須で、割り当ても少なく、**オンボーディング（初期環境構築）すら完了できない**ケースがありました。caw を試すなら **Codex CLI / Claude Code を推奨**します。Gemini CLI を使う場合は**有料 API キー**を前提にしてください。
:::

## なぜ Gemini CLI を扱うか

- **OSS（Apache 2.0）**：ソースコードが公開されており、内部挙動を確認できる
- **無料枠はあるが caw には不十分**：個人 Google アカウントで Gemini 2.5 Pro クラスを 60 req/min・1000 req/day 程度。ただし実地（テスト運用）では caw のオンボーディングが完了せず、**有料 API キーが前提**
- **Claude Code / Codex CLI と同系統**：ターミナル native エージェントの選択肢として並び立つ
- OSS でソースが追える選択肢（ただし **caw を回すには有料 API が必要**＝無料枠だけでは厳しい）

## 章立て（執筆中）

1. Gemini CLI セットアップ
2. 個人 Google アカウント連携と無料枠の使い切り戦略
3. AGENTS.md 風のルールファイルを Gemini CLI に効かせる
4. Claude Code / Codex CLI との機能比較表
5. 化学計算系の実例（PDF 解析、log ファイル要約）
6. 「無料枠で回せる範囲」の見極め

## 関連 Google プロダクト（参考）

- **Jules**：GitHub 連携の async coding agent。Codex web 相当
- **Gemini Code Assist**：IDE 拡張（VS Code / JetBrains）。Copilot 寄り

→ 本書では **ターミナル native の Gemini CLI** を主に扱う。

## caw の導入（Gemini CLI 版）

caw は Gemini CLI の **extension** として提供している（`gemini-plugin/`、version 1.0.0）。

```bash
gemini extensions install https://github.com/dr-neoueda/chemist-ai-workflow
```

導入後、プロジェクトフォルダで `gemini` を起動し、`/caw` または「環境を作って」と話しかけるとオンボーディングが始まる。Gemini CLI には hooks（bash）が無いため、**Windows でも Git Bash は不要**。

Gemini CLI は「説明文で skill を自動発火」する仕組みを持たないため、caw 本体（秘書・両トラックのオンボーディング・ディスパッチ・統合 inbox の自動仕分け・各スキル手順）を**単一の `GEMINI.md`（常時ロード）に集約**し、`commands/*.toml`（`/caw-*`）も併設している。プロジェクト設定は `office/GEMINI.md`。メソッド・成果物の二層原則・統合 inbox は Claude Code / Codex CLI 版と共通。

## ステータス

**caw 対応済み（Gemini extension 1.0.0）**。最新仕様は提供元（Gemini CLI）の更新時に再 verify する。
