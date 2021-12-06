import pandas as pd

from keystroke_analysis import analyze_pattern_for_keystrokes
from utils.read_data import read_password_measurements
from utils.visualize import visualize_sensor_pattern

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

if __name__ == '__main__':
    pattern = read_password_measurements("data/simple_samples/input_3333.json")
    keystrokes_input = analyze_pattern_for_keystrokes(pattern)

    # visualize_sensor_data(pattern)
    visualize_sensor_pattern(pattern, "pattern_3333.svg")

    for keystroke in keystrokes_input:
        print(keystroke.keystroke_confidences)
