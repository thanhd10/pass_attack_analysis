import numpy as np
import pandas as pd

from definitions import TIMESTAMP_COL, WINDOW_ID_COL_NAME


def create_sliding_windows(data: pd.DataFrame, window_size: float, sliding_factor: float) -> pd.DataFrame:
    """
    create a DataFrame, that transforms the raw time series data of a 'record' into windows depending
    on the passed time
    every row in the DataFrame will be assigned a value for the 'time_id_column' to indicate,
    which window the row belongs to

    :param data: the raw data of a 'record'
    :param window_size: the time in seconds a sliding window covers
    :param sliding_factor: a percentage that determines, how much the sliding windows should overlap
    :return: the transformed DataFrame containing the raw data of a 'record' in sliding windows
    """
    result = []
    time_id = 0
    while True:
        data.reset_index(inplace=True, drop=True)
        curr_window_start_time = data[TIMESTAMP_COL].iloc[0]
        values_after_curr_window = data[data[TIMESTAMP_COL] - curr_window_start_time > window_size]

        data[WINDOW_ID_COL_NAME] = time_id

        if values_after_curr_window.empty:
            result.append(data)
            # no windows to create left, so exit
            break
        else:
            curr_window_end = values_after_curr_window.index[0]
            curr_window_frame = data.head(curr_window_end + 1)
            result.append(curr_window_frame)

            # remove values of previous window depending on overlapping factor
            data = data.drop(data.index[: int(np.round(curr_window_end * sliding_factor))])
            # increase index for next sliding window
            time_id += 1

    return pd.concat(result, axis=0, ignore_index=True)
