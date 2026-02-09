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

## 利用可能なツール

### プロジェクト

| ツール | 説明 |
|--------|------|
| `list_projects` | プロジェクト一覧 |
| `create_project` | プロジェクト作成 |
| `delete_project` | プロジェクト削除 |

### タスク

| ツール | 説明 |
|--------|------|
| `list_tasks` | タスク一覧 |
| `create_task` | テンプレートからタスク作成 |
| `delete_task` | タスク削除 |

### ファイル

| ツール | 説明 |
|--------|------|
| `list_files` | タスク内ファイル一覧 |
| `get_file` | ファイル読み取り |
| `create_file` | ファイル作成 |
| `update_file` | ファイル更新（変更前データをtmpに保存、差分表示対応） |
| `delete_file` | ファイル削除 |
| `revert_file` | tmpから変更前の状態に復元 |

### tmp 管理

| ツール | 説明 |
|--------|------|
| `tmp_stats` | tmpのファイル数・サイズ確認 |
| `clear_tmp` | tmp内の全ファイル削除 |

### テンプレート

| ツール | 説明 |
|--------|------|
| `list_templates` | テンプレート一覧 |
| `create_template` | テンプレート作成 |
| `add_template_file` | テンプレートにファイル追加 |
