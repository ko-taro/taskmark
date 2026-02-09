"""Taskmarkのストレージ操作 (~/.taskmark/ のファイル・ディレクトリ管理)"""

import shutil
import subprocess
from pathlib import Path

from taskmark.models import DEFAULT_TEMPLATE_CONTENT, render_template

BASE_DIR = Path.home() / ".taskmark"
TEMPLATES_DIR = BASE_DIR / "templates"
PROJECTS_DIR = BASE_DIR / "projects"
TEMP_DIR = BASE_DIR / ".tmp"


def _run_git(*args: str) -> subprocess.CompletedProcess[str]:
    """~/.taskmark/ 内で git コマンドを実行する"""
    return subprocess.run(
        ["git", *args],
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
        check=True,
    )


def ensure_base_dirs() -> None:
    """ベースディレクトリとデフォルトテンプレートを作成する（未作成の場合）"""
    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    PROJECTS_DIR.mkdir(parents=True, exist_ok=True)

    # git init（未初期化の場合のみ）
    if not (BASE_DIR / ".git").exists():
        _run_git("init")
        gitignore = BASE_DIR / ".gitignore"
        gitignore.write_text(".tmp/\n", encoding="utf-8")

    default_template_dir = TEMPLATES_DIR / "default"
    if not default_template_dir.exists():
        default_template_dir.mkdir()
        (default_template_dir / "task.md").write_text(
            DEFAULT_TEMPLATE_CONTENT, encoding="utf-8"
        )


# --- プロジェクト操作 ---


def list_projects() -> list[str]:
    """プロジェクト名の一覧を返す"""
    ensure_base_dirs()
    return sorted(d.name for d in PROJECTS_DIR.iterdir() if d.is_dir())


def create_project(name: str) -> Path:
    """新しいプロジェクトディレクトリを作成する。パスを返す。"""
    ensure_base_dirs()
    project_dir = PROJECTS_DIR / name
    if project_dir.exists():
        raise FileExistsError(f"プロジェクト '{name}' は既に存在します")
    project_dir.mkdir()
    return project_dir


def delete_project(name: str) -> None:
    """プロジェクトとその全タスクを削除する"""
    project_dir = PROJECTS_DIR / name
    if not project_dir.exists():
        raise FileNotFoundError(f"プロジェクト '{name}' が見つかりません")
    shutil.rmtree(project_dir)


# --- タスク操作 ---


def _project_dir(project: str) -> Path:
    path = PROJECTS_DIR / project
    if not path.is_dir():
        raise FileNotFoundError(f"プロジェクト '{project}' が見つかりません")
    return path


def list_tasks(project: str) -> list[str]:
    """プロジェクト内のタスク名一覧を返す"""
    project_dir = _project_dir(project)
    return sorted(d.name for d in project_dir.iterdir() if d.is_dir())


def create_task(
    project: str, task_name: str, title: str, template: str = "default"
) -> Path:
    """テンプレートから新しいタスクディレクトリを作成する。パスを返す。"""
    project_dir = _project_dir(project)
    task_dir = project_dir / task_name
    if task_dir.exists():
        raise FileExistsError(
            f"タスク '{task_name}' はプロジェクト '{project}' に既に存在します"
        )

    template_dir = TEMPLATES_DIR / template
    if not template_dir.is_dir():
        raise FileNotFoundError(f"テンプレート '{template}' が見つかりません")

    task_dir.mkdir()

    # テンプレートファイルをコピーしてプレースホルダを置換
    for template_file in template_dir.iterdir():
        if template_file.is_file():
            content = template_file.read_text(encoding="utf-8")
            rendered = render_template(content, title)
            (task_dir / template_file.name).write_text(rendered, encoding="utf-8")

    return task_dir


def delete_task(project: str, task_name: str) -> None:
    """タスクディレクトリを削除する"""
    task_dir = _project_dir(project) / task_name
    if not task_dir.is_dir():
        raise FileNotFoundError(
            f"タスク '{task_name}' がプロジェクト '{project}' に見つかりません"
        )
    shutil.rmtree(task_dir)


# --- タスク内ファイル操作 ---


def _task_dir(project: str, task_name: str) -> Path:
    path = _project_dir(project) / task_name
    if not path.is_dir():
        raise FileNotFoundError(
            f"タスク '{task_name}' がプロジェクト '{project}' に見つかりません"
        )
    return path


def list_files(project: str, task_name: str) -> list[str]:
    """タスクディレクトリ内のファイル一覧を返す"""
    task_dir = _task_dir(project, task_name)
    return sorted(f.name for f in task_dir.iterdir() if f.is_file())


def get_file(project: str, task_name: str, filename: str) -> str:
    """タスクディレクトリ内のファイルを読み取る"""
    file_path = _task_dir(project, task_name) / filename
    if not file_path.is_file():
        raise FileNotFoundError(
            f"ファイル '{filename}' がタスク '{task_name}' に見つかりません"
        )
    return file_path.read_text(encoding="utf-8")


def update_file(
    project: str, task_name: str, filename: str, content: str
) -> tuple[Path, Path]:
    """タスクディレクトリ内のファイルを上書き更新する。変更前・変更後のファイルパスを返す。"""
    file_path = _task_dir(project, task_name) / filename
    if not file_path.is_file():
        raise FileNotFoundError(
            f"ファイル '{filename}' がタスク '{task_name}' に見つかりません"
        )
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    old_path = TEMP_DIR / f"{project}_{task_name}_{filename}"
    old_path.write_text(file_path.read_text(encoding="utf-8"), encoding="utf-8")
    file_path.write_text(content, encoding="utf-8")
    return old_path, file_path


def create_file(project: str, task_name: str, filename: str, content: str) -> Path:
    """タスクディレクトリ内に新しいファイルを作成する"""
    file_path = _task_dir(project, task_name) / filename
    if file_path.exists():
        raise FileExistsError(
            f"ファイル '{filename}' はタスク '{task_name}' に既に存在します"
        )
    file_path.write_text(content, encoding="utf-8")
    return file_path


def delete_file(project: str, task_name: str, filename: str) -> None:
    """タスクディレクトリ内のファイルを削除する"""
    file_path = _task_dir(project, task_name) / filename
    if not file_path.is_file():
        raise FileNotFoundError(
            f"ファイル '{filename}' がタスク '{task_name}' に見つかりません"
        )
    file_path.unlink()


# --- テンプレート操作 ---


def list_templates() -> list[str]:
    """テンプレート名の一覧を返す"""
    ensure_base_dirs()
    return sorted(d.name for d in TEMPLATES_DIR.iterdir() if d.is_dir())


def create_template(name: str) -> Path:
    """新しい空のテンプレートディレクトリを作成する"""
    ensure_base_dirs()
    template_dir = TEMPLATES_DIR / name
    if template_dir.exists():
        raise FileExistsError(f"テンプレート '{name}' は既に存在します")
    template_dir.mkdir()
    return template_dir


def git_status() -> str:
    """~/.taskmark/ 内の未コミット変更を返す。"""
    result = _run_git("status", "--short")
    return result.stdout.strip()


def git_commit(message: str) -> str:
    """~/.taskmark/ 内の全変更をステージしてコミットする。結果メッセージを返す。"""
    _run_git("add", "-A")
    try:
        result = _run_git("commit", "-m", message)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        if "nothing to commit" in e.stdout:
            return ""
        raise


def revert_file(project: str, task_name: str, filename: str) -> None:
    """tmpから変更前のファイルを復元する"""
    tmp_path = TEMP_DIR / f"{project}_{task_name}_{filename}"
    if not tmp_path.is_file():
        raise FileNotFoundError(
            f"ファイル '{filename}' の変更前データがtmpに見つかりません"
        )
    file_path = _task_dir(project, task_name) / filename
    file_path.write_text(tmp_path.read_text(encoding="utf-8"), encoding="utf-8")
    tmp_path.unlink()


def tmp_stats() -> dict:
    """tmpディレクトリのファイル数と合計サイズを返す"""
    if not TEMP_DIR.exists():
        return {"file_count": 0, "total_bytes": 0}
    files = [f for f in TEMP_DIR.iterdir() if f.is_file()]
    total_bytes = sum(f.stat().st_size for f in files)
    return {"file_count": len(files), "total_bytes": total_bytes}


def clear_tmp() -> int:
    """tmpディレクトリ内の全ファイルを削除する。削除したファイル数を返す。"""
    if not TEMP_DIR.exists():
        return 0
    files = [f for f in TEMP_DIR.iterdir() if f.is_file()]
    for f in files:
        f.unlink()
    return len(files)


def add_template_file(template: str, filename: str, content: str) -> Path:
    """テンプレートディレクトリにファイルを追加する"""
    template_dir = TEMPLATES_DIR / template
    if not template_dir.is_dir():
        raise FileNotFoundError(f"テンプレート '{template}' が見つかりません")
    file_path = template_dir / filename
    file_path.write_text(content, encoding="utf-8")
    return file_path
