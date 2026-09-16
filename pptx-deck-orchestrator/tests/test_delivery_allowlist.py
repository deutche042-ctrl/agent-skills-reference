from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_ROOT / "scripts" / "validate_delivery.py"
SPEC = importlib.util.spec_from_file_location("validate_delivery", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class DeliveryAllowlistTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def make_file(self, name: str) -> Path:
        path = self.root / name
        path.touch()
        return path

    def test_exactly_one_pptx_passes(self) -> None:
        deck = self.make_file("deck.pptx")
        result = MODULE.validate_delivery([deck], expected_pptx=deck)
        self.assertTrue(result["allowed"])

    def test_uppercase_pptx_passes_case_insensitively(self) -> None:
        deck = self.make_file("deck.PPTX")
        result = MODULE.validate_delivery([deck], expected_pptx=deck)
        self.assertTrue(result["allowed"])

    def test_zero_planned_files_defaults_to_validated_pptx(self) -> None:
        deck = self.make_file("deck.pptx")
        result = MODULE.validate_delivery([], expected_pptx=deck)
        self.assertTrue(result["allowed"])
        self.assertEqual(result["user_visible_files"], [str(deck.resolve())])

    def test_two_planned_pptx_files_are_normalized_to_validated_pptx(self) -> None:
        first = self.make_file("first.pptx")
        second = self.make_file("second.pptx")
        result = MODULE.validate_delivery([first, second], expected_pptx=first)
        self.assertTrue(result["allowed"])
        self.assertEqual(result["user_visible_file_count"], 1)
        self.assertEqual(result["suppressed_user_visible_files"], [str(second)])

    def test_jpg_preview_is_independently_suppressed(self) -> None:
        deck = self.make_file("deck.pptx")
        preview = self.make_file("preview.jpg")
        result = MODULE.validate_delivery([preview], expected_pptx=deck)
        self.assertTrue(result["allowed"])
        self.assertEqual(result["user_visible_files"], [str(deck.resolve())])
        self.assertEqual(result["suppressed_user_visible_files"], [str(preview)])

    def test_jpeg_preview_is_independently_suppressed(self) -> None:
        deck = self.make_file("deck.pptx")
        preview = self.make_file("preview.JPEG")
        result = MODULE.validate_delivery([preview], expected_pptx=deck)
        self.assertTrue(result["allowed"])
        self.assertEqual(result["suppressed_user_visible_files"], [str(preview)])

    def test_pptx_plus_preview_keeps_only_pptx(self) -> None:
        deck = self.make_file("deck.pptx")
        preview = self.make_file("cover.jpeg")
        result = MODULE.validate_delivery([deck, preview], expected_pptx=deck)
        self.assertTrue(result["allowed"])
        self.assertEqual(result["user_visible_files"], [str(deck.resolve())])
        self.assertEqual(result["suppressed_user_visible_files"], [str(preview)])

    def test_other_preview_and_internal_formats_are_suppressed(self) -> None:
        deck = self.make_file("deck.pptx")
        for name in (
            "preview.png",
            "preview.webp",
            "preview.gif",
            "preview.svg",
            "slides.pdf",
            "qa-report.json",
            "thumbnail.pptx.jpg",
        ):
            with self.subTest(name=name):
                preview = self.make_file(name)
                result = MODULE.validate_delivery([preview], expected_pptx=deck)
                self.assertTrue(result["allowed"])
                self.assertEqual(result["suppressed_user_visible_files"], [str(preview)])

    def test_missing_pptx_is_blocked(self) -> None:
        result = MODULE.validate_delivery([self.root / "missing.pptx"])
        self.assertFalse(result["allowed"])
        self.assertIn("DELIVERY_PPTX_MISSING", {item["code"] for item in result["issues"]})

    def test_different_pptx_is_suppressed_in_favor_of_validated_artifact(self) -> None:
        validated = self.make_file("validated.pptx")
        other = self.make_file("other.pptx")
        result = MODULE.validate_delivery([other], expected_pptx=validated)
        self.assertTrue(result["allowed"])
        self.assertEqual(result["user_visible_files"], [str(validated.resolve())])
        self.assertEqual(result["suppressed_user_visible_files"], [str(other)])


if __name__ == "__main__":
    unittest.main()
