#!/usr/bin/env python3
"""Regression checks for the November 2026 editorial workflow update.
Run from the repository root: python3 tests/test-skill-updates.py
No external dependencies or network access required.
"""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEO = ROOT / ".claude/skills/ai-assisted-blog-post/scripts/check-seo.py"
ID_CHECK = ROOT / ".claude/skills/bahasa-indonesia/scripts/cek.py"

class SkillUpdateTests(unittest.TestCase):
    def run_checker(self, checker, text):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "2020-01-01-review-example.md"
            path.write_text(text, encoding="utf-8")
            result = subprocess.run([sys.executable, str(checker), str(path)],
                                    text=True, capture_output=True)
            self.assertNotIn("Traceback", result.stderr)
            return result

    def fixture(self, words=50, description=120, keywords=3):
        terms = ", ".join("topic " + str(i) for i in range(keywords))
        summary = "**In short:** " + " ".join(["word"] * (words - 2))
        return ("---\n" +
                "title: \"A clear statement heading\"\n" +
                "description: \"" + "d" * description + "\"\n" +
                "date: 2020-01-01 09:00:00 +0800\n" +
                "tags: [finance]\nkeywords: [" + terms + "]\n---\n\n" +
                summary + "\n{: .tldr}\n\n## A statement\nUseful prose.\n")

    def test_summary_boundaries(self):
        for words in (40, 90):
            out = self.run_checker(SEO, self.fixture(words=words)).stdout
            self.assertNotIn("the In short block is", out)
        for words in (39, 91):
            out = self.run_checker(SEO, self.fixture(words=words)).stdout
            self.assertIn("the In short block is " + str(words) + " words", out)

    def test_description_boundaries(self):
        for count in (110, 160):
            out = self.run_checker(SEO, self.fixture(description=count)).stdout
            self.assertNotIn("description is", out)
        for count in (109, 161):
            out = self.run_checker(SEO, self.fixture(description=count)).stdout
            self.assertIn(str(count) + " characters", out)
            self.assertIn("WARN: description is", out)

    def test_keyword_upper_bound(self):
        self.assertNotIn("keywords: target", self.run_checker(SEO, self.fixture(keywords=8)).stdout)
        self.assertIn("9 keywords: target", self.run_checker(SEO, self.fixture(keywords=9)).stdout)

    def test_no_heading_or_section_quota(self):
        out = self.run_checker(SEO, self.fixture()).stdout
        self.assertNotIn("section headings are questions", out)
        self.assertNotIn("only 1 sections", out)

    def test_percentage_points_are_valid(self):
        result = self.run_checker(ID_CHECK,
            "Selisih kedua suku bunga itu adalah satu poin persentase.\n")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertNotIn("known calque", result.stdout)

    def test_existing_indonesian_rules_remain(self):
        for text in ("Anda perlu membaca angka itu dengan teliti.\n", "Jawabannya gak.\n"):
            result = self.run_checker(ID_CHECK, text)
            self.assertEqual(result.returncode, 1, result.stdout)
            self.assertIn("ERROR", result.stdout)

    def test_all_python_sources_compile(self):
        for path in ROOT.glob(".claude/**/*.py"):
            compile(path.read_text(encoding="utf-8"), str(path), "exec")

    def test_workflow_requirements_and_references(self):
        workflow = (ROOT / ".claude/skills/ai-assisted-blog-post/SKILL.md").read_text()
        for text in ("Primary intention has no silent default", "Tone and wording choices",
                     "Evidence ledger", "Substantive review, all languages", "Persist explicit preferences"):
            self.assertIn(text, workflow)
        for relative in (
            ".claude/skills/adjie-writing-style/references/editorial-safeguards.md",
            ".claude/skills/adjie-writing-style/references/voice-preferences.md",
            ".claude/skills/bahasa-indonesia/references/word-preferences.md",
            ".claude/agents/substantive-editor.md"):
            self.assertTrue((ROOT / relative).is_file(), relative)

if __name__ == "__main__":
    unittest.main(verbosity=2)
