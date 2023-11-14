from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import style


style.use('dark_background')  # Use a dark theme

class CsvPlotter:
    def __init__(self, csv_path: Path):
        self.csv_path = csv_path

    def plot_benchmark(self):
        df = pd.read_csv(self.csv_path)

        def format_ticks(x):
            if x < 1000:
                return x
            elif x < 1_000_000:
                return f"{x // 1000}k"
            else:
                return f"{x // 1_000_000}M"

        df['Dataset'] = df['Dataset'].apply(format_ticks)
        df.set_index('Dataset', inplace=True)
        df.rename(columns={'Dataset': 'Dataset Size'}, inplace=True)

        plt.rcParams["font.sans-serif"] = "Arial"  # Use a modern font
        plt.rcParams["font.size"] = 12  # Increase font size

        # Define Darcula-like colors for bars and labels
        bar_colors = ['#5294E2', '#E2777A']  # Soft blue and red
        label_color = '#FFC66D'  # Softer yellow for labels
        edge_color = '#646464'  # Gray for bar contour

        # Create the plot
        ax = df.plot(kind='bar', figsize=(8, 4), rot=0, width=0.5, color=bar_colors,
                     edgecolor=edge_color)

        # Set the background color
        ax.set_facecolor('#2B2B2B')

        # Set font
        plt.rcParams["font.family"] = "Helvetica"  # You can change this to your preferred font

        # Titles and labels with a lighter color for visibility
        plt.title('Benchmark Results', color='white')
        plt.ylabel('Execution Time (seconds)', color='white')
        plt.xlabel('Dataset', color='white')

        # Remove small ticks on the y-axis
        ax.tick_params(axis='y', which='minor', left=False)

        plt.yscale('log')
        plt.grid(axis='y', color='gray')  # Adjust grid color for visibility
        plt.tight_layout()

        # Add labels to bars
        for p in ax.patches:
            ax.annotate(f"{p.get_height():.3f}", (p.get_x() + p.get_width() / 2., p.get_height()),
                        ha='center', va='center', fontsize=9, color=label_color, xytext=(0, 10),
                        textcoords='offset points', bbox=dict(facecolor='black', edgecolor='0.1'))


        plt.savefig(str(self.csv_path.with_suffix('.png')), dpi=300)  # High-resolution output

# Usage remains the same

