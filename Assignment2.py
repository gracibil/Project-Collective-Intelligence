import random
from dataclasses import dataclass, field
from vi import Agent, Config, Simulation, Window, HeadlessSimulation
from vi.util import count, probability

@dataclass
class PredatorPreyConfig(Config):
    width : int = 100
    height : int  = 100
    radius : int = 20
    movement_speed : float = 5.0
    seed : int = 1
    duration : int = 5001
    window : Window = field(default_factory=lambda: Window(width=1000, height=1000))

@dataclass
class PredatorConfig(Config):
    width : int = 100
    height : int  = 100
    radius : int = 500
    movement_speed : float = 5.0
    seed : int = 1
    duration : int = 5001


class Predator(Agent[PredatorConfig]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = "wander"  # Initial state
        self.ticks = 0
        self.energy = 125
        self.ticks_to_reproduce = 175
        self.reproduction_chance = 1  # Percentage chance to reproduce
        self.energy_for_reproduction = 80  # Energy threshold for reproduction
        self.hunt_chance = 1  # Percentage chance to successfully hunt prey
        self.speed = 0.7

    def update_ticks(self) -> None:
        self.ticks += 1
        self.energy -= 1  # Decrease energy with each tick


    def detect_prey(self):
        # Check if there are any Prey agents in proximity
        for neighbor in self.in_proximity_performance():
            if isinstance(neighbor, Prey):
                return neighbor

        return False

    def check_energy(self) -> None:
        if self.energy <= 0:
            self.kill()

        if self.energy > self.energy_for_reproduction:
            self.try_reproduce()

    def try_reproduce(self) -> None:
        if self.ticks >= self.ticks_to_reproduce:
            if probability(self.reproduction_chance):
                self.reproduce()
                self.ticks = 0  # Reset ticks after reproduction


    def hunt_prey(self) -> None:
        prey = self.detect_prey()

        if prey and probability(self.hunt_chance):
            prey.kill()
            self.energy += 10 # Gain energy from eating prey

    def update(self) -> None:

        self.hunt_prey()
        self.check_energy()
        self.update_ticks()
        self.pos += self.move * self.speed


class Prey(Agent[PredatorPreyConfig]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = "wander"  # Initial state
        self.ticks = 0
        self.ticks_to_reproduce = random.randint(80, 100)
        self.reproduction_chance = 0.9  # Percentage chance to reproduce
        self.speed = 0.4

    def update_ticks(self) -> None:
        self.ticks += 1

    def update_breed(self) -> None:
        if probability(self.reproduction_chance):
            self.reproduce()
            self.ticks_to_reproduce = random.randint(80, 100)

    def update(self) -> None:

        if self.ticks == self.ticks_to_reproduce:
            self.update_breed()
            self.ticks = 0

        self.update_ticks()
        self.pos += self.move * self.speed

def run_sim():
    (
        Simulation(PredatorPreyConfig())
        .batch_spawn_agents(100, Prey, images=["images/prey.png"])
        .batch_spawn_agents(10, Predator, images=["images/predator.png"])
        .run()
    )


if __name__ == "__main__":
    run_sim()