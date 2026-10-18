import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("fakett_release_audit", ROOT / "scripts" / "audit_release.py")
assert SPEC and SPEC.loader
release_audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release_audit)


class ReleaseAuditTests(unittest.TestCase):
    def test_allows_invented_data_in_synthetic_tree(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            csv_path = root / "data" / "synthetic" / "demo.csv"
            csv_path.parent.mkdir(parents=True)
            csv_path.write_text("sample_id,split,label\nmade-up-1,train,real\n", encoding="utf-8")
            self.assertEqual(release_audit.audit(root), [])

    def test_flags_data_outside_synthetic_tree(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data_path = root / "data" / "raw" / "examples.csv"
            data_path.parent.mkdir(parents=True)
            data_path.write_text("restricted material", encoding="utf-8")
            problems = release_audit.audit(root)
            self.assertTrue(any("restricted data directory" in issue for issue in problems))
            self.assertTrue(any("non-synthetic data tree" in issue for issue in problems))

    def test_flags_access_controlled_directory_anywhere(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            media = root / "assets" / "keyframes" / "frame.png"
            media.parent.mkdir(parents=True)
            media.write_bytes(b"not checked as a real image")
            problems = release_audit.audit(root)
            self.assertTrue(any("restricted data directory" in issue for issue in problems))


if __name__ == "__main__":
    unittest.main()
