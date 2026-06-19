# caw HTML デザイン契約（全 CLI 共通の唯一の設計図）

caw が出力する HTML（文献リスト・企業プロファイル・イベントカタログ・比較表など）の見た目を **Claude Code / Codex CLI / Gemini CLI で統一**するための単一の設計図。**HTML を生成するスキルは、この `<style>` と部品をそのまま使う**（CLI ごとに自己流の CSS を作らない）。これにより、どの CLI で作っても同じデザインの HTML が出る。

## 原則

- **オフライン自己完結**：インライン CSS のみ。外部 CSS / Web フォント / 画像に依存しない（インタラクティブ図で Chart.js を使うときだけ CDN を許可・要明示）。**ダブルクリックで開ける**
- **白基調・コーラルのアクセント・ヘアライン罫線**。**影・色面（塗りパネル）・アイコン画像・背景色は使わない**（罫線とカード枠だけで構造を出す）
- システム / Inter フォント、`max-width` で読みやすい幅に
- 見出しアンカー id と `<svg>` / `<canvas id>` は**別名**にする（衝突するとグラフが空になる。`ch` 接頭辞推奨）

## 共通 `<style>`（`<head>` にそのままコピーする）

```html
<style>
:root{--ink:#181d26;--body:#333840;--accent:#aa2d00;--line:#e2e2e2;--muted:#8a8a8a;--bg:#fff}
*{box-sizing:border-box}
body{font-family:Inter,-apple-system,BlinkMacSystemFont,'Segoe UI','Hiragino Sans',sans-serif;color:var(--body);background:var(--bg);max-width:900px;margin:28px auto;padding:0 18px;line-height:1.7}
h1{font-size:21px;color:var(--ink);margin:0 0 4px}
h2{font-size:16px;color:var(--ink);margin:26px 0 8px;border-bottom:2px solid var(--line);padding-bottom:5px}
.cond,.muted{color:var(--muted);font-size:13px}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}
/* リスト（文献など） */
ol.list{list-style:none;padding:0;margin:0}
ol.list>li{padding:14px 0;border-bottom:1px solid var(--line)}
.ttl{color:var(--accent);font-weight:600;font-size:15.5px}
.meta{color:var(--muted);font-size:13px;margin:3px 0}
.sum{font-size:14px;margin:3px 0}
/* カード（企業・イベント） */
.card{border:1px solid var(--line);border-radius:10px;padding:15px 16px;margin:11px 0}
.card h3{font-size:15.5px;color:var(--ink);margin:0 0 6px}
/* テーブル */
table{width:100%;border-collapse:collapse;font-size:14px;margin:10px 0}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}
th{color:var(--ink);font-weight:600;white-space:nowrap}
/* バッジ */
.badge{display:inline-block;border:1px solid var(--line);color:var(--accent);border-radius:4px;padding:2px 8px;font-size:12px;font-weight:600}
footer{color:var(--muted);font-size:12.5px;margin-top:22px;border-top:1px solid var(--line);padding-top:12px}
</style>
```

## 部品（用途別に使い分ける）

- **リスト**（文献リスト等）：`<ol class="list"><li>` … `<span class="ttl">`（タイトル＝コーラルのリンク）＋ `.meta`（著者・年・誌名）＋ `.sum`（要約）
- **カード**（企業プロファイル・イベント）：`<div class="card"><h3>…</h3> … </div>`。状態区別は `.badge`（塗らずに枠＋コーラル文字）
- **テーブル**（比較表・対照表）：`<table>`。罫線は下線のみ、ヘッダは塗らない
- **チャート（オフライン）**：インライン `<svg>`。棒=`<rect>`、レーダー=`<polygon>`、散布=`<circle>`+`<text>`。色は `--accent`（コーラル）と `#888888` の2色に絞る

## スケルトン

```html
<!doctype html><html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title><タイトル></title>
<style>/* 上の共通 <style> をそのまま */</style></head><body>
<header>
  <h1><タイトル></h1>
  <p class="cond">条件・取得日・出典など</p>
</header>
<!-- 本文: ol.list / .card / table を用途で使い分け -->
<footer>出典・取得日</footer>
</body></html>
```

## 適用スキル

- **caw-research（研究）**：文献リスト → `ol.list`
- **caw-research（就活）**：企業プロファイル → `.card`、比較表 → `table`、ポジショニング → SVG 散布
- **caw-events**：イベントカタログ → `.card`、年間スケジュール → SVG タイムライン、過去×今年度 → `table`
- 他に HTML を出力するスキルも本契約に従う

> **Gemini CLI 版**（`GEMINI.md`）は references を読み込まないため、同一の `<style>` を `GEMINI.md` 内にインラインで保持する。本ファイルを変更したら `GEMINI.md` の `<style>` も同じ内容に合わせる。
