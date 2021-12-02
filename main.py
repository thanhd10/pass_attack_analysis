import pandas as pd

from keystroke_analysis import analyze_pattern_for_keystrokes
from utils.read_data import read_password_measurements

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

if __name__ == '__main__':
    pattern = read_password_measurements("data/input_4444.json")
    keystrokes_input = analyze_pattern_for_keystrokes(pattern)
