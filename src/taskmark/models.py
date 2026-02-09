"""Taskmarkのデータモデル定義"""

from datetime import datetime

# テンプレートファイル内で使用可能なプレースホルダ変数
TEMPLATE_VARIABLES = {
    "title": "タスクのタイトル",
    "created_at": "作成日時 (ISO 8601)",
    "updated_at": "更新日時 (ISO 8601)",
}

DEFAULT_TEMPLATE_CONTENT = """\
---
status: todo
created: {{created_at}}
updated: {{updated_at}}
---

# {{title}}

## 概要


## タスク

- [ ]

## メモ

"""


def render_template(content: str, title: str) -> str:
    """テンプレートのプレースホルダを実際の値に置換する"""
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    return (
        content.replace("{{title}}", title)
        .replace("{{created_at}}", now)
        .replace("{{updated_at}}", now)
    )
