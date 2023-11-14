from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


class CsvPlotter:
    def __init__(self, csv_path: Path):
        self.csv_path = csv_path

    def plot_benchmark(self):
        # Read CSV file
        df = pd.read_csv(self.csv_path)

        # Rename x axis ticks to be the dataset size in thousands in the format of 1k, 10k, 1M
        def format_ticks(x):
            if x < 1000:
                return x
            elif x < 1_000_000:
                return f"{x // 1000}k"
            else:
                return f"{x // 1_000_000}M"

        df['Dataset'] = df['Dataset'].apply(format_ticks)

        # Set dataset as index
        df.set_index('Dataset', inplace=True)

        # Rename x axis to "Dataset Size"
        df.rename(columns={'Dataset': 'Dataset Size'}, inplace=True)

        # Plot the results in a compact way
        df.plot(kind='bar', figsize=(8, 4), rot=0, width=0.7)

        plt.title('Benchmark Results')
        plt.ylabel('Execution Time (seconds)')
        plt.xlabel('Dataset')

        plt.yscale('log')
        plt.grid(axis='y')
        plt.tight_layout()

        # add label to the top of each bar with a white background behind the black label
        for p in plt.gca().patches:
            plt.gca().annotate(f"{p.get_height():.3f}",
                               (p.get_x() + p.get_width() / 2, p.get_height()),
                               ha='center', va='center', color='b', xytext=(0, 10),
                               textcoords='offset points', bbox=dict(facecolor='white'))

        # save to the same filename as the csv file
        plt.savefig(str(self.csv_path).replace(".csv", ".png"))
