# Codex 委譲プロンプトテンプレ集（v2: 完全お任せ）

スライド作成を `codex exec` 経由で Codex に委譲するときのプロンプトひな形。

**v2 方針**: 構成・L1 メッセージ・視覚デザインの裁量はすべて Codex に渡す。Claude は元データと最低限の要件（場面・言語・制約）のみ渡し、計画メモは Codex 自身が書く。

## 共通の呼び出し形

`codex exec` はプロンプトを引数で受け取っても **stdin が開いていると追加入力を読みに行ってハングする**（過去に約 17 分停止を実測した事故あり）。**必ず `</dev/null` で stdin を閉じる**。

### 推奨形（プロンプトをファイル経由）

```bash
# プロンプトを一時ファイルに書く
cat > /tmp/codex_prompt.txt <<'EOF'
<プロンプト本体>
EOF

codex exec --full-auto --skip-git-repo-check -C <project_root> "$(cat /tmp/codex_prompt.txt)" </dev/null
```

### 短い指示の簡易形

```bash
codex exec --full-auto --skip-git-repo-check -C <project_root> "<短いプロンプト>" </dev/null
```

### 禁止形（過去にハングした）

```bash
# stdin を閉じていないため "Reading additional input from stdin..." で停止する
codex exec --full-auto --skip-git-repo-check -C <project_root> "$(cat <<'EOF'
<プロンプト本体>
EOF
)"
```

`<project_root>/office/presentation/AGENTS.md` および `<project_root>/AGENTS.md` は Codex が cwd 起点で自動ロードする。

---

## テンプレ汎用版（推奨ベース）

```
<project_root>/office/presentation/AGENTS.md と <project_root>/AGENTS.md のスタイルガイドに厳密に従って、
研究発表用 PowerPoint スライドを生成してください。

## 元データ
<元データのパスまたは貼り付け本文>

## 発表場面・要件
- 場面: <報告会 / 国内学会 / 国際学会 / 研究紹介 / 修論 / 論文紹介 / 講義>
- 発表者: <your_name>
- 言語: <日本語 / 英語>
- 想定発表時間: <X 分（任意）>
- 既知の制約: <あれば。なければ「特になし」>

## Codex 自身に委ねる判断
- スライド枚数（スタイルガイドの場面別目安に従う）
- 各スライドのタイトル
- 各スライドの L1 メッセージ（1 スライド 1 個、具体的な主張）
- 視覚要素の選定（テーブル / チャート / フロー図 / 原図切り抜き）
- 内容の取捨選択と圧縮（元データの何を残し何を捨てるか）

## 必須事項
- 着手前に `office/presentation/notes/<YYYY-MM-DD>-plan.md` に計画
  （構成・各スライドのタイトル・L1 メッセージ・視覚要素の方針）を必ず書き残してから実装に入る
- 生成スクリプト: `office/presentation/scripts/generate_<目的>_<YYYYMMDD>.py`
- .pptx: `work/presentations/slides/<目的>_<YYYYMMDD>.pptx`
- `pptx_helpers.py` を import して再利用（重複実装しない）
- 各スライドビルダー末尾で `assert_no_overlap(rects)` を呼ぶ
- L1 強調は 1 スライド 1 個ルールを厳守

## 完了報告
- 生成した .pptx パス
- 採用した枚数と、なぜその枚数にしたかの根拠
- 各スライドのタイトル + L1 メッセージ一覧
- 計画メモのパス
```

---

## テンプレ簡略版（短い指示でいいとき）

```
<project_root>/<元データへのパス> を読んで、<発表場面（例: 研究室報告会）>用の <言語（例: 日本語）> スライドを生成してください。
<project_root>/office/presentation/AGENTS.md および <project_root>/AGENTS.md のスタイルガイドに従い、
構成・L1 メッセージ・視覚デザインは Codex の裁量で決めてください。

着手前に計画を `office/presentation/notes/<YYYY-MM-DD>-plan.md` に記録してから実装してください。
出力は `work/presentations/slides/<目的>_<YYYYMMDD>.pptx`、
スクリプトは `office/presentation/scripts/generate_<目的>_<YYYYMMDD>.py` に保存してください。
完了時に枚数の根拠と L1 メッセージ一覧を返してください。
```

---

## テンプレ場面別の補助情報

汎用版のプロンプトに以下のヒントを足したいときに参考にする。

### 報告会
- 発表場面: 研究室の定期報告会
- 想定枚数: 6-15 枚（スタイルガイド既定）
- 想定時間: 12-15 分
- 含めたい要素: テーマ概要 / 実験進捗 / 解析結果 / 今後の予定

### 国内学会
- 想定枚数: 20-50 枚
- 想定時間: 12-15 分（口頭）/ ポスター長時間
- 含めたい要素: 先行研究 / 目的 / 実験 / 結果 / 考察 / 結語 / 謝辞 / 補助

### 国際学会（英語）
- 想定枚数: 20-25 枚（圧縮）
- 言語: English
- 翻訳の専門用語チェック必須（化学・物理学術用語）

### 研究紹介
- 想定枚数: 8-12 枚
- 対象聴衆: 研究室見学者、新人など
- タイトルスライドは「研究紹介」(28pt)

### 論文紹介（journal club）
- 想定枚数: 6-12 枚
- **必須**: 原論文・SI の図表が「主」、自作図表は「補助」
- 抽出フロー: pdftoppm + crop + add_picture_fit
- 出典明記必須（Source: <Authors>, <Journal> <Year>, Figure X）

### 修論発表
- 想定枚数: 25-35 枚
- 想定時間: 15-25 分
- タイトル: 論文タイトル(32pt 太字)、補助スライドあり

### 講義・チュートリアル
- 想定枚数: 15-30 枚
- 対象聴衆: 学生・他分野研究者
- 平易語・概念図・段階的説明を優先
- 数式の出現箇所は注釈付き

---

## テンプレ既存スライド差分修正

```
既存の生成スクリプト office/presentation/scripts/<script_name>.py を読み、
以下の修正を加えてから .pptx を再生成してください。

## 修正内容
<具体的な修正指示。例: "スライド 5 の L1 メッセージを XX に変更"、"スライド 8 の図を YY.png に差し替え" など>

## 制約
- office/presentation/AGENTS.md のスタイルガイドを引き続き厳守
- 既存の他スライドには触らない（指定スライドのみ修正）
- assert_no_overlap が末尾で必ず走ることを確認

## 出力
- 既存スクリプトを上書き
- .pptx を同名で再生成

完了時に「どのスライドをどう変更したか」を返してください。
```

---

## 運用 tips

### v1 と v2 の違い

| 項目 | v1（旧） | v2（現行） |
|------|---------|-----------|
| 計画メモ作成 | Claude が事前作成 | Codex が自ら作成 |
| 枚数決定 | Claude が決定 | Codex が決定 |
| 各スライドのタイトル | Claude が決定 | Codex が決定 |
| L1 メッセージ選定 | Claude が決定 | Codex が決定 |
| 視覚要素方針 | Claude が指定 | Codex が決定 |
| python-pptx 実装 | Codex | Codex |
| 検証 | Claude | Claude |

### コピペ手順

1. このファイルから該当テンプレを選ぶ
2. `<...>` プレースホルダを埋める（最低限: 元データ・場面・言語）
3. `codex exec --full-auto --skip-git-repo-check -C <project_root> "..." </dev/null` の形でターミナル実行（または Claude Code から `Bash` ツールで起動）

### Codex 出力後の検証は Claude Code 側で

Codex の生成物（.pptx）は必ず python-pptx で構造検証 +（soffice あれば）PNG 化して目視。詳細は caw-slides Skill 本体の「Step D: 検証」を参照。

### テンプレ追加・更新

新しい発表場面が出たらこのファイルにテンプレを追加する。テンプレの内容（特にスタイルガイドの呼び出し方）を変更したら、caw-slides の SKILL.md「Codex 委譲ワークフロー」セクションも整合させる。
