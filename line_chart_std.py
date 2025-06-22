import json
import numpy as np
import matplotlib.pyplot as plt

# Sample JSON data (replace with your actual JSON file or string)
# For demonstration, I'll create a small sample based on your structure
# data = {
#     str(sim): {str(tick): {'predator': np.random.randint(20, 80), 'prey': np.random.randint(1900, 2200)}
#                for tick in range(1, 4002)} for sim in range(1, 31)
# }

 #If you have a JSON file, load it like this:
with open('datapoints_30_pred_prey.json', 'r') as f:
     data = json.load(f)

# Initialize arrays to store populations for each tick across all simulations
num_ticks = 4000
num_sims = 30
predator_data = np.zeros((num_sims, num_ticks))
prey_data = np.zeros((num_sims, num_ticks))

# Extract population data
for sim in range(1, num_sims + 1):
    sim_key = str(sim)
    for tick in range(1, num_ticks + 1):
        tick_key = str(tick)
        predator_data[sim - 1, tick - 1] = data[sim_key][tick_key]['predator']
        prey_data[sim - 1, tick - 1] = data[sim_key][tick_key]['prey']

# Calculate mean and standard deviation across simulations for each tick
predator_mean = np.mean(predator_data, axis=0)
prey_mean = np.mean(prey_data, axis=0)
predator_std = np.std(predator_data, axis=0)
prey_std = np.std(prey_data, axis=0)

# Create the plot
plt.figure(figsize=(12, 6))

# Plot mean lines
ticks = np.arange(1, num_ticks + 1)
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

# Customize the plot
plt.figtext(.1, .85, "Predator Death % = 0.5 \nPrey Reproduction % = 0.05")
plt.xlabel('Tick')
plt.ylabel('Population')
plt.title('Mean Population with Standard Deviation (30 Simulations)')
plt.legend()
plt.grid(True)
plt.tight_layout()

# Show the plot
plt.show()