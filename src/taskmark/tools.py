"""TaskmarkのMCPツール定義"""

from mcp.server.fastmcp import FastMCP

from taskmark import storage


def register_tools(mcp: FastMCP) -> None:
    """全Taskmarkツールを指定のFastMCPサーバーに登録する"""

    # --- プロジェクトツール ---

    @mcp.tool()
    def list_projects() -> str:
        """全プロジェクトの一覧を取得する。

        プロジェクト名を改行区切りで返す。
        """
        projects = storage.list_projects()
        if not projects:
            return "プロジェクトが見つかりません。"
        return "\n".join(projects)

    @mcp.tool()
    def create_project(name: str) -> str:
        """新しいプロジェクトを作成する。

        Args:
            name: プロジェクト名（ディレクトリ名として使用）
        """
        path = storage.create_project(name)
        return f"プロジェクト '{name}' を作成しました: {path}"

    @mcp.tool()
    def delete_project(name: str) -> str:
        """プロジェクトとその全タスクを削除する。

        Args:
            name: 削除するプロジェクト名
        """
        storage.delete_project(name)
        return f"プロジェクト '{name}' を削除しました。"

    # --- タスクツール ---

    @mcp.tool()
    def list_tasks(project: str) -> str:
        """プロジェクト内の全タスク一覧を取得する。

        Args:
            project: プロジェクト名
        """
        tasks = storage.list_tasks(project)
        if not tasks:
            return f"プロジェクト '{project}' にタスクが見つかりません。"
        return "\n".join(tasks)

    @mcp.tool()
    def create_task(
        project: str, task_name: str, title: str, template: str = "default"
    ) -> str:
        """テンプレートから新しいタスクディレクトリを作成する。

        テンプレートディレクトリがコピーされ、プレースホルダ（{{title}}, {{created_at}}, {{updated_at}}）が置換される。

        Args:
            project: プロジェクト名
            task_name: タスクのディレクトリ名
            title: タスクのタイトル（テンプレートのプレースホルダに使用）
            template: 使用するテンプレート名（デフォルト: "default"）
        """
        path = storage.create_task(project, task_name, title, template)
        files = storage.list_files(project, task_name)
        return f"タスク '{task_name}' を作成しました: {path}\nファイル: {', '.join(files)}"

    @mcp.tool()
    def delete_task(project: str, task_name: str) -> str:
        """タスクディレクトリとその全ファイルを削除する。

        Args:
            project: プロジェクト名
            task_name: 削除するタスク名
        """
        storage.delete_task(project, task_name)
        return f"タスク '{task_name}' をプロジェクト '{project}' から削除しました。"

    @mcp.tool()
    def list_tasks_by_status(project: str, status: str) -> str:
        """プロジェクト内のタスクをステータスで絞り込む。

        Args:
            project: プロジェクト名
            status: 絞り込むステータス（例: todo, in_progress, done）
        """
        tasks = storage.list_tasks_by_status(project, status)
        if not tasks:
            return f"プロジェクト '{project}' にステータス '{status}' のタスクはありません。"
        return "\n".join(tasks)

    # --- ファイルツール ---

    @mcp.tool()
    def list_files(project: str, task_name: str) -> str:
        """タスクディレクトリ内の全ファイル一覧を取得する。

        Args:
            project: プロジェクト名
            task_name: タスク名
        """
        files = storage.list_files(project, task_name)
        if not files:
            return f"タスク '{task_name}' にファイルがありません。"
        return "\n".join(files)

    @mcp.tool()
    def get_file(project: str, task_name: str, filename: str) -> str:
        """タスクディレクトリ内のファイルを読み取る。

        Args:
            project: プロジェクト名
            task_name: タスク名
            filename: 読み取るファイル名
        """
        return storage.get_file(project, task_name, filename)

    @mcp.tool()
    def update_file(
        project: str, task_name: str, filename: str, content: str
    ) -> str:
        """タスクディレクトリ内のファイルを上書き更新する。

        更新後、変更前・変更後のファイルパスが返される。
        差分を確認するため、返されたパスを使って `code --diff 変更前パス 変更後パス` を実行すること。

        Args:
            project: プロジェクト名
            task_name: タスク名
            filename: 更新するファイル名
            content: 新しいファイル内容
        """
        old_path, new_path = storage.update_file(project, task_name, filename, content)
        return (
            f"タスク '{task_name}' のファイル '{filename}' を更新しました。\n"
            f"変更前: {old_path}\n変更後: {new_path}"
        )

    @mcp.tool()
    def create_file(
        project: str, task_name: str, filename: str, content: str
    ) -> str:
        """タスクディレクトリ内に新しいファイルを作成する。

        Args:
            project: プロジェクト名
            task_name: タスク名
            filename: 新しいファイル名
            content: ファイル内容
        """
        path = storage.create_file(project, task_name, filename, content)
        return f"ファイル '{filename}' を作成しました: {path}"

    @mcp.tool()
    def delete_file(project: str, task_name: str, filename: str) -> str:
        """タスクディレクトリ内のファイルを削除する。

        Args:
            project: プロジェクト名
            task_name: タスク名
            filename: 削除するファイル名
        """
        storage.delete_file(project, task_name, filename)
        return f"タスク '{task_name}' のファイル '{filename}' を削除しました。"

    # --- gitツール ---

    @mcp.tool()
    def status() -> str:
        """~/.taskmark/ 内の未コミット変更一覧を取得する。"""
        result = storage.git_status()
        if not result:
            return "未コミットの変更はありません。"
        return result

    @mcp.tool()
    def commit(message: str) -> str:
        """~/.taskmark/ 内の全変更をgitコミットする。

        明示的に指示されたときのみ使用すること。

        Args:
            message: コミットメッセージ
        """
        result = storage.git_commit(message)
        if not result:
            return "コミットする変更はありませんでした。"
        return result

    # --- tmpツール ---

    @mcp.tool()
    def revert_file(project: str, task_name: str, filename: str) -> str:
        """タスクファイルを直前の変更前の状態に復元する。

        update_fileで保存された変更前データをtmpから書き戻す。
        復元後、tmpの変更前データは削除される。

        Args:
            project: プロジェクト名
            task_name: タスク名
            filename: 復元するファイル名
        """
        storage.revert_file(project, task_name, filename)
        return f"タスク '{task_name}' のファイル '{filename}' を変更前の状態に復元しました。"

    @mcp.tool()
    def tmp_stats() -> str:
        """tmpディレクトリのファイル数と合計サイズを取得する。"""
        stats = storage.tmp_stats()
        count = stats["file_count"]
        total = stats["total_bytes"]
        if count == 0:
            return "tmpディレクトリにファイルはありません。"
        if total < 1024:
            size_str = f"{total} B"
        elif total < 1024 * 1024:
            size_str = f"{total / 1024:.1f} KB"
        else:
            size_str = f"{total / (1024 * 1024):.1f} MB"
        return f"ファイル数: {count}\n合計サイズ: {size_str}"

    @mcp.tool()
    def clear_tmp() -> str:
        """tmpディレクトリ内の全ファイルを削除する。"""
        deleted = storage.clear_tmp()
        if deleted == 0:
            return "削除するファイルはありませんでした。"
        return f"{deleted} 件のファイルを削除しました。"

    # --- テンプレートツール ---

    @mcp.tool()
    def list_templates() -> str:
        """利用可能な全テンプレートの一覧を取得する。

        テンプレート名を改行区切りで返す。
        """
        templates = storage.list_templates()
        if not templates:
            return "テンプレートが見つかりません。"
        return "\n".join(templates)

    @mcp.tool()
    def create_template(name: str) -> str:
        """新しい空のテンプレートディレクトリを作成する。

        作成後、add_template_file でファイルを追加できる。

        Args:
            name: テンプレート名（ディレクトリ名として使用）
        """
        path = storage.create_template(name)
        return f"テンプレート '{name}' を作成しました: {path}"

    @mcp.tool()
    def add_template_file(template: str, filename: str, content: str) -> str:
        """テンプレートディレクトリにファイルを追加・更新する。

        テンプレートファイルではプレースホルダが使用可能: {{title}}, {{created_at}}, {{updated_at}}

        Args:
            template: テンプレート名
            filename: 追加するファイル名
            content: ファイル内容（プレースホルダを含めることが可能）
        """
        path = storage.add_template_file(template, filename, content)
        return f"テンプレート '{template}' にファイル '{filename}' を追加しました: {path}"
