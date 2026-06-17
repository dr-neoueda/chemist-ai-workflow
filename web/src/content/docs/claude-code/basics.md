---
title: 設定の階層と基礎
description: ~/.claude/ と .claude/、CLAUDE.md、settings.json の使い分け
---

Claude Code の設定は **2 階層 + CLAUDE.md** で構成されます。本ページでこの構造を整理します。

## 設定ファイルの階層

```
~/.claude/         ← User level（全プロジェクト共通、全環境で読まれる）
.claude/           ← Project level（カレントディレクトリ配下、後勝ち）
```

各階層に置けるもの：

| ファイル / ディレクトリ | 役割 |
|---|---|
| `CLAUDE.md` | Claude にプロジェクト指示を渡す（自動ロード） |
| `settings.json` | permissions / hooks / allowedTools の設定 |
| `agents/` | Sub-agent の定義 |
| `skills/` | Skill の定義 |
| `commands/` | Slash command の定義 |
| `rules/` | コーディング規約・運用ルール |

User と Project に同名ファイルがあれば、Claude Code は両方をマージして読みます（プロジェクト側が後勝ちで上書き）。

## CLAUDE.md：プロジェクト指示の中心

`./CLAUDE.md` または `.claude/CLAUDE.md` を置くと、セッション開始時に自動でコンテキストに入ります。

最小例：

```md
# 研究プロジェクト設定

## 使用ツール
- Python 3.12+
- Gaussian, GROMACS, CP2K
- Notion + Google Drive

## コーディング規約
- 型ヒント必須
- 単位コメント必須（# kJ/mol, # Å）
```

複数の `CLAUDE.md` を nested に配置することも可能（`~/lab/CLAUDE.md` + `~/lab/office/<部署>/CLAUDE.md` のような構造）。Claude Code はカレントディレクトリから親方向に遡って関連 `CLAUDE.md` を見つけます。

## settings.json の典型構造

```json
{
  "permissions": {
    "allow": [
      "Bash(ls:*)",
      "Bash(git status:*)",
      "Bash(npm run dev:*)"
    ],
    "deny": []
  },
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [
          { "type": "command", "command": "..." }
        ]
      }
    ]
  }
}
```

`permissions.allow` で permission prompt の頻度を減らせます。よく使う read-only コマンドを許可リストに入れると、確認ダイアログが減って体験が改善します。

## 化学プロジェクトでの典型構成

著者の `~/lab/` ルート：

```
~/lab/
├── CLAUDE.md            ← 全研究プロジェクト共通の指示（ECC 自動発動プロトコル等）
├── .claude/
│   ├── settings.json    ← permissions, hooks
│   └── agents/          ← python-reviewer, codex-rescue 等
├── office/            ← 部署システム
│   ├── CLAUDE.md
│   └── <部署>/CLAUDE.md
├── work/papers/              ← 文献管理パイプライン
├── work/manuscripts/         ← 論文ドラフト
└── qc-calculations/     ← 計算ジョブ
```

`~/lab/CLAUDE.md` で「自動発火トリガー」を一元管理し、各部署の `CLAUDE.md` で部署固有のルールを補足する 2 階層構造。

## 次のステップ

- [Skills](/claude-code/skills/) — プロジェクト固有のメソッドをスキル化
- [Hooks](/claude-code/hooks/) — ライフサイクルに自動化を仕込む
- [office/ 部署テンプレート](/claude-code/company-template/)
