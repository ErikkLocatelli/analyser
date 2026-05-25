from pathlib import Path
import tempfile
import subprocess
import os

DEBUG = False

BASE_DIR = Path(__file__).resolve().parent.parent
TEMP_DIR = BASE_DIR / "temp"

TEMP_DIR.mkdir(exist_ok=True)

def clone_repo(repo_url: str):

    if DEBUG:

        temp_dir = tempfile.mkdtemp(dir=TEMP_DIR)

        auto_cleanup = False

    else:

        temp_dir_obj = tempfile.TemporaryDirectory()

        temp_dir = temp_dir_obj.name

        auto_cleanup = True

    repo_path = os.path.join(temp_dir, "repo")

    try:

        subprocess.run(
            ["git", "clone", "-c", "core.longpaths=true", "--depth", "1", repo_url, repo_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=60
        )

        return {
            "repo_path": repo_path,
            "temp_dir": temp_dir,
            "temp_dir_obj": temp_dir_obj if auto_cleanup else None,
            "auto_cleanup": auto_cleanup
        }

    except subprocess.CalledProcessError as err:

        if auto_cleanup:
            temp_dir_obj.cleanup()

        raise Exception(
            f"Erro ao clonar repositório: {err.stderr}"
        )