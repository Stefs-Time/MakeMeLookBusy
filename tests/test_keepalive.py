"""Unit tests for MakeMeLookBusy.

These tests exercise the headless, non-GUI logic only. Importing the module
does not create a Tk root (that happens inside ``Launcher.__init__``, guarded
by ``if __name__ == "__main__"``), so the suite runs on a display-less CI box.
pyautogui is optional; the keep-alive engine degrades to no-ops without it,
which is exactly what we assert here.
"""

import time
import unittest

import MakeMeLookBusy as mmlb


class KeepAliveProfileTests(unittest.TestCase):
    def test_known_profiles_set_intervals(self):
        eng = mmlb.KeepAliveEngine()
        for name, prof in mmlb.KEEP_ALIVE_PROFILES.items():
            eng.set_profile(name)
            self.assertEqual(eng.profile, name)
            self.assertEqual(eng.mouse_interval, prof["mouse"])
            self.assertEqual(eng.key_interval, prof["key"])

    def test_unknown_profile_falls_back_to_default(self):
        eng = mmlb.KeepAliveEngine()
        eng.set_profile("does-not-exist")
        self.assertEqual(eng.profile, mmlb.DEFAULT_PROFILE)
        default = mmlb.KEEP_ALIVE_PROFILES[mmlb.DEFAULT_PROFILE]
        self.assertEqual(eng.mouse_interval, default["mouse"])

    def test_every_profile_has_required_keys(self):
        for prof in mmlb.KEEP_ALIVE_PROFILES.values():
            self.assertIn("mouse", prof)
            self.assertIn("key", prof)
            self.assertIn("desc", prof)

    def test_default_profile_is_a_known_profile(self):
        self.assertIn(mmlb.DEFAULT_PROFILE, mmlb.KEEP_ALIVE_PROFILES)


class KeepAliveJitterTests(unittest.TestCase):
    def test_jitter_stays_within_configured_band(self):
        eng = mmlb.KeepAliveEngine()
        base = 100
        for _ in range(2000):
            v = eng._jittered(base)
            self.assertGreaterEqual(v, base * (1 - eng.jitter))
            self.assertLessEqual(v, base * (1 + eng.jitter))


class KeepAliveLifecycleTests(unittest.TestCase):
    def test_stats_snapshot_has_expected_shape(self):
        eng = mmlb.KeepAliveEngine()
        stats = eng.stats()
        self.assertEqual(
            set(stats), {"profile", "mouse_moves", "key_presses", "last_action"}
        )

    def test_start_is_idempotent_and_resets_counters(self):
        eng = mmlb.KeepAliveEngine()
        eng.mouse_moves = 7
        eng.key_presses = 3
        eng.start()
        try:
            self.assertTrue(eng.running)
            # Counters reset on (re)start.
            self.assertEqual(eng.mouse_moves, 0)
            self.assertEqual(eng.key_presses, 0)
            thread = eng._thread
            eng.start()  # second start must be a no-op, same thread
            self.assertIs(eng._thread, thread)
        finally:
            eng.stop()
        self.assertFalse(eng.running)
        self.assertEqual(eng.last_action, "stopped")

    def test_stop_joins_thread(self):
        eng = mmlb.KeepAliveEngine()
        eng.start()
        time.sleep(0.05)
        eng.stop()
        self.assertFalse(eng.running)
        self.assertIsNone(eng._thread)

    def test_available_reflects_pyautogui_presence(self):
        eng = mmlb.KeepAliveEngine()
        self.assertEqual(eng.available, mmlb.pyautogui is not None)


class RegistryConsistencyTests(unittest.TestCase):
    """The launcher card list and the dispatch registry must not drift apart."""

    def test_every_simulation_card_has_a_registry_entry(self):
        registry = mmlb.Launcher.SIM_REGISTRY
        for sim in mmlb.SIMULATIONS:
            self.assertIn(sim["id"], registry, f"{sim['id']} missing from registry")

    def test_every_registry_entry_has_a_card(self):
        card_ids = {sim["id"] for sim in mmlb.SIMULATIONS}
        for sim_id in mmlb.Launcher.SIM_REGISTRY:
            self.assertIn(sim_id, card_ids, f"{sim_id} has no launcher card")

    def test_simulation_cards_have_required_fields(self):
        required = {"id", "icon", "title", "subtitle", "desc", "color"}
        for sim in mmlb.SIMULATIONS:
            self.assertTrue(required.issubset(sim), f"{sim} missing fields")

    def test_registry_values_are_class_and_duration_flag(self):
        for sim_id, (cls, takes_duration) in mmlb.Launcher.SIM_REGISTRY.items():
            self.assertTrue(isinstance(cls, type), f"{sim_id} class invalid")
            self.assertIsInstance(takes_duration, bool)

    def test_docs_is_the_only_non_timed_mode(self):
        non_timed = [
            sid for sid, (_, timed) in mmlb.Launcher.SIM_REGISTRY.items() if not timed
        ]
        self.assertEqual(non_timed, ["docs"])


class HarmlessKeysTests(unittest.TestCase):
    def test_harmless_keys_present(self):
        self.assertTrue(mmlb.HARMLESS_KEYS)
        for key in mmlb.HARMLESS_KEYS:
            self.assertIsInstance(key, str)


if __name__ == "__main__":
    unittest.main()
