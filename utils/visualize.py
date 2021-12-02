import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def visualize_sensor_data(readings: pd.DataFrame, start=0, end=float('inf')):
    """
    visualize trip with desired y-axis to display depending on time and distance between given time interval
    """
    sns.set_style(style='ticks')
    fig, axes = plt.subplots(3, 1, figsize=(12, 6))
    target_df = readings[(readings['time_difference'] >= start) & (readings['time_difference'] <= end)]
    sns.lineplot(y='acc_z', x='time_difference', data=target_df, ax=axes[0], palette='tab10', linewidth=2, dashes=True)
    sns.lineplot(y='gyr_y', x='time_difference', data=target_df, ax=axes[1], palette='tab10', linewidth=2, dashes=True)
    sns.lineplot(y='gyr_x', x='time_difference', data=target_df, ax=axes[2], palette='tab10', linewidth=2, dashes=True)
    plt.tight_layout()

    plt.show()
