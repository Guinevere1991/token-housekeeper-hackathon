"""Pre-install disclosure is visible in both public documentation surfaces."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PreinstallDisclosureTests(unittest.TestCase):
    def test_installable_subtree_has_catalog_readme(self):
        readme = ROOT / "plugin" / "README.md"
        self.assertTrue(readme.is_file(), "catalog subdir needs an actual README")
        text = readme.read_text(encoding="utf-8")
        for phrase in (
            "pre_llm_call", "nearly every substantive text request",
            "additional tool call", "No runtime network calls",
            "No reads outside", "No shell commands", "No background processes",
            "No stored credentials", "No telemetry", "No open-source license",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_repository_readme_discloses_hook_frequency_and_test_inventory(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("nearly every substantive text request", text)
        self.assertIn("additional tool call", text)
        self.assertIn("tests/test_navigator_language.py", text)
        self.assertNotIn("contains only the installable runtime package and this readme", text)


if __name__ == "__main__":
    unittest.main()
