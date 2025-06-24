import json
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

def find_full_aggregation_ticks(json_path):
    with open(json_path, 'r') as f:
        data = json.load(f)

    ticks_to_aggregate = []
    for sim, ticks in data.items():
        sorted_ticks = sorted((int(t), v) for t, v in ticks.items())
        streak_0 = streak_1 = 0
        streak_start_0 = streak_start_1 = None
        for tick, counts in sorted_ticks:
            # Site 0
            if counts['site_0'] == 50:
                if streak_0 == 0:
                    streak_start_0 = tick
                streak_0 += 100
                if streak_0 == 500:
                    ticks_to_aggregate.append(streak_start_0)
                    break
            else:
                streak_0 = 0
                streak_start_0 = None
            # Site 1
            if counts['site_1'] == 50:
                if streak_1 == 0:
                    streak_start_1 = tick
                streak_1 += 100
                if streak_1 == 500:
                    ticks_to_aggregate.append(streak_start_1)
                    break
            else:
                streak_1 = 0
                streak_start_1 = None
    return ticks_to_aggregate

def plot_aggregation_stats(json_path):
    ticks = find_full_aggregation_ticks(json_path)
    if not ticks:
        print('No simulation reached full aggregation on site_0 or site_1.')
        return

    arr = np.array(ticks)
    mean = np.mean(arr)
    std = np.std(arr, ddof=1)
    z_scores = (arr - mean) / std
    t_stat, p_value = stats.ttest_1samp(arr, 0)
    min_tick = np.min(arr)
    max_tick = np.max(arr)

    # Print stats
    print(f'Average tick: {mean}')
    print(f'Minimum tick: {min_tick}')
    print(f'Maximum tick: {max_tick}')
    print(f'Standard deviation: {std}')
    print(f'Z-scores: {z_scores}')
    print(f'T-statistic: {t_stat}')
    print(f'P-value: {p_value:.6f}')

    # Plot
    plt.figure(figsize=(10, 6))
    plt.hist(arr, bins=10, edgecolor='black', alpha=0.7)
    plt.axvline(mean, color='red', linestyle='dashed', linewidth=1, label=f'Avg: {mean:.1f}')
    plt.axvline(min_tick, color='green', linestyle='dotted', linewidth=1, label=f'Min: {min_tick}')
    plt.axvline(max_tick, color='blue', linestyle='dotted', linewidth=1, label=f'Max: {max_tick}')
    plt.xlabel('Ticks to full aggregation')
    plt.ylabel('Number of simulations')
    plt.title('Distribution of Aggregation Times (site_0 or site_1)')
    plt.legend()
    plt.text(0.7, 0.95, f'p-value: {p_value:.6f}', transform=plt.gca().transAxes)
    plt.text(0.7, 0.90, f'z-scores: {np.round(z_scores, 2)}', transform=plt.gca().transAxes, fontsize=8)
    plt.tight_layout()
    plt.show()

# Usage
plot_aggregation_stats('../Predator_Prey_Simple/datapoints_30_symm.json')