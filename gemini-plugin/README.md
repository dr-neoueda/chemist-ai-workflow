# caw — Gemini CLI 版

> ## ⛔ この版は凍結中です（非推奨）
>
> **Gemini CLI の無料枠では caw のオンボーディングすら完走できません**（2026-06-19 のテストユーザー会で実地に判明）。
> API キーが必須で無料枠の割り当てが少なく、caw を使い始める前に枠を使い切ります。実用には**有料 API が前提**です。
>
> **2026-08-21 に凍結しました。** 以後、本体（Claude Code / Codex CLI / Copilot CLI 版）の変更をこの版に追従させません。
> バージョンも 1.49.0 で据え置きます。凍結の経緯・解除条件は [`FROZEN.md`](./FROZEN.md) を参照してください。
>
> **推奨：Codex CLI（本命）／ Claude Code（次点）／ Copilot CLI（企業向け）** のいずれかをお使いください。

[Chemist's AI Workflow（caw）](https://github.com/dr-neoueda/chemist-ai-workflow) の **Gemini CLI 版**。研究プロジェクト（化学者向け）と就活の 2 トラックに対応した AI 部署システムを、Gemini CLI の **extension** として提供する。

## Claude Code / Codex CLI 版との違い

| | Claude Code 版（`plugin/`） | Codex CLI 版（`codex-plugin/`） | Gemini CLI 版（`gemini-plugin/`） |
|---|---|---|---|
| 形式 | プラグイン（skills/） | プラグイン（skills/） | extension（`gemini-extension.json` + `GEMINI.md` + `commands/`） |
| プロジェクト設定ファイル | `office/CLAUDE.md` | `office/AGENTS.md` | `office/GEMINI.md` |
| スキルの発火 | 自然言語で自動発火 | 自然言語で自動発火 | **常時ロードの `GEMINI.md`** で振る舞いを定義（自然言語 OK）＋ `/caw-*` コマンド |
| hooks | あり（bash） | なし | なし |

Gemini CLI はスキルを「説明文で自動発火」する仕組みを持たないため、caw 本体（秘書・オンボーディング・ディスパッチ・各スキル手順）を**単一の `GEMINI.md`（常時ロード）に集約**し、明示コマンド（`commands/*.toml`）も併設している。メソッド・成果物の配置（二層原則）・統合 inbox の自動仕分けは 3 CLI 共通。

## 導入

```bash
gemini extensions install https://github.com/dr-neoueda/chemist-ai-workflow
```

（ローカルから入れる場合は `gemini extensions install --path=./gemini-plugin`。更新は `gemini extensions update`。）

導入後、プロジェクトフォルダで `gemini` を起動し、`/caw` または「環境を作って」と話しかけるとオンボーディングが始まる。

## できること

研究：文献検索（`/caw-research`）・文献登録（`/caw-register`）・論文/申請書執筆（`/caw-write`）・計算入力（`/caw-input`）・スライド/図（`/caw-slides`）・計算ノウハウ蓄積（`/caw-playbook`）・データ解析（`/caw-analyze`）。
就活：企業/業界研究（`/caw-research`）・ES（`/caw-es`）・面接対策（`/caw-interview`）・募集/締切収集（`/caw-events`）。
共通：環境整備（`/caw-setup`）・過去資料の取り込み・自動仕分け（`/caw-intake`、統合 `inbox/`）・構造点検（`/caw-doctor`）・動作レポート（`/caw-report`）。

## データの扱い

Gemini CLI は Google のクラウド上のモデルで動くため、読み取った内容は処理のため送信される。未公開データ・他者の個人情報・秘匿情報は入力しないこと。学習利用の可否は各自の Google アカウント／Gemini の設定に従う。
