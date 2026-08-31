"""Regression tests for defects found during UAT.

Each test here pins a specific failure that shipped once. All are headless:
importing WorkFacade creates no Tk root, and nothing below opens a window.
"""

import unittest

import WorkFacade as mmlb


class TkTextEncodabilityTests(unittest.TestCase):
    """Strings handed to Tk must survive encoding to UTF-8.

    DOCS_TEXT once contained an emoji written as a UTF-16 surrogate PAIR
    ("\\ud83c\\udfb2"). Python reads that as two unpaired surrogates, which
    cannot be encoded when the string is passed to Tcl, so inserting the text
    raised UnicodeEncodeError and the Documentation mode silently did nothing.
    """

    def _assert_encodable(self, text, label):
        try:
            text.encode("utf-8")
        except UnicodeEncodeError as exc:
            self.fail(f"{label} is not UTF-8 encodable ({exc}); "
                      f"a lone surrogate will crash the Tk widget it goes into")

    def test_docs_text_is_encodable(self):
        self._assert_encodable(mmlb.DOCS_TEXT, "DOCS_TEXT")

    def test_docs_text_has_no_lone_surrogates(self):
        bad = [(i, hex(ord(c))) for i, c in enumerate(mmlb.DOCS_TEXT)
               if 0xD800 <= ord(c) <= 0xDFFF]
        self.assertEqual(bad, [], f"lone surrogates in DOCS_TEXT at {bad}")

    def test_simulation_card_strings_are_encodable(self):
        for sim in mmlb.SIMULATIONS:
            for field in ("icon", "title", "subtitle", "desc"):
                self._assert_encodable(sim[field], f"{sim['id']}.{field}")

    def test_bi_lesson_strings_are_encodable(self):
        for lesson in mmlb.BI_LESSONS:
            for field in ("title", "family", "question", "pitfall", "lang", "code"):
                self._assert_encodable(lesson[field], f"{lesson['chart']}.{field}")
            for rule in lesson["read"]:
                self._assert_encodable(rule, f"{lesson['chart']}.read")
            for line in lesson["insights"]:
                self._assert_encodable(line, f"{lesson['chart']}.insights")


class UsableKeysTests(unittest.TestCase):
    """F13-F15 are advertised by pyautogui but map to keycode 0 on X11 layouts
    that stop at F12. Pressing an unmapped keycode raises an X protocol error
    and can wedge the Xlib connection, which silently killed key injection."""

    def test_returns_a_non_empty_subset_of_harmless_keys(self):
        keys = mmlb.usable_keys()
        self.assertTrue(keys, "keep-alive must always have at least one key")
        self.assertTrue(set(keys).issubset(mmlb.HARMLESS_KEYS))
        for key in keys:
            self.assertIsInstance(key, str)

    def test_engine_uses_the_filtered_key_list(self):
        eng = mmlb.KeepAliveEngine()
        self.assertTrue(eng.keys)
        self.assertTrue(set(eng.keys).issubset(mmlb.HARMLESS_KEYS))

    def test_falls_back_to_full_list_without_pyautogui(self):
        saved = mmlb.pyautogui
        mmlb.pyautogui = None
        try:
            self.assertEqual(mmlb.usable_keys(), list(mmlb.HARMLESS_KEYS))
        finally:
            mmlb.pyautogui = saved


class DurationLabelTests(unittest.TestCase):
    """Integer-dividing seconds by 3600 rendered every sub-hour run as '0h'."""

    def test_sub_hour_durations_read_in_minutes(self):
        self.assertEqual(mmlb._format_duration(60), "1m")
        self.assertEqual(mmlb._format_duration(1800), "30m")
        self.assertEqual(mmlb._format_duration(3540), "59m")

    def test_whole_hours(self):
        self.assertEqual(mmlb._format_duration(3600), "1h")
        self.assertEqual(mmlb._format_duration(7200), "2h")

    def test_mixed_hours_and_minutes(self):
        self.assertEqual(mmlb._format_duration(5400), "1h30m")
        self.assertEqual(mmlb._format_duration(9000), "2h30m")

    def test_never_renders_zero(self):
        self.assertEqual(mmlb._format_duration(30), "1m")
        self.assertEqual(mmlb._format_duration(1), "1m")


class ImportGuardTests(unittest.TestCase):
    """pyautogui's import chain reads os.environ['DISPLAY'] and raises KeyError
    on a headless box, so the guard must be broader than ImportError."""

    def test_module_imports_without_a_display(self):
        # Reaching this line at all means the module imported successfully in
        # whatever environment the suite runs in, headless included.
        self.assertTrue(hasattr(mmlb, "keep_alive"))
        self.assertIn(mmlb.pyautogui, (None, mmlb.pyautogui))

    def test_engine_degrades_when_pyautogui_is_absent(self):
        saved = mmlb.pyautogui
        mmlb.pyautogui = None
        try:
            eng = mmlb.KeepAliveEngine()
            self.assertFalse(eng.available)
            eng._do_mouse()     # must be a no-op, not an AttributeError
            eng._do_key()
            self.assertEqual(eng.mouse_moves, 0)
            self.assertEqual(eng.key_presses, 0)
        finally:
            mmlb.pyautogui = saved


if __name__ == "__main__":
    unittest.main()
