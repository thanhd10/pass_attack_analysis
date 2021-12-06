import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from definitions import TIMESTAMP_COL


def visualize_sensor_data(readings: pd.DataFrame, start=0, end=float('inf')):
    """
    visualize trip with desired y-axis to display depending on time and distance between given time interval
    """
    sns.set_style(style='ticks')
    fig, axes = plt.subplots(3, 1, figsize=(12, 6))
    target_df = readings[(readings[TIMESTAMP_COL] >= start) & (readings[TIMESTAMP_COL] <= end)]
    sns.lineplot(y='acc_z', x=TIMESTAMP_COL, data=target_df, ax=axes[0], palette='tab10', linewidth=2, dashes=True)
    sns.lineplot(y='gyr_y', x=TIMESTAMP_COL, data=target_df, ax=axes[1], palette='tab10', linewidth=2, dashes=True)
    sns.lineplot(y='gyr_x', x=TIMESTAMP_COL, data=target_df, ax=axes[2], palette='tab10', linewidth=2, dashes=True)
    plt.tight_layout()

    plt.show()


def visualize_sensor_pattern(pattern: pd.DataFrame,
                             target_path: str,
                             columns_to_plot=None,
                             x_label='Time in seconds',
                             y_label='Distribution'):
    # plot pattern of roundabout
    if columns_to_plot is None:
        columns_to_plot = ["acc_z", "gyr_x", "gyr_y"]

    fig, ax = plt.subplots(figsize=(12, 3))
    sns.set_style(style='ticks')
    sns.lineplot(x=TIMESTAMP_COL, y='value', hue='variable',
                 data=pd.melt(pattern[columns_to_plot + [TIMESTAMP_COL]], [TIMESTAMP_COL]),
                 palette='tab10', linewidth=2, dashes=True).set(xlabel=x_label,
                                                                ylabel=y_label)

    # design optimizations
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    plt.tight_layout()
    fig.savefig(target_path, format='svg', dpi=1200)
    plt.show()
