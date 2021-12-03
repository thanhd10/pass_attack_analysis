from enum import Enum
from typing import Tuple, List

import pandas as pd
from scipy.signal import find_peaks

from definitions import ACC_Z_MIN_CHANGE_VALLEY, ACC_Z_MAX_CHANGE_VALLEY, GYR_Y_MIN_CHANGE, GYR_X_MIN_CHANGE, \
    ACC_Z_MIN_CHANGE_PEAK, ACC_Z_MAX_CHANGE_PEAK, SLIDING_FACTOR, WINDOW_ID_COL_NAME, WINDOW_SIZE
from utils.sliding_windows import create_sliding_windows


class KeyboardSide(Enum):
    NO_SIDE = 1
    IS_LEFT = 2
    IS_RIGHT = 3


class KeystrokeConfidence(Enum):
    NO_KEYSTROKE = 1
    IS_LOW = 2
    IS_HIGH = 3
    IS_LEFT_LOW = 4
    IS_LEFT_HIGH = 5
    IS_RIGHT_LOW = 6
    IS_RIGHT_HIGH = 7


class Keystroke(object):
    def __init__(self, keystroke_confidences: List[KeystrokeConfidence], start_time: float, end_time: float):
        self.keystroke_confidences = keystroke_confidences
        self.start_time = start_time
        self.end_time = end_time


def analyze_pattern_for_keystrokes(pattern: pd.DataFrame):
    # Step 1: Create sliding windows
    sliding_windows = create_sliding_windows(pattern, window_size=WINDOW_SIZE, sliding_factor=SLIDING_FACTOR)
    sliding_windows = [x for _, x in sliding_windows.groupby(WINDOW_ID_COL_NAME)]

    # Step 2: Create calculate mean values
    mean_acc_z = pattern['acc_z'].mean()
    mean_gyr_x = pattern['gyr_x'].mean()
    mean_gyr_y = pattern['gyr_y'].mean()

    # Step 3: Detect keystrokes
    analyzed_windows = [__check_for_keystroke(window, mean_acc_z, mean_gyr_x, mean_gyr_y)
                        for window in sliding_windows]
    keystroke_candidates = [keystroke for keystroke in analyzed_windows if
                            keystroke[0] != KeystrokeConfidence.NO_KEYSTROKE]

    # Helper variable for already considered keystroke windows, if they overlap with another time window
    already_grouped = []

    detected_keystrokes = []

    # Step 4: Group overlapping windows of keystrokes
    for keystroke_a, keystroke_b in zip(keystroke_candidates[:-1], keystroke_candidates[1:]):
        if keystroke_a in already_grouped:
            continue
        if keystroke_b[1] < keystroke_a[2] < keystroke_b[2]:
            detected_keystrokes.append(Keystroke(keystroke_confidences=[keystroke_a[0], keystroke_b[0]],
                                                 start_time=keystroke_a[1],
                                                 end_time=keystroke_b[2]))
            already_grouped.append(keystroke_b)
        else:
            detected_keystrokes.append(Keystroke(keystroke_confidences=[keystroke_a[0]],
                                                 start_time=keystroke_a[1],
                                                 end_time=keystroke_b[2]))

    # Check last keystroke separately, as loop before does not explicitely check last keystroke_candidate
    if keystroke_candidates[-1] not in already_grouped:
        detected_keystrokes.append(Keystroke(keystroke_confidences=[keystroke_candidates[-1][0]],
                                             start_time=keystroke_candidates[-1][1],
                                             end_time=keystroke_candidates[-1][2]))

    return detected_keystrokes


def __check_for_keystroke(window: pd.DataFrame,
                          mean_acc_z: float,
                          mean_gyr_x: float,
                          mean_gyr_y: float) -> Tuple[KeystrokeConfidence, float, float]:
    if not __check_acceleration_pattern(window, mean_acc_z):
        keystroke_confidence = KeystrokeConfidence.NO_KEYSTROKE
    else:
        is_high_confidence = __is_phone_shaking_from_keyboard_pressed(window, mean_gyr_x)
        keyboard_side = __find_keyboard_side(window, mean_gyr_y)

        if keyboard_side == KeyboardSide.IS_LEFT:
            if is_high_confidence:
                keystroke_confidence = KeystrokeConfidence.IS_LEFT_HIGH
            else:
                keystroke_confidence = KeystrokeConfidence.IS_LEFT_LOW
        elif keyboard_side == KeyboardSide.IS_RIGHT:
            if is_high_confidence:
                keystroke_confidence = KeystrokeConfidence.IS_RIGHT_HIGH
            else:
                keystroke_confidence = KeystrokeConfidence.IS_RIGHT_LOW
        else:
            if is_high_confidence:
                keystroke_confidence = KeystrokeConfidence.IS_HIGH
            else:
                keystroke_confidence = KeystrokeConfidence.IS_LOW

    return keystroke_confidence, window['time_difference'].min(), window['time_difference'].max()


def __check_acceleration_pattern(window: pd.DataFrame, mean_acc_z: float) -> bool:
    """
    On clicking on a device, a keystroke can be detected by small peaks within the z-axis of the accelerometer.
    """
    peaks = window.iloc[find_peaks(window['acc_z'].values, prominence=ACC_Z_MIN_CHANGE_PEAK)[0]]
    peaks = peaks[(peaks['acc_z'] - mean_acc_z > ACC_Z_MIN_CHANGE_PEAK) &
                  (peaks['acc_z'] - mean_acc_z < ACC_Z_MAX_CHANGE_PEAK)]

    valleys = window.iloc[find_peaks(window['acc_z'].values * -1, prominence=ACC_Z_MIN_CHANGE_VALLEY)[0]]
    valleys = valleys[(mean_acc_z - valleys['acc_z'] > ACC_Z_MIN_CHANGE_VALLEY) &
                      (mean_acc_z - valleys['acc_z'] < ACC_Z_MAX_CHANGE_VALLEY)]

    if len(peaks) == 0 or len(valleys) == 0:
        return False
    else:
        # noinspection PyTypeChecker
        return any(peaks['time_difference'].values > valleys['time_difference'].values)


def __is_phone_shaking_from_keyboard_pressed(window: pd.DataFrame, mean_gyr_x: float) -> bool:
    """
    Keyboard is positioned on the bottom of a smartphone. Therefore, changes on the x-axis of the
    gyroscope might be observable to indicate typing. Higher confidence on prediction with this observation.
    """
    peaks = window.iloc[find_peaks(window['gyr_x'].values, prominence=GYR_X_MIN_CHANGE)[0]]
    peaks = peaks[peaks['gyr_x'] - GYR_X_MIN_CHANGE > mean_gyr_x]

    valleys = window.iloc[find_peaks(window['gyr_x'].values * -1, prominence=GYR_X_MIN_CHANGE)[0]]
    valleys = valleys[abs(valleys['gyr_x']) - GYR_X_MIN_CHANGE > mean_gyr_x]

    return len(peaks) != 0 or len(valleys) != 0


def __find_keyboard_side(window: pd.DataFrame, mean_gyr_y: float) -> KeyboardSide:
    """
    Depending on which side of a smartphone keyboard a key is pressed, corresponding changes in
    the y-axis of the gyroscope are visible:
    - stronger negative peaks indicate button press on the left side
    - stronger positive peaks indicate button pressed on the right side
    - no clear peak can either indicate a key in the middle, or no key stroke at all
    """
    valleys = __is_phone_left_tilting(window, mean_gyr_y)
    peaks = __is_phone_right_tilting(window, mean_gyr_y)

    if len(valleys) == 0 and len(peaks) == 0:
        return KeyboardSide.NO_SIDE
    elif len(valleys) == 0:
        return KeyboardSide.IS_RIGHT
    elif len(peaks) == 0:
        return KeyboardSide.IS_LEFT
    else:
        max_stroke_left = valleys['gyr_y'].max()
        max_stroke_right = peaks['gyr_y'].max()
        if abs(max_stroke_left) - abs(max_stroke_right) > 0:
            return KeyboardSide.IS_LEFT
        else:
            return KeyboardSide.IS_RIGHT


def __is_phone_left_tilting(window: pd.DataFrame, mean_gyr_y: float) -> pd.DataFrame:
    """
    By pressing the key on the left side, the phone tilts to the left,
    which can be seen via *negative* peaks on the y-axis of the gyroscope.
    """
    valleys = window.iloc[find_peaks(window['gyr_y'].values * -1, prominence=GYR_Y_MIN_CHANGE)[0]]
    return valleys[abs(valleys['gyr_y']) - GYR_Y_MIN_CHANGE > mean_gyr_y]


def __is_phone_right_tilting(window: pd.DataFrame, mean_gyr_y: float) -> pd.DataFrame:
    """
    By pressing the key on the right side, the phone tilts to the right,
    which can be seen via *positive* peaks on the y-axis of the gyroscope.
    """
    peaks = window.iloc[find_peaks(window['gyr_y'].values, prominence=GYR_Y_MIN_CHANGE)[0]]
    return peaks[peaks['gyr_y'] - GYR_Y_MIN_CHANGE > mean_gyr_y]
