from __future__ import annotations

from pathlib import Path
import unittest


SKILL_ROOT = Path(__file__).resolve().parents[1]


class SkillContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        cls.interface = (SKILL_ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        cls.lite = (SKILL_ROOT / "scripts" / "qa_lite.py").read_text(encoding="utf-8")
        cls.mid = (SKILL_ROOT / "scripts" / "qa_mid.py").read_text(encoding="utf-8")
        cls.frontmatter = cls.skill.split("---", 2)[1]
        cls.opening = cls.skill.split("## Finish and deliver", 1)[0]

    def test_public_identity_is_pptx_generation(self) -> None:
        self.assertIn("name: pptx-deck-orchestrator", self.skill)
        self.assertIn("Create and edit polished, editable PowerPoint presentations", self.frontmatter)
        self.assertIn("Produce the actual presentation file", self.frontmatter)

    def test_trigger_and_interface_do_not_position_the_skill_as_qa(self) -> None:
        public_text = f"{self.frontmatter}\n{self.interface}".lower()
        for phrase in ("qa", "quality assurance", "validation", "validator", "gate"):
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, public_text)

    def test_opening_is_about_making_the_deck(self) -> None:
        self.assertNotIn("QA", self.opening)
        self.assertIn("Create one strong, editable `.pptx`", self.opening)
        self.assertIn("The requested deliverable is the actual presentation", self.opening)

    def test_generation_precedes_internal_final_check(self) -> None:
        self.assertIn("## Generate the deck", self.skill)
        self.assertLess(
            self.skill.index("## Generate the deck"),
            self.skill.index("## Finish and deliver"),
        )
        self.assertLess(
            self.skill.index("## Generate the deck"),
            self.skill.index("## Run one internal final check"),
        )
        self.assertIn("Build the actual presentation", self.skill)
        self.assertIn("opens as a PPTX", self.skill)

    def test_body_has_no_cost_or_version_maintenance_bias(self) -> None:
        for phrase in (
            "Keep the original",
            "final validation layer",
            "delivery allowlist",
            "minimizing QA time",
            "tool calls",
            "review tokens",
            "elapsed time",
            "compact working notes",
            "one small visual system",
            "hash-keyed",
        ):
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, self.skill)

    def test_body_has_no_unrelated_skill_or_audit_routing(self) -> None:
        self.assertNotIn("another skill", self.skill)
        self.assertNotIn("PPTX Max", self.skill)
        self.assertNotIn("pptx-max", self.skill)
        self.assertNotIn("evidence ledger", self.skill)

    def test_default_prompt_asks_for_a_real_deck_first(self) -> None:
        self.assertIn("$pptx-deck-orchestrator", self.interface)
        self.assertIn("create a polished, editable PowerPoint presentation", self.interface)

    def test_final_delivery_is_a_positive_allowlist(self) -> None:
        self.assertIn("exactly one user-visible file", self.skill)
        self.assertIn("end in `.pptx` case-insensitively", self.skill)

    def test_jpg_and_jpeg_are_explicitly_internal(self) -> None:
        self.assertIn("JPEG/JPG", self.skill)
        self.assertIn("PNG", self.skill)

    def test_both_profiles_require_delivery_preflight(self) -> None:
        for source in (self.lite, self.mid):
            with self.subTest(profile="lite" if source is self.lite else "mid"):
                self.assertIn("validate_delivery", source)
                self.assertIn("--user-visible-file", source)
                self.assertIn('"delivery_check"', source)

    def test_internal_checks_do_not_replace_generation(self) -> None:
        self.assertIn(
            "These checks inspect a finished candidate; they do not create or replace the presentation",
            self.skill,
        )

    def test_lite_does_not_discourage_needed_repair_runs(self) -> None:
        self.assertNotIn("Run once after a coherent candidate exists", self.skill)
        self.assertNotIn("Inspect the 60 DPI montage once", self.skill)
        self.assertIn(
            "If the candidate changes during repair, rerun the same profile on the changed file",
            self.skill,
        )

    def test_delivery_waits_for_internal_final_check(self) -> None:
        self.assertIn("Treat the generated PPTX as an internal candidate", self.skill)
        self.assertIn("Do not attach, link, upload", self.skill)
        self.assertIn("status=PASS", self.skill)
        self.assertIn("If the final check is incomplete or fails", self.skill)


if __name__ == "__main__":
    unittest.main()
