"""WCAG contrast tests for the palette.

A UI audit of every rendered widget found 25 of 140 text elements below WCAG
2.1 AA — the muted/secondary text ramp measured 2.3-2.7:1 against the dark
surfaces where a body-size requirement is 4.5:1. These tests pin the palette so
a future colour tweak cannot quietly walk it back. They are pure arithmetic on
the constants: no Tk, no display.
"""

import unittest

import WorkFacade as mmlb

AA_NORMAL = 4.5   # body text
AA_LARGE = 3.0    # >=18pt, or >=14pt bold

# Surfaces are split by what actually gets painted on them: the text ramp is
# used on page chrome, while cards only ever carry a title, a description and
# the mode's accent colour. Asserting the full cartesian product would tune the
# palette against pairings that never render.
PAGE_SURFACES = {
    "BG_DARK": mmlb.BG_DARK,
    "BG_INPUT": mmlb.BG_INPUT,
    "panel": "#0a0e17",
    "bi_page": "#070b14",
    "plot": "#05080f",
    "header": "#0d1220",
}
CARD_SURFACES = {
    "BG_CARD": mmlb.BG_CARD,
    "BG_CARD_HOVER": mmlb.BG_CARD_HOVER,   # hover and keyboard focus lighten it
}
SURFACES = dict(PAGE_SURFACES, **CARD_SURFACES)


def _rgb(value):
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def _luminance(color):
    def channel(v):
        v /= 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = _rgb(color)
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def contrast_ratio(fg, bg):
    """WCAG 2.1 relative contrast between two hex colours."""
    a, b = _luminance(fg), _luminance(bg)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


class ContrastHelperTests(unittest.TestCase):
    def test_known_ratios(self):
        self.assertAlmostEqual(contrast_ratio("#ffffff", "#000000"), 21.0, places=2)
        self.assertAlmostEqual(contrast_ratio("#000000", "#000000"), 1.0, places=2)
        self.assertAlmostEqual(contrast_ratio("#777777", "#ffffff"), 4.48, places=2)


class BodyTextContrastTests(unittest.TestCase):
    """Text tones must clear AA on every surface they are painted on."""

    BODY_TONES = ("TEXT_PRIMARY", "TEXT_SECONDARY", "TEXT_MUTED", "TEXT_DESC")

    def test_text_ramp_clears_aa_on_every_page_surface(self):
        for name in self.BODY_TONES:
            fg = getattr(mmlb, name)
            for surface, bg in PAGE_SURFACES.items():
                ratio = contrast_ratio(fg, bg)
                self.assertGreaterEqual(
                    ratio, AA_NORMAL,
                    f"{name} ({fg}) on {surface} ({bg}) is {ratio:.2f}:1, "
                    f"below the {AA_NORMAL}:1 needed for body text")

    def test_ramp_keeps_a_visible_hierarchy(self):
        """Muted must actually read as dimmer than secondary, and secondary
        than primary — otherwise the fix flattens the visual hierarchy."""
        muted = _luminance(mmlb.TEXT_MUTED)
        secondary = _luminance(mmlb.TEXT_SECONDARY)
        primary = _luminance(mmlb.TEXT_PRIMARY)
        self.assertLess(muted, secondary)
        self.assertLess(secondary, primary)


class CardAccentContrastTests(unittest.TestCase):
    """Each card paints its subtitle in the mode's accent colour at 9pt."""

    def test_every_card_accent_clears_aa_on_card_backgrounds(self):
        for sim in mmlb.SIMULATIONS:
            for bg_name, bg in CARD_SURFACES.items():
                ratio = contrast_ratio(sim["color"], bg)
                self.assertGreaterEqual(
                    ratio, AA_NORMAL,
                    f"{sim['id']} accent {sim['color']} on {bg_name} is "
                    f"{ratio:.2f}:1, below {AA_NORMAL}:1")

    def test_card_body_text_clears_aa_on_card_backgrounds(self):
        """Titles and descriptions have to survive the hover/focus lift too."""
        for name in ("TEXT_PRIMARY", "TEXT_DESC"):
            fg = getattr(mmlb, name)
            for bg_name, bg in CARD_SURFACES.items():
                ratio = contrast_ratio(fg, bg)
                self.assertGreaterEqual(
                    ratio, AA_NORMAL,
                    f"{name} ({fg}) on {bg_name} is {ratio:.2f}:1")


class AccentContrastTests(unittest.TestCase):
    """Accents used for headings and status text, at large sizes (AA >= 3.0)."""

    ACCENTS = ("ACCENT", "CYAN_ACCENT", "RED_ACCENT", "YELLOW_ACCENT",
               "BLUE_ACCENT", "ORANGE_ACCENT", "PURPLE_ACCENT",
               "MAGENTA_ACCENT", "MATRIX_GREEN")

    def test_accents_clear_large_text_threshold(self):
        for name in self.ACCENTS:
            fg = getattr(mmlb, name)
            for surface, bg in SURFACES.items():
                ratio = contrast_ratio(fg, bg)
                self.assertGreaterEqual(
                    ratio, AA_LARGE,
                    f"{name} ({fg}) on {surface} is {ratio:.2f}:1, "
                    f"below {AA_LARGE}:1 for large text")


if __name__ == "__main__":
    unittest.main()
