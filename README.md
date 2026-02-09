# Taskmark

タスクをディレクトリ + Markdown ファイルで管理する MCP サーバー。

## 必要なもの

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

## セットアップ

### 1. 依存関係のインストール

```bash
cd /path/to/taskmark
uv sync
```

### 2. Claude Code に MCP サーバーを登録

`~/.claude.json` の `mcpServers` に以下を追加:

```json
{
  "mcpServers": {
    "taskmark": {
      "type": "stdio",
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/taskmark",
        "run",
        "src/taskmark/server.py"
      ],
      "env": {}
    }
  }
}
```

`/path/to/taskmark` は実際のパスに置き換えること。

### 3. パーミッション設定（任意）

毎回の確認をスキップするには、プロジェクトの `.claude/settings.local.json` に以下を追加:

```json
{
  "permissions": {
    "allow": [
      "mcp__taskmark__*",
      "Bash(code --diff:*)"
    ]
  }
}
```

## データ構造

```
~/.taskmark/
├── templates/          # タスクテンプレート
│   └── default/
│       └── task.md
├── projects/           # プロジェクト
│   └── <project>/
│       └── <task>/
│           └── task.md
└── .tmp/               # update_file の変更前データ
```

