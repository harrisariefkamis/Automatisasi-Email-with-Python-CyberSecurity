"""Vercel entrypoint and deployment configuration smoke tests."""

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class VercelEntrypointTests(unittest.TestCase):
    def test_root_app_exports_handler(self):
        spec = importlib.util.spec_from_file_location("vercel_root_app", ROOT / "app.py")
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        self.assertTrue(callable(module.handler))

    def test_triage_exports_http_handler(self):
        spec = importlib.util.spec_from_file_location("vercel_triage", ROOT / "api" / "triage.py")
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        self.assertTrue(issubclass(module.handler, __import__("http.server").server.BaseHTTPRequestHandler))


if __name__ == "__main__":
    unittest.main()
