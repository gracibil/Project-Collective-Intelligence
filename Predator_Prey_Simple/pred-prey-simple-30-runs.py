import json
import random
from dataclasses import dataclass, field
from vi import Agent, Config, Simulation, Window, HeadlessSimulation
from vi.util import count, probability
import polars as pl
import matplotlib.pyplot as plt
import time
@dataclass
class PredatorPreyConfig(Config):
    width : int = 100
    height : int  = 100
    radius : int = 25
    movement_speed : float = 0.8
    seed : int = 1
    duration : int = 4000
    window : Window = field(default_factory=lambda: Window(width=800, height=800))


data = []
prey_killed_this_tick = {}
ticks = 0
predator_alive = 0
prey_alive = 0
id_num = 0

class CustomSimulation(Simulation):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Predator(Agent[PredatorPreyConfig]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.death_chance = 0.05  # Chance of dying from starvation





    def detect_prey(self):
        # Check if there are any Prey agents in proximity
        for neighbor in self.in_proximity_performance():
            if isinstance(neighbor, Prey):
                if neighbor.is_alive():
                    neighbor.kill()
                    return True
        return False

    def hunt_prey(self) -> None:
        prey = self.detect_prey()
        if prey:
            self.reproduce()
        else:
            if probability(self.death_chance):
                self.kill()
           # self.state = "reproduce"


    def update(self) -> None:
        self.save_data('kind', 'predator')
        self.hunt_prey()

        self.pos += self.move * self.config.movement_speed



class Prey(Agent[PredatorPreyConfig]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reproduction_chance = 0.005  # Percentage chance to reproduce
        global id_num
        self.id = id_num

        id_num += 1



    def update_breed(self) -> None:
        if probability(self.reproduction_chance):
            self.reproduce()


    def update(self) -> None:
        global prey_killed_this_tick
        self.save_data('kind', 'prey')
        self.update_breed()
        self.pos += self.move * self.config.movement_speed

        prey_killed_this_tick = {}

def run_sim():
    sim_data = {}
    with open('datapoints_30_pred_prey.json', 'r') as f:
        sim_data = json.load(f)
    keys = list(sim_data.keys())
    keys = [int(key) for key in keys if key.isdigit()]  # Ensure keys are integers
    highest_key = max(keys) if keys else 0

    for i in range(highest_key, 30):
        print('starting simulation', i+1)
        time_start = time.time()
        sim = (
            HeadlessSimulation(PredatorPreyConfig())
            .batch_spawn_agents(2000, Prey, images=["../images/prey.png"])
            .batch_spawn_agents(25, Predator, images=["../images/predator.png"])
            .run()
            .snapshots

        )
        time_end = time.time()
        print('simulation', i+1, 'completed in', time_end - time_start, 'seconds')
        print(sim.head(10))

        aggreg = sim.group_by("frame", maintain_order=True).agg([
            pl.col("kind").value_counts().alias("count"),
        ])

        frames = aggreg['frame'].to_list()
        simulation_run_data = {}
        predator_counts = []
        prey_counts = []

        for counts in aggreg['count']:
            pred = next((item['count'] for item in counts if item['kind'] == 'predator'), 0)
            prey = next((item['count'] for item in counts if item['kind'] == 'prey'), 0)
            predator_counts.append(pred)
            prey_counts.append(prey)

        print(f"Predator counts: {predator_counts}")
        print(f"Prey counts: {prey_counts}")

        for x in range(len(predator_counts)):
            simulation_run_data[x] = {'predator': predator_counts[x], 'prey': prey_counts[x]}

        sim_data[i+1] = simulation_run_data

        plt.plot(frames, predator_counts, label='Predator')
        plt.plot(frames, prey_counts, label='Prey')
        plt.xlabel('Frame')
        plt.ylabel('Count')
        plt.title('Predator and Prey Counts Over Time')
        plt.legend()
        plt.show()

        with open('datapoints_30_pred_prey.json', 'w') as f:
            json.dump(sim_data, f, indent=4)


if __name__ == "__main__":
    run_sim()