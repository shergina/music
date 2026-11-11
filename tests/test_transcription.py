"""Run with:  .venv/bin/python -m unittest"""

import unittest

import numpy as np

from transcription import find_sound

SR = 22050


def tone(seconds, freq=440.0, level=0.3):
    t = np.arange(int(SR * seconds)) / SR
    return (level * np.sin(2 * np.pi * freq * t)).astype(np.float32)


def noise(seconds, level=0.002):
    rng = np.random.default_rng(0)
    return (level * rng.standard_normal(int(SR * seconds))).astype(np.float32)


class FindSoundTest(unittest.TestCase):
    def test_trims_quiet_start_and_end(self):
        y = np.concatenate([noise(1.0), tone(2.0), noise(4.0)])
        start, end = find_sound(y, SR)
        self.assertAlmostEqual(start, 1.0, delta=0.3)      # short margin before the first sound
        self.assertAlmostEqual(end, 3.0 + 2.0, delta=0.3)  # two seconds kept for the decay

    def test_keeps_margin_before_first_note(self):
        y = np.concatenate([noise(1.0), tone(2.0), noise(1.5)])
        start, _ = find_sound(y, SR)
        self.assertLess(start, 1.0)

    def test_no_silence_means_no_trim(self):
        y = tone(3.0)
        self.assertEqual(find_sound(y, SR), (0.0, 3.0))

    def test_all_silence_returns_everything(self):
        y = noise(2.0)
        self.assertEqual(find_sound(y, SR), (0.0, 2.0))

    def test_ignores_a_click_in_the_silence(self):
        click = np.zeros(int(SR * 0.5), dtype=np.float32)
        click[100:200] = 0.5
        y = np.concatenate([noise(0.5), click, noise(1.0), tone(2.0), noise(0.5)])
        start, _ = find_sound(y, SR)
        self.assertGreater(start, 1.5)

    def test_quiet_first_note_survives(self):
        y = np.concatenate([noise(1.0), tone(1.0, level=0.03), tone(2.0, level=0.5), noise(1.0)])
        start, _ = find_sound(y, SR)
        self.assertLess(start, 1.0)


if __name__ == "__main__":
    unittest.main()
