import os
import sys
import unittest
from pathlib import Path
import shutil


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


class EnvLoaderTests(unittest.TestCase):
    def setUp(self):
        self.temp_root = (
            Path(__file__).resolve().parents[1] / f".tmp_test_env_loader_{self._testMethodName}"
        )
        if self.temp_root.exists():
            shutil.rmtree(self.temp_root, ignore_errors=True)
        self.temp_root.mkdir(exist_ok=True)

    def tearDown(self):
        if self.temp_root.exists():
            shutil.rmtree(self.temp_root, ignore_errors=True)

    def test_loads_env_from_repo_root(self):
        root = self.temp_root
        scripts_dir = root / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        env_path = root / ".env"
        env_path.write_text("GEMINI_API_KEY=test-key\n", encoding="utf-8")

        from env_loader import load_project_env

        os.environ.pop("GEMINI_API_KEY", None)
        loaded = load_project_env(scripts_dir / "generate_mondo_enhanced.py")

        self.assertTrue(loaded)
        self.assertEqual(os.environ.get("GEMINI_API_KEY"), "test-key")

    def test_does_not_override_existing_environment(self):
        root = self.temp_root
        scripts_dir = root / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        env_path = root / ".env"
        env_path.write_text("GEMINI_API_KEY=file-key\n", encoding="utf-8")

        from env_loader import load_project_env

        original = os.environ.get("GEMINI_API_KEY")
        os.environ["GEMINI_API_KEY"] = "existing-key"
        try:
            loaded = load_project_env(scripts_dir / "generate_mondo_enhanced.py")
            self.assertTrue(loaded)
            self.assertEqual(os.environ.get("GEMINI_API_KEY"), "existing-key")
        finally:
            if original is None:
                os.environ.pop("GEMINI_API_KEY", None)
            else:
                os.environ["GEMINI_API_KEY"] = original


if __name__ == "__main__":
    unittest.main()
