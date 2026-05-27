# Changelog

本ファイルは [Keep a Changelog](https://keepachangelog.com/) と [Semantic Versioning](https://semver.org/) に準拠。

## [1.5.1 / Codex 1.4.1] - 2026-05-27

### Changed — オンボーディング最初の質問を「経験レベルを率直に尋ねる」形に

- Q0（セットアップモード選択）を「どこまで詳しくやりますか？」から **「パソコンのターミナルや AI エージェントを使うのは初めてですか？」** へ言い換え。「はい、初めて」を先頭に強調し、Quick/Standard/Advanced の語が分からない初心者を取りこぼさないようにした（内部モード名は不変）。plugin / codex 両方
- バージョン: plugin 1.5.0 → 1.5.1 / codex-plugin 1.4.0 → 1.4.1 / marketplace 同期

## [1.5.0 / Codex 1.4.0] - 2026-05-27

### Added — 初心者向け初期環境（投入フォルダ・過去データ取り込み・自動インストーラ）

パソコン操作初心者に寄り添うオンボーディングへ拡張。

- **投入フォルダの自動生成**（caw scaffold）: 各計算ソフトディレクトリに `inbox/`（これから計算する入力の置き場）と `_past-data/`（過去の入出力の置き場）、research に `papers/inbox/`（PDF の置き場）を、平易な README 付きで生成。「どこに何を置くか」で迷わせない
- **過去データ一括取り込み**（caw-playbook 拡張）: `_past-data/` の過去入出力を解析し、よく使う汎関数・基底・収束設定・頻出エラーを Playbook の `## Lessons Learned` に初期 seed → その人向けに最適化
- **`caw-setup` スキル（新規）**: 外部ツール（Python・poppler・python-pptx 等）の不足を検出し、計画提示 → 一度の承認 → 順番にインストール（macOS / Windows、冪等、sudo 不使用、失敗継続）
- **bootstrap スクリプト（新規）**: `setup/caw-setup.sh`（macOS / Homebrew）・`setup/caw-setup.ps1`（Windows / winget + Scoop）。CLI・Node・git まで含めて導入（鶏卵問題対応）。同じ「計画提示 → 一括」方式
- README（plugin / codex）に caw-setup と過去データ取り込みを追記

### Added — 初心者を強めに誘導する仕組み

ターミナル・IDE・AI が初めての人を最初は強めに手引きする。

- **「はじめて」モード**（onboarding Call 0 の 4 つ目）: `.company/CLAUDE.md`（codex は AGENTS.md）に `> 運用モード: はじめて` を記録。運営モードが平易語・専門用語の 1 行説明・毎回「次はこれ」提示・不可逆操作の事前確認・コピペコマンド明示を全応答で適用
- **ガイド付き初回ツアー**（scaffold 後）: 「一緒に最初の 1 件をやってみましょう」で TODO / 論文登録 / 計算入力のいずれかを手取り足取り
- **START HERE 文書**: プロジェクト直下に `はじめにお読みください.md` を生成（これは何 / まず何をするか / 言い方早見表 / フォルダの意味 / 用語ミニ辞典 / 困ったとき）
- **用語ヘルプ + ターミナル/IDE 導入案内**: 「〇〇って何?」に平易に即答する運営ルール + Web 新ページ「はじめての方へ（ターミナル・IDE の基本）」（VS Code 導入・ターミナルの開き方・最初の起動・用語表）
- バージョン: plugin 1.4.5 → 1.5.0 / codex-plugin 1.3.5 → 1.4.0 / marketplace 同期（新スキル追加のため minor）

## [1.4.5 / Codex 1.3.5] - 2026-05-21

### Added — showcase（宣伝・紹介・募集）variant（実デッキ添削からの学び）

ユーザーが手で添削した宣伝デッキを手本に、研究発表用 4 variant とは設計思想の異なる
「実スクリーンショット主役のコラージュ型」を 5 つ目の用途バリアントとして追加。

- **`templates/generate_showcase.py`**（新規・5-8 枚）: 概念（プログラムヘッダ + ツール名サブ行 + ヒーロー図 + 説明カード2枚 + 動作環境ロゴ）／メイン機能（俯瞰図 + カード + 機能図2枚）／使用例（スクショ・コラージュ + キャプション画像上 + アプリロゴクラスタ）／募集（CTA）。個人化なし・全 `<...>` プレースホルダ。画像未挿入でもラベル箱で実行可
- **`pptx_helpers.py` に showcase helper 3 種**: `add_context_header`（プログラムヘッダ + ツール名サブ行）／`add_collage_caption`（画像上 2 行キャプション）／`add_logo_cluster`（アプリロゴを小さく等間隔・空リストは無描画）。いずれも `assert_no_overlap` 用 rect を返す
- **style-guide §15**（showcase レイアウト）: 研究発表 variant との差分表（タイトル＝プログラム名／実スクショ主役／コラージュ密度／キャプション画像上／アプリロゴ／§0 緩和／用語一般化）、helper 早見、配布物の個人化禁止
- **SKILL.md**: 用途バリアント 4→5、同梱資産に generate_showcase.py を追記（plugin / codex 両 SKILL.md）
- PR ループ: python-reviewer → codex（記録: `~/lab/.company/review/code-reviews/2026-05-21-showcase-template.md`）
- バージョン: plugin 1.4.4 → 1.4.5 / codex-plugin 1.3.4 → 1.3.5 / marketplace 同期

## [1.4.4 / Codex 1.3.4] - 2026-05-21

### Changed — フォント階層の固定化 + イラスト文字の本文スケール化（蛍デッキ反復の学び）

子供実験教室「ホタルの発光」デッキをイラスト主体で作る一連の添削から、3 つの調整を caw-slides に恒久反映。

- **フォント階層を 3 段に固定**（style-guide §2 / §14-2 / §14-3）: タイトル 28pt / 強調=L1=重要本文 24pt / 本文 20pt。**key-message band（L1）は常に 24pt**。色も役割分担（navy=見出し / dark=本文 / blue=要点 / red=注意 / grey=補足）。§14-3 がこれまで header 21・body 16 で §2 と矛盾していたのを統一
- **4 テンプレ**（generate_conference/journal_club/lab_report/lecture）の font を新階層に: ▸ヘッダー 21→24 / 本文 16→20 / L1 band 20→24
- **`research_icons` のイラスト内文字を本文スケールに拡大 + アイコンへ近接**: `label` 既定 12→17 / `sublabel` 9→13、3 ビルダーの node/center ラベルも 17–18 に、ラベル位置をアイコン直下へ寄せた（離れた配置の「スカスカ感」を解消）
- **style-guide §11bis 品質ルール拡張**: 「アイコンとラベルは近接」「イラスト内文字も本文サイズ目安（fontsize 主 16–19 / 強調 22–24 / 補助 13–15）」「ドメイン特有アイコンは patches で自作可（材料＝登場人物）」を追加
- PR: python-reviewer（constant-tuning、回帰なし APPROVE。figure-lifecycle/guards 健在）。research_icons は 1.4.3 で codex 二段済・本変更は定数のみのため codex 再実行なし。記録: `~/lab/.company/review/code-reviews/2026-05-21-firefly-deck-and-falsepositive.md`
- バージョン: plugin 1.4.3 → 1.4.4 / codex-plugin 1.3.3 → 1.3.4 / marketplace 同期

## [1.4.3 / Codex 1.3.3] - 2026-05-20

### Added — 概念イラストモジュール `research_icons`

caw 宣伝デッキ等のイラスト作成を重ねて確立したノウハウを、再利用可能な配布
モジュールとして恒久化（references 層、`pptx_helpers` と同階層）。任意テーマの
スライドで同等品質の概念イラストを量産できる。

- **線画アイコン 10 種**（`icon_researcher` / `icon_flask` / `icon_molecule` /
  `icon_document` / `icon_chart` / `icon_slides` / `icon_gear` / `icon_magnifier` /
  `icon_laptop` / `icon_sparkle`）。共通シグネチャ `icon(ax, x, y, s=1.0, color=)`、
  同縮尺で混在可。`ICONS` 名前レジストリ付き。配色は `CATEGORICAL_HEX` に整合
- **構図ビルダー 3 種**（PNG パスを返す → `add_picture_fit` に渡す）:
  - `hub_diagram` — 中心 + 放射（部署図・構成要素）
  - `cycle_diagram` — 円環 + 駅間の隙間に弧矢印（研究サイクル。駅を貫かない）
  - `converging_diagram` — 周辺要素が中心へ収束（負荷が押し寄せる課題図。矢じりはリム着地）
- ヘルパ `label` / `sublabel` / `new_figure` / `save_figure`（ビルダーに無い構図を自作する用）
- **style-guide.md §11bis「概念イラスト（schematic）作成」を新設**: イラスト vs チャートの
  題材判断表（規模・桁比較は定量チャート、構成・サイクルはイラスト）、アイコンカタログ、
  3 ビルダーの使い方、品質ルール（矢印はリム/隙間着地・サブラベルで密度・等間隔等縮尺・
  背景は白基調で過度な装飾を避ける）。§14-6 早見表と SKILL.md にも追記
- PR ループ: python-reviewer（HIGH 1 = Figure リーク + MEDIUM 5 + LOW 2）→ codex-rescue
  二段（MEDIUM 2 = 高密度サイクルの弧反転・save 時クリーンアップ順序 + LOW 2）。全件対応。
  記録: `~/lab/.company/review/code-reviews/2026-05-20-research-icons.md`
- バージョン: plugin 1.4.2 → 1.4.3 / codex-plugin 1.3.2 → 1.3.3 / marketplace 同期

## [1.4.2 / Codex 1.3.2] - 2026-05-20

### Changed — カテゴリカル配色（青一色の解消）

CP2K 初学者向けデッキ生成の添削で「全体が青中心で単調」と判明。図表・グラフに識別・対比・強調のための複数色を導入。

- **`CATEGORICAL_HEX` / `CATEGORICAL_RGB`**: 青→橙→緑→赤→シアン→紫→アンバーの 7 色パレット
- **`add_bar_chart` / `add_scatter_line_chart`**: 系列をパレットで自動色分け（線 + マーカー）。マーカー着色は `show_markers` 時のみ
- **`add_data_table(highlight_row=N)`**: 推奨案 / hero 行を淡アンバー（`COLOR_ROW_HIGHLIGHT_FILL` #FFF2CC）で塗る。範囲外は ValueError
- **`add_energy_diagram`**: 状態を役割色（始=青 / 終=緑 / TS・中間体=赤）、connector はグレー。位置（山/谷）が意味を担うため赤緑 CVD でも判別可
- **style-guide.md §0 に「図表・グラフは青一色を避け、カテゴリカル配色」節**を追加（多系列はパレット巡回、テーブルは highlight_row、対比の鉄則は維持）
- PR ループ: python-reviewer（HIGH 1 + MEDIUM 1 + LOW 2 修正、show_markers ガード等）。codex-rescue は背景継続が時間内未完のため Claude + 自己評価で補完
- バージョン: plugin 1.4.1 → 1.4.2 / codex-plugin 1.3.1 → 1.3.2 / marketplace 同期

## [1.4.1 / Codex 1.3.1] - 2026-05-20

### Changed — caw-slides の「AI 作成感」除去（実デッキ添削 fb 反映）

MLIP 研究紹介デッキを caw-slides で生成し、その添削から得た改善を `pptx_helpers.py` と `style-guide.md` に反映。

- **表の空白圧縮（`add_data_table`）**: デフォルト `word_wrap=False`、header 行 = `header_size × 2.0` / body 行 = `font_size × 2.0` に分離（CJK headroom）、セル上下余白 3pt、`row_height=Emu(0)` を auto 扱い。4 行表が 0.9"/行(3.6") → 0.44"/行(1.78") に圧縮。`row_height` / `cell_margin` / `word_wrap` パラメータ追加（後方互換）
- **style-guide.md §0 に「表とまとめスライドの作り込み（AI 作成感の除去）」節を新設**:
  - 表は内容に密着（tight 行・全幅に伸ばさず中央寄せ）。埋めたいなら空白でなく情報を足す
  - まとめ/結語スライドにも必ず図を置く（positioning 図等）
  - **コンテンツスライドは「図・表・グラフ + L1 + 支持本文」を基本構成に**（図 + L1 だけのスパース構成を避ける。視覚要素が幅を埋めないなら左に視覚・右に支持本文の 2 ゾーン、横長テーブルは上に視覚・下に支持本文）
  - **「箱に文字を詰めた」text-box フロー図（`add_flow_box` × N）は原則作らない**。第一選択はプロセスの効果をグラフで示す（例 active learning → 学習曲線）、第二選択はイラスト/アイコン + 最小ラベル
  - 図表構成要素（フロー box・テーブル・split_2col）は §0 文字数上限の対象外（`assert_text_minimal` の override 指針）
- PR ループ: python-reviewer + codex-rescue。`add_data_table` 改修で HIGH 1（行高さ × word_wrap）+ MEDIUM 2（header/body 分離・CJK 余裕）+ LOW 2 を修正
- バージョン: plugin 1.4.0 → 1.4.1 / codex-plugin 1.3.0 → 1.3.1 / marketplace 同期

## [1.4.0 / Codex 1.3.0] - 2026-05-15

### Added — `caw-slides` Skill（PowerPoint スライド生成）

化学研究発表用 PowerPoint スライドを python-pptx ベースで生成する専用 Skill。実運用された 12 件のスライドから抽出したスタイルガイドを内蔵し、4 用途バリアントで「学会発表 / 論文紹介 / 報告会 / 講義」に対応する。

- **発火**: 自然言語マッチ（「スライド作って」「パワポ」「学会発表」「論文紹介」「報告会」「講義スライド」等）
- **同梱資産**（plugin / codex-plugin 並列配信）:
  - `references/pptx_helpers.py`（1000+ 行）: `add_slide_chrome` / `add_key_message_band` / `mixed_runs` / `assert_no_overlap` / `add_bar_chart` / `add_scatter_line_chart` / `add_flow_box` / `add_data_table` 等のヘルパ。MS Gothic のクロスプラットフォーム探索（macOS / Windows / Linux、`CAW_SLIDES_MSGOTHIC` 環境変数で override 可）
  - `references/style-guide.md`: 14 セクション + canonical 実装パターン（**§0 絶対ルール = 文字数を極限まで減らし図表で直感的に伝える**、16:9、フォント混在、L1 強調 1 個ルール、3 層 y 座標構造（chrome / 本文 / key-message band）、3 tier 強調 L1/L2/L4（L2 = 影なし・枠線あり・塗りなしの透明箱）、native chart 強制、座標 hygiene、出典は用途別に任意で `add_source_line`）
  - **§0 強制ヘルパ（実装済み）**: `assert_text_minimal(slide)` でテキストボックス数 ≤ 5 / 本文総行数 ≤ 12 / 1 ボックス内 ≤ 120 字を自動検証（違反は ValueError）; `assert_title_assertive(title)` で「結果」「考察」「方法」「目的」等の無味な見出しを lint（22 ワードの blacklist 内蔵）
  - **化学特化ヘルパ**: `add_molecule(slide, smiles)` — SMILES → RDKit Draw → PNG embed (lazy import); `add_reaction_scheme(slide, reactants, products, conditions)` — 反応式の横並び合成（reactant + reactant → product, conditions ラベル付き）; `add_energy_diagram(slide, levels, labels)` — 反応座標 vs エネルギーの 1 ライン図（matplotlib smoothstep、TS は短い dash で sharp peak 表現）
  - **レイアウトパターン**: `split_2col(slide, left_paragraphs, right_paragraphs)` — 2 カラム比較（Form I/II・before/after 等の概念対比受け皿）; `add_timeline(slide, milestones=[(date, event), ...])` — 横軸時系列バー（≤ 8 milestones、衝突 guard 付き）
  - **クロスプラットフォーム / 安全性**: matplotlib 日本語 lazy auto-config（`_ensure_matplotlib_japanese`、未検出時は `RuntimeWarning` で診断）; PNG temp file は `try/finally + os.unlink` で確実 cleanup（Windows の PIL 再オープン bug 対策含む）
  - `references/codex-exec-templates.md`: Codex 委譲 v2（完全お任せ）プロンプトテンプレ集
  - `templates/generate_conference.py`: 学会発表 variant（口頭・ポスター、20-50 枚）
  - `templates/generate_journal_club.py`: 論文紹介 variant（6-12 枚、pdftoppm + crop ワークフロー）
  - `templates/generate_lab_report.py`: 研究室報告会 variant（6-15 枚、native chart + table）
  - `templates/generate_lecture.py`: 講義・チュートリアル variant（15-30 枚、概念フロー図）
- **品質ゲート**: `assert_no_overlap` で shape 矩形交差を物理的に禁止（ValueError raise）、L1 1 個ルール、Excel-editable native chart のみ
- **動作確認**: 4 templates 全て smoke test 成功（標準的な 4 枚のデモ .pptx を生成、`assert_no_overlap` pass）

### Changed

- **`plugin/skills/caw/references/chemistry-departments.md`**: presentation 部の説明を caw-slides skill 利用前提に更新。サブディレクトリ列挙に `scripts/`, `notes/`, `references/` を追加、成果物パスを `slides/` → `presentations/slides/` に統一
- **`plugin/skills/caw/references/playbook-starters.md`**: 「計算外ソフトの Playbook」セクションを追加し、caw-slides との関係を明示
- **`web/src/content/docs/claude-code/application.md`**: §5 を caw-slides skill ベースに改稿（4 用途バリアント、共通スタイルガイド、`assert_no_overlap` 保証）
- `plugin/.claude-plugin/plugin.json` version 1.3.1 → 1.4.0
- `codex-plugin/.codex-plugin/plugin.json` version 1.2.1 → 1.3.0
- `.claude-plugin/marketplace.json` plugin 列挙の version 同期

### Notes

- スライド生成システムは元々ユーザーの `.company/presentation/` で実運用されていた成熟資産を caw plugin 化したもの。新規開発ではなく **配信パッケージング**として実装。個人情報（著者名・研究室名・特定研究テーマ・機器型番）はすべて除去済み
- Codex CLI 版（codex-plugin）も同一資産を並列配信。両 CLI で完全機能パリティ
- python-pptx の依存（`python-pptx`、`matplotlib`、`Pillow`）はユーザーが事前にインストール
- スタイルガイド本体（`references/style-guide.md`）はプラグイン更新で上書きされる。プロジェクト固有のオーバーライドは `.company/presentation/CLAUDE.md` (or AGENTS.md) に追加

## [1.3.1 / Codex 1.2.1] - 2026-05-14

### Fixed（B16 — Windows / Linux 対応）

- **`plugin/hooks/load-playbooks.sh`**：mtime 降順ソートを BSD/macOS 専用の `xargs -0 stat -f "%m %N"` から `ls -t`（macOS / Linux / WSL / Git Bash 共通の POSIX）に置換。これまで macOS 以外（Linux 含む）で直近ノートの注入が動いていなかったのを修正
- **`plugin/skills/caw-doctor/SKILL.md` / `codex-plugin/skills/caw-doctor/SKILL.md`**：Playbook の `last_updated` 経過日数計算を BSD/macOS 専用の `date -j -f` から、GNU `date -d` → BSD `date -j` フォールバックの `to_epoch` ヘルパーに置換。macOS 以外でも動作するように

### Changed

- **`.company/` の可視性に関する説明を OS 別に正確化**：「Finder / Explorer から不可視」という macOS/Linux 前提の表現を「macOS Finder / Linux のファイルマネージャでは標準で非表示、Windows Explorer では表示される（いずれの OS でも運営情報専用エリアという位置づけは同じ）」に修正。SKILL.md / claude-md-template / agents-md-template / chemistry-departments / output-location-check.sh / README
- **`plugin/README.md`**：「動作環境」節を追加（OS × コア/Hooks の対応表、Windows は WSL / Git Bash 必須の旨）。v1.1.0 のまま古かった Skills / Hooks / Playbook / プラグイン構造の記述を v1.3.1 の実態に更新
- `plugin/.claude-plugin/plugin.json` version 1.3.0 → 1.3.1
- `codex-plugin/.codex-plugin/plugin.json` version 1.2.0 → 1.2.1
- `.claude-plugin/marketplace.json` version 同期

### Notes

- caw のコア（オンボーディング・部署スキャフォールド・5 Skills のワークフロー）は元々 OS 非依存。今回の修正は **hooks と caw-doctor の bash スニペットに混入していた macOS 専用構文**（`stat -f` / `date -j`）の除去で、これらは Windows のみならず Linux でも壊れていた
- Windows でネイティブに hooks を動かすには WSL または Git Bash が必要（`hooks.json` が `bash` を呼ぶため）。コア機能は Windows ネイティブでも動作

## [1.3.0 / Codex 1.2.0] - 2026-05-14

### Added

- **B1 — Codex 版の Skills 機能パリティ**：`caw-paper` / `caw-input` / `caw-playbook` を `codex-plugin/skills/` に移植。Codex 流に合わせ `trigger:` フィールドを削除し、自然言語マッチで発火。CLAUDE.md → AGENTS.md 表記に変換。これで両プラグインとも 5 Skills（caw / caw-doctor / caw-paper / caw-input / caw-playbook）で揃った
- **B2 — `caw-doctor` Skill 新規追加**（Claude / Codex 両版）：`.company/` 構造の健全性チェック。ルート CLAUDE.md・秘書部・各部署 CLAUDE.md の存在確認、旧構造（成果物が `.company/<dept>/X/` に残存）の検出、Playbook 更新滞り、同日ファイル重複、inbox 孤立ファイルを総点検し、レポート + 修復コマンドを提示
- **B7 — Playbook 雛形を 8 件拡充**（Claude / Codex 両版）：計算ソフト 4 件（Psi4 / NAMD / LAMMPS / OpenMM）+ Python ライブラリ 4 件（RDKit / ASE / MDAnalysis / pymatgen）を `playbook-starters.md` に追加。Python ライブラリ Playbook は API quirks・version 依存挙動・よくある罠を体系化
- **B8 — MCP 自動セットアップ案内**（Claude / Codex 両版）：オンボーディング Step 3-5 で Q3（ナレッジベース）/ Q4（クラウドストレージ）の選択に応じて `.company/.mcp-setup.md` を生成。Notion / Obsidian / Logseq / Google Drive / Dropbox / OneDrive / Gmail の MCP 設定手順 + API key の環境変数管理ガイド。`references/mcp-setup-templates.md` を新規追加。**鍵そのものは書かず手順書のみ**
- **B10 — オンボーディングの 3 段階化**（Claude / Codex 両版）：Step 2 に「セットアップモード」選択（Call 0）を追加。Quick（1 問・秘書のみ即起動）/ Standard（現行 6 問）/ Advanced（10+ 問、HPC・研究体制・申請書予定・論文ステータスまでヒアリング）
- **B11 — PostToolUse hook で二層原則違反を検出**（Claude Code 版のみ）：`plugin/hooks/output-location-check.sh` を追加。Edit/Write/MultiEdit が `.company/<dept>/<旧パス>/` に書き込んだ時に警告 + 修復コマンドを提示（block はしない warn-only）。`hooks.json` に PostToolUse エントリを追加。Codex 版は hook framework が未整備のため未対応

### Changed

- **`plugin/skills/caw/SKILL.md` / `codex-plugin/skills/caw/SKILL.md`**：Step 2 を 3 段階モード化、Step 3 に MCP セットアップ生成（3-5）を追加し完了メッセージを 3-6 にリネーム、「ファイル参照」に `mcp-setup-templates.md` を追加
- **`plugin/skills/caw/SKILL.md` / `codex-plugin/skills/caw/SKILL.md`**：オンボーディング Q2（計算ソフト）の古典 MD 例示に NAMD / OpenMM を追記（B7 と整合）
- `plugin/.claude-plugin/plugin.json` version 1.2.0 → 1.3.0
- `codex-plugin/.codex-plugin/plugin.json` version 1.1.0 → 1.2.0
- `.claude-plugin/marketplace.json` version 同期

### Notes

- Codex 版は hooks 非対応（B11 のみ Claude Code 限定）。それ以外（B1/B2/B7/B8/B10）は両プラグインで機能等価
- caw-doctor は v1.2 の二層原則 migration 状況の点検にも使える（旧構造を検出して移行コマンドを提示）

## [1.2.0 / Codex 1.1.0] - 2026-05-14

### Added

- **成果物配置の二層原則（CRITICAL）**：caw の出力ファイルを `.company/` 配下（運営情報）と project root 直下（成果物）に明確に二層化
  - 第 1 層 `.company/<dept>/` = 運営情報のみ（TODO・意思決定・学び・Playbook・内部レビュー）
  - 第 2 層 project root = 成果物（`papers/`, `topics/`, `manuscripts/`, `slides/`, `analyses/`, `notebooks/`, `figures/`, `scripts/`, `tools/`, `reports/`, `experiments/`, `gaussian/` 等）
  - `.company/` は dotfile で Finder / Explorer から不可視。AI が生成した md / pptx / docx / png / ipynb 等を `.company/<dept>/` に置くと **ユーザーがファイラーで見つけられない** という v1.0 / v1.1 の構造的問題を解消

### Changed

- **`plugin/skills/caw/SKILL.md`**：「成果物配置の二層原則」セクションを追加。Step 3-4 の作業ディレクトリ生成リストを拡張（research → `papers/` + `topics/`、analysis → `analyses/` + `notebooks/` + `figures/`、engineering → `scripts/` + `tools/`、presentation → `slides/`）
- **`plugin/skills/caw/references/chemistry-departments.md`**：research / engineering / analysis / writing / presentation の各 CLAUDE.md テンプレで出力パスを `.company/<dept>/X/` から `{{PROJECT_ROOT}}/X/` に変更
- **`plugin/skills/caw/references/claude-md-template.md`**：ルート CLAUDE.md にも二層原則を明文化
- **`codex-plugin/skills/caw/SKILL.md`**：同上（AGENTS.md 表記）
- **`codex-plugin/skills/caw/references/agents-md-template.md`**：同上
- **`codex-plugin/skills/caw/references/chemistry-departments.md`**：同上
- `plugin/.claude-plugin/plugin.json` version 1.1.0 → 1.2.0
- `codex-plugin/.codex-plugin/plugin.json` version 1.0.0 → 1.1.0
- `marketplace.json` version 同期

### Migration（v1.0 / v1.1 → v1.2 / Codex 1.0 → 1.1）

既存ユーザーが旧構造（`.company/research/papers/`, `.company/writing/manuscripts/`, `.company/analysis/results/`, `.company/presentation/slides/`）に成果物を蓄積している場合、以下を手動で実施：

```bash
# 移動例（既存ファイルがある場合のみ実行）
mv .company/research/papers/* papers/ 2>/dev/null
mv .company/research/topics/* topics/ 2>/dev/null
mv .company/writing/manuscripts/* manuscripts/ 2>/dev/null
mv .company/analysis/results/* analyses/ 2>/dev/null
mv .company/analysis/figures/* figures/ 2>/dev/null
mv .company/analysis/notebooks/* notebooks/ 2>/dev/null
mv .company/presentation/slides/* slides/ 2>/dev/null
```

`.company/<dept>/` 配下に残った空ディレクトリ（`papers/` `manuscripts/` 等）は削除して構わない。残しても害は無い（caw が読みに行かなくなるだけ）。

将来 v1.3 で `caw-migrate` Skill を追加予定（自動移動 + 衝突解決 + dry-run）。

## [Codex 1.0.0] - 2026-05-13

### Added (Codex CLI 版)

- **codex-plugin/**：Codex CLI 用 caw プラグイン（v1.0.0）を新規追加
  - `codex-plugin/.codex-plugin/plugin.json` — Codex 用プラグインマニフェスト
  - `codex-plugin/skills/caw/SKILL.md` — `/caw` スキル本体（CLAUDE.md → AGENTS.md ターゲットに変換）
  - `codex-plugin/skills/caw/references/{agents-md-template, chemistry-departments, playbook-starters}.md`
- **`.agents/plugins/marketplace.json`**：Codex 用マーケットプレイス manifest（同リポジトリから並列配信）
- **LP**：`/codex-cli/` セクションを placeholder から実装に書き換え、`/codex-cli/setup/` 環境構築ページを新規作成
- **plugin.md**：両環境のインストール手順（Claude Code / Codex CLI）を併記

研究室で Claude Code 派と Codex CLI 派が混在しても、同じ caw メソッドで `.company/` を運用できる構成。

## [1.1.0] - 2026-05-13

### Added

- **Hooks**：SessionStart で `.company/secretary/notes` の直近 3 件と利用可能 Playbook をコンテキスト自動注入、Stop で今日の活動があるのに learnings.md が無い場合にリマインド。
- **`/caw-paper` スキル**：論文検索（arXiv / Crossref / Semantic Scholar / OpenAlex / PubMed）と入手済み PDF の自動メタデータ抽出 → ナレッジベース（Notion / Obsidian / Logseq 等）+ クラウドストレージ（Google Drive 他）への登録。バッチ処理対応。
- **`/caw-input` スキル**：6 ソフト（Gaussian / ORCA / CP2K / GROMACS / VASP / Quantum ESPRESSO）の入力ファイル雛形生成。Playbook デフォルト推奨値を起点に対話的に系・目的・計算条件を確定、`<tool>/<system>_<purpose>_<YYYYMMDD>/` 配下に配置 + ジョブ記録自動生成。
- **`/caw-playbook` スキル**：計算 log の自動解析（収束 / エラー / 異常パターン）→ Lessons Learned エントリ起案 → Playbook への末尾追記。memory feedback への昇格判定も含む。

### Changed

- `plugin.json` version 1.0.0 → 1.1.0（後方互換のスキル追加）。
- `marketplace.json` version 同期。

## [1.0.0] - 2026-05-13

### Added

- 初回公開。caw プラグイン（Chemist's AI Workflow）。
- `/caw` スキル：オンボーディング → 自動スキャフォールド → 運営モードの一連を実装。
- 化学者向け 8 部署 CLAUDE.md テンプレート（secretary / research / engineering / computation / analysis / writing / review / presentation）。
- 計算ソフト Playbook 雛形：Gaussian / GROMACS / CP2K / ORCA / VASP / Quantum ESPRESSO + 汎用。
- 作業ディレクトリの自動生成：選択した計算ソフトに応じて `gaussian/` / `orca/` 等、選択した部署に応じて `papers/` / `manuscripts/` / `slides/`。
- ローカル marketplace 経由の開発・テスト環境。
- 4 つのテストプロファイルでの実機検証完了。

### Documentation

- 配布マーケットプレイスの `.claude-plugin/marketplace.json` を整備。
- MIT ライセンス採用。
- Chemist's AI Workflow LP（Astro Starlight）。
