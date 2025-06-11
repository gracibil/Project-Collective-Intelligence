from dataclasses import dataclass, field
import random
from statistics import fmean
from pygame import Vector2
from pygame.examples.moveit import WIDTH
from vi import Agent, Config, Simulation, Window
from vi.util import count, probability

sites = {
    0: {
        "width": 200,
        "height": 200,
        "center_x": 400,
        "center_y": 400,
        "image": "images/site_fill.png"
    }
}

@dataclass
class AggregationConfig(Config):
    width : int = 100
    height : int  = 100
    radius : int = 50
    movement_speed : float = 20.0
    seed : int = 1
    duration : int = 0

    window : Window = field(default_factory=lambda: Window(width=800, height=800))


class AggregationAgent(Agent[AggregationConfig]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = "wander"  # Initial state
        self.possible_directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
        self.direction = self.select_random_direction()
        self.ticks = 0
        self.next_tick_update = 0

    def update_next_tick(self):
        # random int between 1 and 150
        self.ticks = 0
        self.next_tick_update = random.randint(1, 150)

    def select_random_direction(self) -> Vector2:
        direction = random.choice(self.possible_directions)
        match direction:
            case 'N':
                return Vector2(0, -1)
            case 'NE':
                return Vector2(1, -1)
            case 'E':
                return Vector2(1, 0)
            case 'SE':
                return Vector2(1, 1)
            case 'S':
                return Vector2(0, 1)
            case 'SW':
                return Vector2(-1, 1)
            case 'W':
                return Vector2(-1, 0)
            case 'NW':
                return Vector2(-1, -1)


    def detect_aggregation_site(self) -> bool:
        return self.on_site()

    def detect_agents_in_proximity(self) -> int:
        agents_in_proximity = count(self.in_proximity_accuracy())
        return agents_in_proximity

    def calculate_prob_leave(self) -> float:
        agents_in_proximity = self.detect_agents_in_proximity()
        prob = 1 / agents_in_proximity if agents_in_proximity > 0 else 1
        if prob > 0.1:
            prob = 0
            return prob
        else:
            return 0

    def calculate_prob_join(self) -> float:
        prob = 1 - self.calculate_prob_leave()

        return prob

    def check_collision_with_agents(self):
        # Check if the agent is colliding with any other agents
        distance_to_others = [self.pos.distance_to(other_agent.pos) for other_agent in self.in_proximity_performance()]

        for distance in distance_to_others:
            if distance < 14:  # Assuming a collision threshold of 10 pixels
                print(f"Collision detected with another agent at distance {distance}")
                return True
        return False

    def site_boundries(self):
        site_id = self.on_site_id()
        if site_id is None:
            return None
        site = sites[site_id]
        return {
            "left": site["center_x"] - site["width"] / 2,
            "right": site["center_x"] + site["width"] / 2,
            "top": site["center_y"] - site["height"] / 2,
            "bottom": site["center_y"] + site["height"] / 2
        }

    def within_site_boundries(self):
        boundaries = self.site_boundries()
        if boundaries is None:
            return False
        return (boundaries["left"] <= self.pos.x <= boundaries["right"] and
                boundaries["top"] <= self.pos.y <= boundaries["bottom"])


    def choose_direction_to_stay_within_site(self):
        boundaries = self.site_boundries()
        if boundaries is None:
            return Vector2(0, 0)

        directions = []
        if self.pos.x < boundaries["left"]:
            directions.append(Vector2(1, 0))
        elif self.pos.x > boundaries["right"]:
            directions.append(Vector2(-1, 0))
        if self.pos.y < boundaries["top"]:
            directions.append(Vector2(0, 1))
        elif self.pos.y > boundaries["bottom"]:
            directions.append(Vector2(0, -1))

        return random.choice(directions) if directions else Vector2(0, 0)



    def wander_loop(self):
        if self.detect_aggregation_site():
            prob_join = self.calculate_prob_join()
            random_value = random.random()
            if prob_join > random_value:
                self.state = "join"

        self.move = self.direction
        self.pos += self.move * self.config.movement_speed
        self.there_is_no_escape()
        self.ticks += 1


    def join_loop(self):
        distances_from_others = [dist for _, dist in self.in_proximity_accuracy()]
        distances_from_others.sort()
        frst_five = distances_from_others[:5]  # Get the first five distances
        if  len(frst_five) == 0:
            avg_distance_from_others = 100
        else:
        # Calculate the average distance from other agents
            avg_distance_from_others = fmean(frst_five) if frst_five else 0

        # If the agent is close by others, isn't colliding, and is within the site boundaries, it will stop moving
        if avg_distance_from_others < 30 and not self.check_collision_with_agents() and self.on_site():
            if self.within_site_boundries():
                self.state = "still"
                self.freeze_movement()
        else:
            move = self.choose_direction_to_stay_within_site()
            self.pos += move * self.config.movement_speed
            self.there_is_no_escape()


    def still_loop(self):
        self.freeze_movement()
        prob_leave = self.calculate_prob_leave()
        random_value = random.random()
        if prob_leave > random_value:
            self.state = "leave"
            self.direction = self.select_random_direction()
            self.continue_movement()


    def leave_loop(self):
        # Logic to leave the aggregation site

        if not self.on_site():
            self.state = 'wander'

        self.pos += self.direction * self.config.movement_speed
        self.there_is_no_escape()

    def update(self):
        if self.ticks >= self.next_tick_update:
            self.update_next_tick()
            self.direction = self.select_random_direction()

        if self.state == "wander":
            self.wander_loop()

        if self.state == "join":
            self.join_loop()

        if self.state == "still":
            self.still_loop()

        if self.state == "leave":
            self.leave_loop()



(
    Simulation(AggregationConfig())
    .spawn_site("images/site_fill.png", 400, 400)
    .batch_spawn_agents(50, AggregationAgent, images=["images/triangle.png"])
    .run()
)