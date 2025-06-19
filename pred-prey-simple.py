import random
from dataclasses import dataclass, field
from vi import Agent, Config, Simulation, Window, HeadlessSimulation
from vi.util import count, probability
import polars as pl
import matplotlib.pyplot as plt

@dataclass
class PredatorPreyConfig(Config):
    width : int = 100
    height : int  = 100
    radius : int = 20
    movement_speed : float = 2.0
    #seed : int = 1
    duration : int = 1000
    window : Window = field(default_factory=lambda: Window(width=800, height=800))

@dataclass
class PredatorConfig(Config):
    width : int = 100
    height : int  = 100
    radius : int = 500
    movement_speed : float = 2.0
    seed : int = 1
    duration : int = 200


data = []
prey_killed_this_tick = {}
ticks = 0
predator_alive = 0
prey_alive = 0
id_num = 0

class Predator(Agent[PredatorConfig]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = "hunt"  # Initial state
        self.ticks = 0
        self.ticks_to_reproduce = 175
        self.reproduction_chance = 0.01  # Percentage chance to reproduce
        self.death_chance = 0.1  # Chance of dying from starvation
        self.speed = 0.01


    def detect_prey(self):
        # Check if there are any Prey agents in proximity
        for neighbor in self.in_proximity_performance():
            if isinstance(neighbor, Prey):
                if not f"{neighbor.id}" in prey_killed_this_tick:
                    return neighbor
        return False


    def try_reproduce(self) -> None:
        if probability(self.reproduction_chance):
            self.reproduce()
            self.state = "hunt"  # Reset state to hunt after reproduction

    def hunt_prey(self) -> None:
        prey = self.detect_prey()
        if prey:
            global prey_killed_this_tick
            prey_killed_this_tick[f"{prey.id}"] = prey.id
            prey.kill()
            self.reproduce()
           # self.state = "reproduce"


    def update(self) -> None:
        self.save_data('kind', 'predator')
        self.hunt_prey()
        if probability(self.death_chance):
            self.kill()
        self.pos += self.move * self.speed



class Prey(Agent[PredatorPreyConfig]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = "wander"  # Initial state
        self.ticks = 0
        self.reproduction_chance = 0.006  # Percentage chance to reproduce
        self.speed = 0.002
        global id_num
        self.id = id_num

        id_num += 1

    def update_ticks(self) -> None:
        self.ticks += 1


    def update_breed(self) -> None:
        if probability(self.reproduction_chance):
            self.reproduce()


    def update(self) -> None:
        global prey_killed_this_tick
        self.save_data('kind', 'prey')
        self.update_breed()
        self.update_ticks()
        self.pos += self.move * self.speed

        prey_killed_this_tick = {}

def run_sim():
    sim = (
        HeadlessSimulation(PredatorPreyConfig())
        .batch_spawn_agents(1000, Prey, images=["images/prey.png"])
        .batch_spawn_agents(50, Predator, images=["images/predator.png"])
        .run()
        .snapshots
    )
    print('simulation finished')
    print(sim.head(10))

    aggreg = sim.group_by("frame", maintain_order=True).agg([
        pl.col("kind").value_counts().alias("count"),
    ])

    frames = aggreg['frame'].to_list()
    predator_counts = []
    prey_counts = []

    for counts in aggreg['count']:
        pred = next((item['count'] for item in counts if item['kind'] == 'predator'), 0)
        prey = next((item['count'] for item in counts if item['kind'] == 'prey'), 0)
        predator_counts.append(pred)
        prey_counts.append(prey)

    plt.plot(frames, predator_counts, label='Predator')
    plt.plot(frames, prey_counts, label='Prey')
    plt.xlabel('Frame')
    plt.ylabel('Count')
    plt.title('Predator and Prey Counts Over Time')
    plt.legend()
    plt.show()

if __name__ == "__main__":
    run_sim()