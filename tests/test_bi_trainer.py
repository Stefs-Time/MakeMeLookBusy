"""Headless tests for THE BI TRAINER lesson deck.

The trainer's content lives in module-level data (``BI_LESSONS``) and its
charts are drawn by ``_draw_<chart>`` methods, so both can drift apart
silently. These tests keep the deck, the renderers, and the data generator
consistent without needing a display: nothing here creates a Tk widget.
"""

import unittest

import WorkFacade as mmlb


class LessonDeckTests(unittest.TestCase):
    REQUIRED = {"chart", "title", "family", "question", "read",
                "pitfall", "lang", "code", "insights"}

    def test_deck_is_not_empty(self):
        self.assertGreaterEqual(len(mmlb.BI_LESSONS), 1)

    def test_every_lesson_has_required_fields(self):
        for lesson in mmlb.BI_LESSONS:
            missing = self.REQUIRED - set(lesson)
            self.assertFalse(missing, f"{lesson.get('title')} missing {missing}")

    def test_every_lesson_has_a_renderer(self):
        for lesson in mmlb.BI_LESSONS:
            self.assertTrue(
                hasattr(mmlb.BITrainerSimulation, "_draw_" + lesson["chart"]),
                f"no _draw_{lesson['chart']} for {lesson['title']}",
            )

    def test_chart_ids_are_unique(self):
        charts = [lesson["chart"] for lesson in mmlb.BI_LESSONS]
        self.assertEqual(len(charts), len(set(charts)))

    def test_interpretation_and_insight_lists_are_populated(self):
        for lesson in mmlb.BI_LESSONS:
            self.assertGreaterEqual(len(lesson["read"]), 3, lesson["title"])
            self.assertTrue(lesson["insights"], lesson["title"])
            for rule in lesson["read"]:
                self.assertIsInstance(rule, str)
                self.assertTrue(rule.strip())

    def test_code_samples_are_multi_line_snippets(self):
        for lesson in mmlb.BI_LESSONS:
            self.assertGreaterEqual(len(lesson["code"].split("\n")), 4,
                                    lesson["title"])

    def test_feed_chatter_is_populated(self):
        self.assertTrue(mmlb.BI_FEED_CHATTER)
        for line in mmlb.BI_FEED_CHATTER:
            self.assertIsInstance(line, str)


class LessonDataTests(unittest.TestCase):
    """``_make_data`` is pure and instance-independent, so call it unbound."""

    def _data_for(self, chart):
        return mmlb.BITrainerSimulation._make_data(None, chart)

    def test_every_chart_type_generates_data(self):
        for lesson in mmlb.BI_LESSONS:
            data = self._data_for(lesson["chart"])
            self.assertIsInstance(data, dict)
            self.assertTrue(data, f"{lesson['chart']} generated no data")

    def test_generated_data_is_shaped_as_the_renderers_expect(self):
        expected = {
            "bar": {"labels", "values"},
            "line": {"series"},
            "stacked_area": {"names", "stacks"},
            "donut": {"names", "pcts"},
            "scatter": {"points", "r"},
            "histogram": {"bins", "median_bin"},
            "heatmap": {"rows", "cells", "cols"},
            "box": {"groups"},
            "waterfall": {"start", "steps", "end"},
            "funnel": {"names", "counts"},
            "pareto": {"names", "values", "cum"},
            "kpi": {"tiles"},
        }
        for chart, keys in expected.items():
            self.assertTrue(keys.issubset(self._data_for(chart)), chart)

    def test_bar_values_are_sorted_descending(self):
        values = self._data_for("bar")["values"]
        self.assertEqual(values, sorted(values, reverse=True))

    def test_donut_slices_sum_to_one_hundred_percent(self):
        pcts = self._data_for("donut")["pcts"]
        self.assertAlmostEqual(sum(pcts), 100.0, places=6)

    def test_funnel_stages_never_widen(self):
        counts = self._data_for("funnel")["counts"]
        for prev, cur in zip(counts, counts[1:]):
            self.assertLess(cur, prev)

    def test_pareto_cumulative_reaches_one_hundred(self):
        data = self._data_for("pareto")
        self.assertEqual(len(data["cum"]), len(data["values"]))
        self.assertAlmostEqual(data["cum"][-1], 100.0, places=6)
        self.assertEqual(data["cum"], sorted(data["cum"]))

    def test_waterfall_bridge_reconciles(self):
        data = self._data_for("waterfall")
        bridged = data["start"] + sum(delta for _, delta in data["steps"])
        self.assertAlmostEqual(bridged, data["end"], places=6)

    def test_unknown_chart_type_returns_empty_data(self):
        self.assertEqual(self._data_for("no-such-chart"), {})


class TrainerConfigTests(unittest.TestCase):
    def test_trainer_is_registered_as_a_timed_mode(self):
        cls, takes_duration = mmlb.Launcher.SIM_REGISTRY["bi_trainer"]
        self.assertIs(cls, mmlb.BITrainerSimulation)
        self.assertTrue(takes_duration)

    def test_timings_are_sane(self):
        sim = mmlb.BITrainerSimulation
        self.assertGreater(sim.LESSON_SECONDS, sim.ENTRANCE_SECONDS)
        # Every rule (plus the closing pitfall) must appear before the
        # lesson auto-advances, or the panel is never fully readable.
        longest = max(len(lesson["read"]) for lesson in mmlb.BI_LESSONS)
        self.assertLess((longest + 1) * sim.RULE_MS / 1000.0, sim.LESSON_SECONDS)

    def test_colour_blend_endpoints_and_clamping(self):
        self.assertEqual(mmlb._bi_mix("#000000", "#ffffff", 0.0), "#000000")
        self.assertEqual(mmlb._bi_mix("#000000", "#ffffff", 1.0), "#ffffff")
        self.assertEqual(mmlb._bi_mix("#000000", "#ffffff", 0.5), "#7f7f7f")
        # Out-of-range factors clamp instead of producing invalid colours.
        self.assertEqual(mmlb._bi_mix("#000000", "#ffffff", -3.0), "#000000")
        self.assertEqual(mmlb._bi_mix("#000000", "#ffffff", 9.0), "#ffffff")


if __name__ == "__main__":
    unittest.main()
