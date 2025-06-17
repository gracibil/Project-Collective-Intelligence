import json
import matplotlib.pyplot as plt
from collections import Counter
import numpy as np
from scipy import stats

def plot_datapoints_from_json(json_path):
    with open(json_path, 'r') as f:
        data = json.load(f)

    ticks = sorted(int(k) for k in data.keys())
    site_0 = [data[str(tick)]['site_0'] for tick in ticks]
    site_1 = [data[str(tick)]['site_1'] for tick in ticks]

    plt.plot(ticks, site_0, label='site_0')
    plt.plot(ticks, site_1, label='site_1')
    plt.xlabel('Ticks')
    plt.ylabel('Amount of agents')
    plt.title('Site Data Over Time')
    plt.legend()
    plt.show()


def average_aggregation_tick(json_path):
    with open(json_path, 'r') as f:
        data = json.load(f)

    ticks_to_aggregate = []

    for sim, ticks in data.items():
        for tick_str, sites in sorted(ticks.items(), key=lambda x: int(x[0])):
            if sites.get('site_0', 0) == 50:
                ticks_to_aggregate.append(int(tick_str))
                break  # Only the first occurrence per simulation

    if ticks_to_aggregate:
        avg_tick = sum(ticks_to_aggregate) / len(ticks_to_aggregate)
        min_tick = min(ticks_to_aggregate)
        max_tick = max(ticks_to_aggregate)
        print(f'Average tick: {avg_tick}')
        print(f'Minimum tick: {min_tick}')
        print(f'Maximum tick: {max_tick}')
    else:
        print('No simulation reached full aggregation on site_0.')

def aggregation_stats(json_path):
    with open(json_path, 'r') as f:
        data = json.load(f)

    ticks_to_aggregate = []

    for sim, ticks in data.items():
        for tick_str, sites in sorted(ticks.items(), key=lambda x: int(x[0])):
            if sites.get('site_0', 0) == 50:
                ticks_to_aggregate.append(int(tick_str))
                break

    if not ticks_to_aggregate:
        print('No simulation reached full aggregation on site_0.')
        return

    ticks_array = np.array(ticks_to_aggregate)
    mean = np.mean(ticks_array)
    std = np.std(ticks_array, ddof=1)

    # z-scores for each simulation
    z_scores = (ticks_array - mean) / std

    # One-sample t-test: is the mean significantly different from a reference value (e.g., 0)?
    t_stat, p_value = stats.ttest_1samp(ticks_array, 0)

    print(f'Average tick: {mean}')
    print(f'Standard deviation: {std}')
    print(f'Z-scores: {z_scores}')
    print(f'T-statistic: {t_stat}')
    print(f'P-value: {p_value}')

def find_full_aggregation_ticks(json_path):
    with open(json_path, 'r') as f:
        data = json.load(f)

    ticks_to_aggregate = []

    for sim, ticks in data.items():
        sorted_ticks = sorted((int(t), v['site_0']) for t, v in ticks.items())
        streak = 0
        streak_start = None
        for tick, count in sorted_ticks:
            if count == 50:
                if streak == 0:
                    streak_start = tick
                streak += 100
                if streak == 500:
                    ticks_to_aggregate.append(streak_start)
                    break
            else:
                streak = 0
                streak_start = None

    return ticks_to_aggregate

def aggregation_stats_and_plot(json_path):
    ticks_to_aggregate = find_full_aggregation_ticks(json_path)
    if not ticks_to_aggregate:
        print('No simulation reached full aggregation on site_0.')
        return

    ticks_array = np.array(ticks_to_aggregate)
    mean = np.mean(ticks_array)
    std = np.std(ticks_array, ddof=1)
    z_scores = (ticks_array - mean) / std
    t_stat, p_value = stats.ttest_1samp(ticks_array, 0)

    print(f'Average tick: {mean}')
    print(f'Standard deviation: {std}')
    print(f'Minimum tick: {min(ticks_array)}')
    print(f'Maximum tick: {max(ticks_array)}')
    print(f'Z-scores: {z_scores}')
    print(f'T-statistic: {t_stat}')
    print(f'P-value: {p_value}')

    plt.hist(ticks_to_aggregate, bins=50, edgecolor='black')
    plt.xlabel('Ticks to full aggregation (streak start)')
    plt.ylabel('Number of simulations')
    plt.title('Distribution of Aggregation Times (500-tick streak)')
    plt.show()

# Usage
if __name__ == "__main__":
    aggregation_stats_and_plot('datapoints_30.json')



if __name__ == "__main__":
    aggregation_stats('datapoints_30.json')

if __name__ == "__main__":
    average_aggregation_tick('datapoints_30.json')




#plot_datapoints_from_json('datapoints_2_symm.json')