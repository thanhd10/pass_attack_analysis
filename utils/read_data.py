import json

import pandas as pd

from definitions import TIMESTAMP_COL, TRIM_BEGINNING_TIME, TRIM_ENDING_TIME


def read_password_measurements(file_path: str) -> pd.DataFrame:
    with open(file_path) as file:
        sample = json.load(file)

    pattern = pd.DataFrame(sample['measurements'])

    # Remove button press for opening textfield and button press for stopping record
    return __remove_beginning_and_end(pattern)


def __remove_beginning_and_end(pattern: pd.DataFrame) -> pd.DataFrame:
    return pattern[(pattern[TIMESTAMP_COL] >= TRIM_BEGINNING_TIME) &
                   (pattern[TIMESTAMP_COL] <= (pattern[TIMESTAMP_COL].max() - TRIM_ENDING_TIME))]
