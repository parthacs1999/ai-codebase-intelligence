import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlparse


def validate_github_url(url):
    parsed = urlparse(url)

    if parsed.scheme != "https":
        raise ValueError("Only HTTPS GitHub URLs are supported")

    if parsed.hostname != "github.com":
        raise ValueError("Only github.com repositories are supported")

    parts = parsed.path.strip("/").split("/")

    if len(parts) != 2 or not all(parts):
        raise ValueError("Expected URL: https://github.com/owner/repository")

    owner, repository = parts
    repository = repository.removesuffix(".git")

    if not repository:
        raise ValueError("Invalid repository name")

    if not all(
        value.replace("-", "").replace("_", "").replace(".", "").isalnum()
        for value in (owner, repository)
    ):
        raise ValueError("Invalid GitHub repository path")

    return f"https://github.com/{owner}/{repository}.git"


def prepare_repository(source):
    if source.startswith("https://"):
        clone_url = validate_github_url(source)
        workspace = tempfile.mkdtemp(prefix="codebase_ai_")
        destination = os.path.join(workspace, "repository")

        try:
            subprocess.run(
                [
                    "git",
                    "clone",
                    "--depth",
                    "1",
                    "--single-branch",
                    clone_url,
                    destination
                ],
                check=True,
                timeout=120,
                capture_output=True,
                text=True,
                env={
                    **os.environ,
                    "GIT_TERMINAL_PROMPT": "0",
                    "GIT_LFS_SKIP_SMUDGE": "1"
                }
            )

            return destination, workspace

        except Exception:
            shutil.rmtree(workspace, ignore_errors=True)
            raise

    path = Path(source).expanduser().resolve()

    if not path.is_dir():
        raise ValueError("Local repository path does not exist")

    return str(path), None


def cleanup_repository(workspace):
    if workspace:
        shutil.rmtree(workspace, ignore_errors=True)