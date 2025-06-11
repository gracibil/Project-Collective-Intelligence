from dataclasses import dataclass
import random

from pygame import Vector2
from vi import Agent, Config, Simulation


@dataclass
class FlockingConfig(Config):
    alignment_weight: float = 0.5
    cohesion_weight: float = 0.5
    separation_weight: float = 0.5
    delta_time: float = 3
    mass: int = 20
    max_velocity: float = 5.0
    radius: float = 50.0


    pred_pursuit_weight: float = 1.0
    pred_mass: int = 30
    pred_max_velocity: float = 6
    pred_radius: float = 100.0
    width: float = 800.0  # Simulation area width
    height: float = 600.0  # Simulation area height

    def weights(self) -> tuple[float, float, float]:
        return (self.alignment_weight, self.cohesion_weight, self.
                separation_weight)

class PredatorAgent(Agent[Config]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize instance-level position and velocity
        self.pos = Vector2(
            random.uniform(0, self.config.width),
            random.uniform(0, self.config.height)
        )
        self.move = Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * self.config.pred_max_velocity * 0.5

    def change_position(self):
        # Get nearby FlockingAgents within radius
        prey_positions = []
        for neighbor in self.in_proximity_performance():
            if isinstance(neighbor, FlockingAgent):  # Only consider FlockingAgents as prey
                prey_positions.append(neighbor.pos)

        # Pursuit: Steer towards the closest FlockingAgent
        pursuit = Vector2(0, 0)
        if prey_positions:
            # Find the closest prey
            closest_prey = min(prey_positions, key=lambda pos: (self.pos - pos).length())
            diff = closest_prey - self.pos
            if diff.length() > 0:  # Avoid division by zero
                pursuit = diff / diff.length()  # Normalize to steer toward prey

        # If no prey, continue in current direction (pursuit remains zero, so move is unchanged)
        total_force = pursuit * self.config.pred_pursuit_weight / self.config.pred_mass

        # Update velocity: Vboid = Vboid + ftotal
        self.move += total_force

        # Cap velocity
        if self.move.length() > self.config.pred_max_velocity:
            self.move = self.move.normalize() * self.config.pred_max_velocity

        # Update position
        self.pos += self.move * self.config.delta_time

        # Handle boundary conditions
        self.there_is_no_escape()


class FlockingAgent(Agent[FlockingConfig]):
    # By overriding `change_position`, the default behaviour is overwritten.
    # Without making changes, the agents won't move.
    def change_position(self):
        neighbors = self.in_proximity_performance()
        neighbor_positions = []
        neighbor_velocities = []

        # Detect predators in a radius of 100 and avoid them
        neighbors = self.in_proximity_performance()
        predators = [n for n in neighbors if isinstance(n, PredatorAgent)]
        predators_to_avoid = []

        for predator in predators:
            # if distance from predator is less than 10 add to avoidance vector
            if (self.pos - predator.pos).length() < self.config.pred_radius:
                predators_to_avoid.append(predator)

        if predators_to_avoid:
            print('Predator detected! FlockingAgent will avoid it.')
            # Calculate avoidance vector
            avoidance_vector = Vector2(0, 0)
            for predator in predators:
                diff = self.pos - predator.pos
                if diff.length() > 0:
                    avoidance_vector += diff / diff.length()
            # Average the avoidance vector
            avoidance_vector /= len(predators)
            # Normalize and scale the avoidance vector to ensure realistic movement
            if avoidance_vector.length() > 0:
                avoidance_vector = avoidance_vector.normalize() * 2.0  # Scale and normalize
            self.move += avoidance_vector

            # Cap the velocity to prevent exceeding the maximum allowed speed
            if self.move.length() > self.config.max_velocity:
                self.move = self.move.normalize() * self.config.max_velocity


        neighbors = self.in_proximity_performance()
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
    .batch_spawn_agents(2, PredatorAgent, images=["images/triangle@50px.png"])
    .run()
)


