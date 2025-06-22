import json
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

# Load JSON data from file
json_file_path = 'datapoints_30_pred_prey.json'  # Replace with the path to your JSON file
try:
    with open(json_file_path, 'r') as f:
        data = json.load(f)
except FileNotFoundError:
    print(f"Error: File {json_file_path} not found.")
    exit(1)
except json.JSONDecodeError:
    print("Error: Invalid JSON format.")
    exit(1)

# Initialize arrays to store populations
num_sims = 30
num_ticks = 4000
predator_data = np.zeros((num_sims, num_ticks))
prey_data = np.zeros((num_sims, num_ticks))

# Extract population data
for sim in range(1, num_sims + 1):
    sim_key = str(sim)
    for tick in range(1, num_ticks + 1):
        tick_key = str(tick)
        try:
            predator_data[sim - 1, tick - 1] = data[sim_key][tick_key]['predator']
            prey_data[sim - 1, tick - 1] = data[sim_key][tick_key]['prey']
        except KeyError:
            print(f"Missing data for sim {sim_key}, tick {tick_key}")
            exit(1)

# Calculate mean and standard deviation across simulations for each tick
predator_mean = np.mean(predator_data, axis=0)
prey_mean = np.mean(prey_data, axis=0)
predator_std = np.std(predator_data, axis=0)
prey_std = np.std(prey_data, axis=0)

# Find local peaks with a minimum distance (e.g., 50 ticks to reduce noise)
predator_peaks, _ = find_peaks(predator_mean, distance=50)
prey_peaks, _ = find_peaks(prey_mean, distance=50)

# Filter peaks to ensure previous 200 ticks and next 200 ticks are lower
window = 200  # Number of ticks to check before and after
filtered_predator_peaks = []
filtered_prey_peaks = []

for peak in predator_peaks:
    # Ensure peak is not too close to the start or end to have full windows
    if peak >= window and peak < num_ticks - window:
        # Check if all values in previous 200 ticks and next 200 ticks are lower
        prev_window = predator_mean[peak - window:peak]
        next_window = predator_mean[peak + 1:peak + window + 1]
        if np.all(prev_window < predator_mean[peak]) and np.all(next_window < predator_mean[peak]):
            filtered_predator_peaks.append(peak)

for peak in prey_peaks:
    if peak >= window and peak < num_ticks - window:
        prev_window = prey_mean[peak - window:peak]
        next_window = prey_mean[peak + 1:peak + window + 1]
        if np.all(prev_window < prey_mean[peak]) and np.all(next_window < prey_mean[peak]):
            filtered_prey_peaks.append(peak)

# Convert to numpy arrays for indexing
filtered_predator_peaks = np.array(filtered_predator_peaks)
filtered_prey_peaks = np.array(filtered_prey_peaks)

# Create the plot
plt.figure(figsize=(12, 6))
ticks = np.arange(1, num_ticks + 1)

# Plot mean lines
plt.plot(ticks, predator_mean, label='Predator Mean', color='red')
plt.plot(ticks, prey_mean, label='Prey Mean', color='blue')

# Add shaded areas for standard deviation
plt.fill_between(ticks,
                 predator_mean - predator_std,
                 predator_mean + predator_std,
                 color='red', alpha=0.2, label='Predator Std Dev')
plt.fill_between(ticks,
                 prey_mean - prey_std,
                 prey_mean + prey_std,
                 color='blue', alpha=0.2, label='Prey Std Dev')

# Mark filtered peaks with vertical lines
for peak in filtered_predator_peaks:
    plt.axvline(x=ticks[peak], color='red', linestyle='--', alpha=0.5, linewidth=1)
for peak in filtered_prey_peaks:
    plt.axvline(x=ticks[peak], color='blue', linestyle='--', alpha=0.5, linewidth=1)

# Customize the plot
plt.figtext(.1, .85, "Predator Death % = 0.5 \nPrey Reproduction % = 0.05")
plt.xlabel('Tick')
plt.ylabel('Population')
plt.title('Mean Population with Standard Deviation and Filtered Local Peaks (30 Simulations)')
plt.legend()
plt.grid(True)
plt.tight_layout()

# Show the plot
plt.show()

# Print number of peaks found
print(f"Number of predator population peaks (filtered): {len(filtered_predator_peaks)}")
print(f"Number of prey population peaks (filtered): {len(filtered_prey_peaks)}")
