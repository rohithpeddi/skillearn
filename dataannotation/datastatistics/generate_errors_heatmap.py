import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# colors = ["lightgreen", "darkgreen"]  # start and end colors
# n_bins = 100  # Number of bins
# cmap_name = "custom1"
# colormap = LinearSegmentedColormap.from_list(cmap_name, colors, N=n_bins)


# Read and parse the JSON data from a file (Assuming the data is saved in 'data.json')
with open('processed_files/v2/activity_error_categories.json', 'r') as f:
	data = json.load(f)

# Convert the nested dictionary to a Pandas DataFrame
df = pd.DataFrame.from_dict(data, orient='index')
df_transposed = df.T

# Generate the heat map using Seaborn
plt.figure(figsize=(9, 6))

sns.heatmap(df_transposed, annot=True, cmap="Greens", fmt='g', linewidths=0.5)
plt.title("Error Count by Recipe")

ax = plt.gca()
for _, spine in ax.spines.items():
	spine.set_visible(True)

plt.tight_layout()
plt.savefig('processed_files/v2/assets/error_heatmap.png')
plt.show()
