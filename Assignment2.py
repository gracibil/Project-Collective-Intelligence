import json
from dataclasses import dataclass, field
import random
from statistics import fmean

from polars import Boolean
from pygame import Vector2
from pygame.examples.moveit import WIDTH
from vi import Agent, Config, Simulation, Window, HeadlessSimulation
from vi.util import count, probability

@dataclass
class PredatorPreyConfig(Config):
    width : int = 100
    height : int  = 100
    radius : int = 25
    movement_speed : float = 5.0
    seed : int = 1
    duration : int = 5001
    window : Window = field(default_factory=lambda: Window(width=800, height=800))

@dataclass
class PredatorConfig(Config):
    width : int = 100
    height : int  = 100
    radius : int = 500
    movement_speed : float = 5.0
    #seed : int = 1
    duration : int = 5001


class Predator(Agent[PredatorConfig]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = "wander"  # Initial state
        self.ticks = 0
        self.energy = 120
        self.ticks_to_reproduce = 250
        self.reproduction_chance = 0.1  # Percentage chance to reproduce
        self.energy_for_reproduction = 90  # Energy threshold for reproduction
        self.hunt_chance = 0.5  # Percentage chance to successfully hunt prey

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
        if self.energy > 90:
            return
        prey = self.detect_prey()
        if prey:
            if probability(self.hunt_chance):
                prey.kill()
                self.energy += 25 # Gain energy from eating prey

    def update(self) -> None:
        self.pos += self.move
        self.hunt_prey()
        self.check_energy()
        self.update_ticks()



class Prey(Agent[PredatorPreyConfig]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = "wander"  # Initial state
        self.ticks = 0
        self.ticks_to_reproduce = 160
        self.reproduction_chance = 0.7  # Percentage chance to reproduce

    def update_ticks(self) -> None:
        self.ticks += 1

    def update_breed(self) -> None:
        if probability(self.reproduction_chance):
            self.reproduce()

    def update(self) -> None:
        self.pos += self.move
        if self.ticks == self.ticks_to_reproduce:
            self.update_breed()
            self.ticks = 0

        self.update_ticks()


def run_sim():
        (
            Simulation(PredatorPreyConfig())
            .batch_spawn_agents(50, Prey, images=["images/triangle.png"])
            .batch_spawn_agents(2, Predator, images=["images/triangle@50px.png"])
            .run()
        )


if __name__ == "__main__":
    run_sim()