import json

import pandas as pd


def read_password_measurements(file_path: str) -> pd.DataFrame:
    with open(file_path) as file:
        sample = json.load(file)
    return pd.DataFrame(sample['measurements'])
