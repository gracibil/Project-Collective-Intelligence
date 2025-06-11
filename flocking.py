from dataclasses import dataclass
import random

from pygame import Vector2
from vi import Agent, Config, Simulation


@dataclass
class FlockingConfig(Config):
    alignment_weight: float = 1
    cohesion_weight: float = 1
    separation_weight: float = 1
    delta_time: float = 1
    mass: int = 20
    max_velocity: float = 5.0
    radius: float = 50.0

    def weights(self) -> tuple[float, float, float]:
        return (self.alignment_weight, self.cohesion_weight, self.
                separation_weight)


class FlockingAgent(Agent[FlockingConfig]):
    # By overriding `change_position`, the default behaviour is overwritten.
    # Without making changes, the agents won't move.
    def change_position(self):
        neighbors = self.in_proximity_performance()
        neighbor_positions = []
        neighbor_velocities = []

        for neighbor in neighbors:
            neighbor_positions.append(neighbor.pos)
            neighbor_velocities.append(neighbor.move)

        alignment = None
        separation = None
        cohesion = None

        if neighbor_positions:
            separation = Vector2(0, 0)
            for pos in neighbor_positions:
                diff = self.pos - pos
                if diff.length() > 0:  # Avoid division by zero
                    separation += diff / max(diff.length(), 0.1)  # Normalize to prevent extreme forces
            separation /= len(neighbor_positions)

        if neighbor_velocities:
            avg_velocity = Vector2(0, 0)
            for vel in neighbor_velocities:
                avg_velocity += vel
            avg_velocity /= len(neighbor_velocities)
            alignment = avg_velocity - self.move

        # Calculate cohesion (move towards center of mass of neighbors)
        if neighbor_positions:
            center_of_mass = Vector2(0, 0)
            for pos in neighbor_positions:
                center_of_mass += pos
            center_of_mass /= len(neighbor_positions)
            cohesion = center_of_mass - self.pos

            # Combine forces with weights
        alpha, beta, gamma = self.config.weights()
        if alignment is None:
            alignment = Vector2(0, 0)
        if separation is None:
            separation = Vector2(0, 0)
        if cohesion is None:
            cohesion = Vector2(0, 0)

        total_force = (alignment * alpha + separation * beta + cohesion * gamma) / self.config.mass

        # Update move vector
        self.move += total_force

        # Cap the velocity
        if self.move.length() > self.config.max_velocity:
            self.move = self.move.normalize() * self.config.max_velocity

        # Update position
        self.pos += self.move * self.config.delta_time

        # Ensure we call this to handle boundary conditions
        self.there_is_no_escape()


        # TODO: Modify self.move and self.pos accordingly.


(
    Simulation(
        # TODO: Modify `movement_speed` and `radius` and observe the change in behaviour.
        FlockingConfig(
            image_rotation=True,
            movement_speed=500,
            radius=200,
            alignment_weight=0.01,
            cohesion_weight=0.01,
            separation_weight=0.1,
            delta_time=1,
            max_velocity=7.0
        )
    )
    .batch_spawn_agents(50, FlockingAgent, images=["images/triangle.png"])
    .run()
)
