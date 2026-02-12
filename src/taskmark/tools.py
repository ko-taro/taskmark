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
        lines = []
        for t in tasks:
            status = f" [{t['status']}]" if t["status"] else ""
            lines.append(f"{t['name']}{status}")
        return "\n".join(lines)

    @mcp.tool()
    def create_task(
        project: str, task_name: str, title: str, template: str = "default"
    ) -> str:
        """テンプレートから新しいタスクディレクトリを作成する。

        テンプレートディレクトリがコピーされ、プレースホルダ（{{title}}, {{created_at}}, {{updated_at}}）が置換される。

        Args:
            project: プロジェクト名
            task_name: タスクのディレクトリ名（日本語可。日付プレフィックスが自動付与される。例: ログインバグ修正 → 20260209_ログインバグ修正）
            title: タスクのタイトル（task.md の見出しに使用）
            template: 使用するテンプレート名（デフォルト: "default"）
        """
        path = storage.create_task(project, task_name, title, template)
        actual_name = path.name
        files = storage.list_files(project, actual_name)
        return f"タスク '{actual_name}' を作成しました: {path}\nファイル: {', '.join(files)}"

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
    def archive_task(project: str, task_name: str) -> str:
        """タスクをアーカイブする。

        タスクを _archive/ ディレクトリに移動する。
        git mv を使用するため履歴は保持される。

        Args:
            project: プロジェクト名
            task_name: アーカイブするタスク名
        """
        dest = storage.archive_task(project, task_name)
        return f"タスク '{task_name}' をアーカイブしました: {dest}"

    @mcp.tool()
    def unarchive_task(project: str, task_name: str) -> str:
        """アーカイブ済みタスクをアクティブに戻す。

        _archive/ からプロジェクト直下に移動する。
        git mv を使用するため履歴は保持される。

        Args:
            project: プロジェクト名
            task_name: 戻すタスク名
        """
        dest = storage.unarchive_task(project, task_name)
        return f"タスク '{task_name}' をアーカイブから復元しました: {dest}"

    @mcp.tool()
    def list_archived_tasks(project: str) -> str:
        """プロジェクト内のアーカイブ済みタスク一覧を取得する。

        Args:
            project: プロジェクト名
        """
        tasks = storage.list_archived_tasks(project)
        if not tasks:
            return f"プロジェクト '{project}' にアーカイブ済みタスクはありません。"
        lines = []
        for t in tasks:
            status = f" [{t['status']}]" if t["status"] else ""
            lines.append(f"{t['name']}{status}")
        return "\n".join(lines)

    @mcp.tool()
    def search(query: str, project: str | None = None) -> str:
        """タスクファイル内をキーワード検索する。

        全プロジェクト横断で検索し、マッチしたタスクとファイル、該当行を返す。
        projectを指定すると、そのプロジェクト内のみ検索する。

        Args:
            query: 検索キーワード（大文字小文字を区別しない）
            project: プロジェクト名（省略時は全プロジェクト横断）
        """
        results = storage.search_tasks(query, project)
        if not results:
            return f"'{query}' に一致するタスクは見つかりませんでした。"
        lines = []
        for r in results:
            tag = " (archived)" if r.get("archived") else ""
            lines.append(f"[{r['project']}/{r['task']}]{tag} {r['file']}")
            for ml in r["matched_lines"]:
                lines.append(f"  {ml}")
        return "\n".join(lines)

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

        適用ルールがある場合は一緒に返す。

        Args:
            project: プロジェクト名
            task_name: タスク名
            filename: 読み取るファイル名
        """
        path, content = storage.get_file(project, task_name, filename)
        rules = storage.get_rules(project, task_name)
        result = f"パス: {path}\n---\n{content}"
        if rules:
            result = f"{rules}\n\n---\n{result}"
        return result

    @mcp.tool()
    def update_file(project: str, task_name: str, filename: str, content: str) -> str:
        """タスクディレクトリ内のファイルを上書き更新する。

        更新後、変更前・変更後のファイルパスが返される。
        差分を確認するため、返されたパスを使って `code --diff 変更前パス 変更後パス` を実行すること。
        適用ルールがある場合は一緒に返す。ルールに従ってファイルを編集すること。

        Args:
            project: プロジェクト名
            task_name: タスク名
            filename: 更新するファイル名
            content: 新しいファイル内容
        """
        old_path, new_path = storage.update_file(project, task_name, filename, content)
        rules = storage.get_rules(project, task_name)
        result = (
            f"タスク '{task_name}' のファイル '{filename}' を更新しました。\n"
            f"変更前: {old_path}\n変更後: {new_path}"
        )
        if rules:
            result = f"{rules}\n\n---\n{result}"
        return result

    @mcp.tool()
    def create_file(project: str, task_name: str, filename: str, content: str) -> str:
        """タスクディレクトリ内に新しいファイルを作成する。

        適用ルールがある場合は一緒に返す。

        Args:
            project: プロジェクト名
            task_name: タスク名
            filename: 新しいファイル名
            content: ファイル内容
        """
        path = storage.create_file(project, task_name, filename, content)
        rules = storage.get_rules(project, task_name)
        result = f"ファイル '{filename}' を作成しました: {path}"
        if rules:
            result = f"{rules}\n\n---\n{result}"
        return result

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

    # --- ルールツール ---

    @mcp.tool()
    def get_rules(project: str | None = None, task_name: str | None = None) -> str:
        """適用ルールを取得する。

        全体 → プロジェクト → タスクの階層順でルールを収集して返す。
        引数の組み合わせで取得範囲が変わる:
        - 引数なし → 全体ルールのみ
        - project → 全体 + プロジェクトルール
        - project + task_name → 全体 + プロジェクト + タスクルール

        Args:
            project: プロジェクト名（省略時は全体ルールのみ）
            task_name: タスク名（省略時はタスクルールを含めない）
        """
        rules = storage.get_rules(project, task_name)
        if not rules:
            return "適用ルールはありません。"
        return rules

    @mcp.tool()
    def set_rules(
        content: str,
        project: str | None = None,
        task_name: str | None = None,
    ) -> str:
        """指定レベルのルール (RULES.md) を設定する。

        引数の組み合わせで対象レベルが変わる:
        - content のみ → 全体ルール (~/.taskmark/RULES.md)
        - content + project → プロジェクトルール
        - content + project + task_name → タスクルール

        Args:
            content: ルール内容
            project: プロジェクト名（省略時は全体ルール）
            task_name: タスク名（省略時はタスクルールを含めない）
        """
        path = storage.set_rules(content, project, task_name)
        if project and task_name:
            level = f"タスク '{task_name}'"
        elif project:
            level = f"プロジェクト '{project}'"
        else:
            level = "全体"
        return f"{level}ルールを設定しました: {path}"

    # --- gitツール ---

    @mcp.tool()
    def status() -> str:
        """~/.taskmark/ 内の未コミット変更一覧を取得する。"""
        result = storage.git_status()
        if not result:
            return "未コミットの変更はありません。"
        return result

    @mcp.tool()
    def commit(
        message: str,
        project: str | None = None,
        task_name: str | None = None,
    ) -> str:
        """~/.taskmark/ 内の変更をgitコミットする。

        明示的に指示されたときのみ使用すること。
        project や task_name を指定すると、その範囲のみコミットする。
        省略時は全変更をコミットする。

        Args:
            message: コミットメッセージ
            project: プロジェクト名（省略時は全変更）
            task_name: タスク名（省略時はプロジェクト全体）
        """
        result = storage.git_commit(message, project, task_name)
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
        return (
            f"テンプレート '{template}' にファイル '{filename}' を追加しました: {path}"
        )
