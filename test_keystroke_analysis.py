import unittest

from keystroke_analysis import analyze_pattern_for_keystrokes, KeystrokeConfidence
from utils.read_data import read_password_measurements


class TestKeystrokeAnalysis(unittest.TestCase):

    def test_input_1111(self):
        pattern = read_password_measurements("data/simple_samples/input_1111.json")
        keystrokes_input = analyze_pattern_for_keystrokes(pattern)
        self.assertEqual(4,
                         len(keystrokes_input),
                         "Expected number of keystrokes was %d, but %d keystrokes were only detected."
                         % (4, len(keystrokes_input)))

        keys_correct_side = [key for key in keystrokes_input
                             if KeystrokeConfidence.IS_LEFT_LOW in key.keystroke_confidences
                             or KeystrokeConfidence.IS_LEFT_HIGH in key.keystroke_confidences]
        self.assertEqual(4,
                         len(keys_correct_side),
                         "Expected number of correct side of keys is %d, but %d keystrokes were only detected."
                         % (4, len(keys_correct_side)))

    def test_input_2222(self):
        pattern = read_password_measurements("data/simple_samples/input_2222.json")
        keystrokes_input = analyze_pattern_for_keystrokes(pattern)
        self.assertEqual(4,
                         len(keystrokes_input),
                         "Expected number of keystrokes was %d, but %d keystrokes were only detected."
                         % (4, len(keystrokes_input)))

        keys_correct_side = [key for key in keystrokes_input
                             if KeystrokeConfidence.IS_HIGH in key.keystroke_confidences]
        self.assertEqual(4,
                         len(keys_correct_side),
                         "Expected number of correct side of keys is %d, but %d keystrokes were only detected."
                         % (4, len(keys_correct_side)))

    def test_input_3333(self):
        pattern = read_password_measurements("data/simple_samples/input_3333.json")
        keystrokes_input = analyze_pattern_for_keystrokes(pattern)
        self.assertEqual(4,
                         len(keystrokes_input),
                         "Expected number of keystrokes was %d, but %d keystrokes were only detected."
                         % (4, len(keystrokes_input)))

        keys_correct_side = [key for key in keystrokes_input
                             if KeystrokeConfidence.IS_RIGHT_LOW in key.keystroke_confidences
                             or KeystrokeConfidence.IS_RIGHT_HIGH in key.keystroke_confidences]
        self.assertEqual(4,
                         len(keys_correct_side),
                         "Expected number of correct side of keys is %d, but %d keystrokes were only detected."
                         % (4, len(keys_correct_side)))
