import os
from pathlib import Path


def load_project_env(start_path=None, filename=".env"):
    """Load simple KEY=VALUE pairs from the nearest repo-root .env file."""
    current = Path(start_path or __file__).resolve()
    base = current.parent if current.is_file() else current

    for directory in (base, *base.parents):
        env_path = directory / filename
        if env_path.is_file():
            for raw_line in env_path.read_text(encoding="utf-8").splitlines():
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue

                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                os.environ.setdefault(key, value)
            return True
    return False
