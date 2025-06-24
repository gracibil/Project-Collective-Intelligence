import json
import random
from dataclasses import dataclass, field
import math
from numpy.testing.print_coercion_tables import print_coercion_table
from vi import Agent, Config, Simulation, Window, HeadlessSimulation
from vi.util import count, probability
import polars as pl
import matplotlib.pyplot as plt
import time
@dataclass
class PredatorPreyConfig(Config):
    width : int = 100
    height : int  = 100
    radius : int = 20
    prey_rad : int = 800
    movement_speed : float = 0.8
    seed : int = 1
    duration : int = 20000
    window : Window = field(default_factory=lambda: Window(width=800, height=800))
    max_prey_age: int = 9             # Maximum age for prey before death
    max_predator_age: int = 12         # Maximum age for predators before death
    predator_start_energy: int = 100    # Initial energy for predators
    predator_energy_to_hunt: int = 75  # Predator hunts when energy is below this threshold
    repro_energy_threshold: int = 30    # Minimum energy required to reproduce
    repro_energy_cost: int = 0       # Energy cost of reproduction
    energy_decrease_per_step: int = 4.5   # Energy lost per time step
    energy_gain_per_prey: int = 30      # Energy gained from hunting prey
    predator_breeding_delay: int = 60  # Ticks before predator can reproduce again

    prey_max_breeding_chance: float = 0.005  # Maximum breeding chance for prey
    prey_breeding_delay: int = 10  # Ticks before prey can reproduce again


class CustomSimulation(Simulation):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Predator(Agent[PredatorPreyConfig]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.death_chance = 0.05  # Chance of dying from starvation
        self.age = 0              # Age of the predator
        self.energy = self.config.predator_start_energy  # Initial energy
        self.ticks = 0  # Ticks for aging and energy management
        self.reproduced_ticks_ago = 0  # Ticks since last reproduction

    def calculate_hunt_success(self) -> float:
        # Calculate the hunting success probability based on age resulting in a normal distribution
        if self.age < 0 or self.config.max_predator_age <= 0 or self.age > self.config.max_predator_age:
                return 0.0

        # Mean is at the midpoint of max_age
        mean = self.config.max_predator_age / 2
        # Standard deviation is set to max_age/4 for a reasonable spread
        std_dev = self.config.max_predator_age / 4

        # Normal distribution formula: f(x) = (1/(σ√(2π))) * e^(-((x-μ)^2/(2σ^2)))
        coefficient = 1 / (std_dev * math.sqrt(2 * math.pi))
        exponent = -((self.age - mean) ** 2) / (2 * std_dev ** 2)

        # Calculate the distribution value
        distribution = coefficient * math.exp(exponent)

        # Scale to return 1 at the peak (when age equals mean)
        max_distribution = coefficient  # Value of f(x) when x = mean
        scaled_value = distribution / max_distribution
        return round(scaled_value, 4)

    def check_age(self):
        # Handle aging logic and dying from old age
        if self.ticks % 60 == 0:  # Check age every 60 ticks
            self.age += 1
            if self.age >= self.config.max_predator_age:
                self.kill()

    def update_energy(self):
        # Handle energy management and dying from starvation
            self.energy -= self.config.energy_decrease_per_step
            if self.energy <= 0:
                self.kill()


    def detect_prey(self):
        # Check if there are any Prey agents in proximity
        for neighbor in self.in_proximity_performance():
            if isinstance(neighbor, Prey):
                if neighbor.is_alive() and probability(self.calculate_hunt_success()):
                    neighbor.kill()
                    return True
        return False

    def hunt_prey(self) -> None:
        if self.energy < self.config.predator_energy_to_hunt:
            prey = self.detect_prey()
            if prey:
                self.energy += self.config.energy_gain_per_prey  # Gain energy from eating prey
                if self.energy >= 100:
                    self.energy = 100  # Cap energy at 100


    def try_reproduce(self) -> None:
        self.reproduced_ticks_ago += 1
        if self.reproduced_ticks_ago >= self.config.predator_breeding_delay:  # Ensure at least 100 ticks since last reproduction
            if self.energy >= self.config.repro_energy_threshold and self.age > 1:
                self.reproduce()
                self.energy -= self.config.repro_energy_cost  # Deduct energy cost of reproduction
                self.reproduced_ticks_ago = 0


    def update(self) -> None:
        self.ticks += 1
        self.save_data('kind', 'predator')
        self.save_data('age', self.age)
        self.check_age()
        self.update_energy()
        self.hunt_prey()
        self.try_reproduce()

        self.pos += self.move * self.config.movement_speed








class Prey(Agent[PredatorPreyConfig]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.age = 0  # Age of the prey
        self.ticks = 0  # Ticks for aging
        self.last_reproduced_ticks = 0  # Ticks since last reproduction

    def calculate_breeding_chance(self) -> float:
        if self.age < 0 or self.config.max_prey_age <= 0 or self.age > self.config.max_prey_age:
            return 0.0

        # Mean is at the midpoint of max_age
        mean = self.config.max_prey_age / 2
        # Standard deviation is set to max_age/4 for a reasonable spread
        std_dev = self.config.max_prey_age / 4

        # Normal distribution formula: f(x) = (1/(σ√(2π))) * e^(-((x-μ)^2/(2σ^2)))
        coefficient = 1 / (std_dev * math.sqrt(2 * math.pi))
        exponent = -((self.age - mean) ** 2) / (2 * std_dev ** 2)

        # Calculate the distribution value
        distribution = coefficient * math.exp(exponent)

        # Scale to return max_breed_chance at the peak (when age equals mean)
        max_distribution = coefficient  # Value of f(x) when x = mean
        scaled_value = (distribution / max_distribution) * self.config.prey_max_breeding_chance

        return round(scaled_value, 4)


    def update_breed(self) -> None:
        # Handle reproduction logic
        self.last_reproduced_ticks += 1
        if self.last_reproduced_ticks >= self.config.prey_breeding_delay:  # Ensure at least 30 ticks since last reproduction
            if probability(self.calculate_breeding_chance()):
                self.last_reproduced_ticks = 0
                self.reproduce()

    def check_age(self):
        # Handle aging logic and dying from old age
        if self.ticks % 60 == 0:  # Check age every 60 ticks
            self.age += 1
            if self.age >= self.config.max_prey_age:
                self.kill()


    def update(self) -> None:
        self.ticks += 1
        self.save_data('kind', 'prey')
        self.save_data('age', self.age)
        self.check_age()
        self.update_breed()
        self.pos += self.move * self.config.movement_speed


def run_sim():
        time_start = time.time()
        sim = (
            Simulation(PredatorPreyConfig())
            .batch_spawn_agents(2000, Prey, images=["../images/prey.png"])
            .batch_spawn_agents(25, Predator, images=["../images/predator.png"])
            .run()
            .snapshots

        )
        time_end = time.time()
        print(sim.head(10))

        aggreg = sim.group_by("frame", maintain_order=True).agg([
            pl.col("kind").value_counts().alias("count"),
        ])

        frames = aggreg['frame'].to_list()
        simulation_run_data = {}
        predator_counts = []
        prey_counts = []
        predator_age_avg = []
        prey_age_avg = []

        for counts in aggreg['count']:
            pred = next((item['count'] for item in counts if item['kind'] == 'predator'), 0)
            prey = next((item['count'] for item in counts if item['kind'] == 'prey'), 0)
            predator_counts.append(pred)
            prey_counts.append(prey)


        for x in range(len(predator_counts)):
            simulation_run_data[x] = {'predator': predator_counts[x], 'prey': prey_counts[x]}

        plt.plot(frames, predator_counts, label='Predator')
        plt.plot(frames, prey_counts, label='Prey')

        plt.xlabel('Frame')
        plt.ylabel('Count')

        plt.title('Predator and Prey Counts Over Time Pred_D % = 0.001, Prey_R % = 0.005')
        plt.legend()
        plt.show()


if __name__ == "__main__":
    run_sim()