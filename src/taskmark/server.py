"""Taskmark MCPサーバーのエントリーポイント"""

from mcp.server.fastmcp import FastMCP

from taskmark import storage
from taskmark.tools import register_tools

mcp = FastMCP("taskmark")


@mcp.resource("taskmark://info")
def server_info() -> str:
    """Taskmarkサーバーの基本情報"""
    return (
        "Taskmark - タスク管理MCPサーバー\n"
        f"データディレクトリ: {storage.BASE_DIR}\n"
        f"テンプレート: {storage.TEMPLATES_DIR}\n"
        f"プロジェクト: {storage.PROJECTS_DIR}"
    )


# 全ツールを登録
storage.ensure_base_dirs()
register_tools(mcp)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
