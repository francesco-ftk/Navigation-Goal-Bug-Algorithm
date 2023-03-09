""" This module contains the Navigation Goal environment class """

import pygame
from gym import spaces
from pygame import Surface
import math
from typing import Tuple

from gym_navigation.enums.color import Color
from gym_navigation.geometry.line import Line
from gym_navigation.geometry.point import Point
from gym_navigation.geometry.pose import Pose
from gym_navigation.envs.navigation_env import Navigation


class NavigationGoal(Navigation):
    """ The Navigation Goal environment """

    GOAL_THRESHOLD = 0.4  # goal radius
    COLLISION_THRESHOLD = 0.4  # robot radius
    OBSTACLE_RADIUS = 0.8
    MINIMUM_DISTANCE_ROBOT_GOAL = 12  # min distance between robot and goal
    MINIMUM_DISTANCE_OBSTACLE = 4  # min distance between obstacles
    MINIMUM_DISTANCE = 2.5  # min distance among obstacles, robot and goal
    MINIMUM_SAFE_DISTANCE = 1.5  # 2
    N_OBSTACLES = 3

    COLLISION_REWARD = -1.0
    GOAL_REWARD = 1.0
    TRANSITION_REWARD = 0.5

    SHIFT = 0.1

    pose: Pose  # robot pose
    goal: Point
    circular_obstacles: Tuple[Point, ...]
    goal_direction: Line
    distance_from_goal: float
    previous_distance_from_goal: float
    last_action_performed: int
    nearer_obstacle_index: int
    initial_yaw: float
    circumnavigation_terminated: bool

    def __init__(self, render_mode=None, track_id: int = 1) -> None:
        super().__init__(render_mode, track_id)

        self.observation_space = spaces.Discrete(1)
        # The id of the too much near obstacle or -1

        self.action_space = spaces.Discrete(2)
        # 0: go_toward_goal
        # 1: go_tangent_to_obstacles

        pygame.display.set_caption('Navigation Goal')

    def perform_action(self, action: int) -> None:
        if action == 0:
            self.pose.shift(self.SHIFT, 0.0)
        else:
            if self.last_action_performed == 0:
                self.move_tangent_to_obsatcle()
            else:
                token_pose = Pose(self.pose.position, self.pose.yaw)
                token_yaw = self.pose.calculate_angle_difference(self.goal)
                token_pose.rotate(token_yaw)
                # Check if the obstacle is back facing the goal
                angle_to_face_obstacle = math.fabs(token_pose.calculate_angle_difference(self.circular_obstacles[self.nearer_obstacle_index]))
                # 3.14 è 180°
                if token_pose.is_closer_yaw(self.initial_yaw) and angle_to_face_obstacle >= 1.7:
                    self.pose.rotate(token_yaw)
                    self.pose.shift(self.SHIFT, 0.0)
                else:
                    self.move_tangent_to_obsatcle()

        self.last_action_performed = action
        self.previous_distance_from_goal = self.distance_from_goal
        self.distance_from_goal = self.pose.position.calculate_distance(self.goal)

    def move_tangent_to_obsatcle(self) -> None:
        obstacle_to_overcome = self.circular_obstacles[self.nearer_obstacle_index]
        yaw = self.pose.calculate_angle_difference(obstacle_to_overcome)
        self.pose.rotate(yaw)   # the robot faces the obstacle
        self.pose.rotate(90.0)  # right direction tangent to obstacle
        self.pose.shift(self.SHIFT, 0.0)
        yaw = self.pose.calculate_angle_difference(obstacle_to_overcome)
        self.pose.rotate(yaw)
        distance_after_shift = self.pose.position.calculate_distance(obstacle_to_overcome)
        shift_closer = distance_after_shift - self.MINIMUM_SAFE_DISTANCE + 0.1
        self.pose.shift(shift_closer, 0.0)


    def get_observation(self) -> int:
        index = -1
        min_obstacle_distance = self.MINIMUM_SAFE_DISTANCE
        for obstacle in self.circular_obstacles:
            if self.pose.position.calculate_distance(obstacle) < min_obstacle_distance:
                min_obstacle_distance = self.pose.position.calculate_distance(obstacle)
                index = self.circular_obstacles.index(obstacle)
        self.nearer_obstacle_index = index
        return index

    def collision_occurred(self) -> bool:
        collision_occurred = False
        for obstacle in self.circular_obstacles:
            if self.pose.position.calculate_distance(obstacle) < (self.OBSTACLE_RADIUS + self.COLLISION_THRESHOLD):
                collision_occurred = True
                break
        return collision_occurred

    def check_if_terminated(self) -> bool:
        return self.collision_occurred() or self.goal_reached()

    def create_info(self) -> dict:
        if self.collision_occurred():
            return {"result": "Collision with obstacle!"}
        elif self.goal_reached():
            return {"result": "Goal reached!!!"}
        else:
            return {"result": "bug-robot proceed"}

    def check_if_truncated(self) -> bool:
        return False

    def goal_reached(self) -> bool:
        return self.distance_from_goal < (self.GOAL_THRESHOLD + self.COLLISION_THRESHOLD)

    def calculate_reward(self, action: int) -> float:
        if self.collision_occurred():
            reward = self.COLLISION_REWARD
        elif self.goal_reached():
            reward = self.GOAL_REWARD
        else:
            reward = self.TRANSITION_REWARD
        return reward

    def init_environment(self, options=None) -> None:
        self.circumnavigation_terminated = True
        self.init_goal()
        self.init_robot_pose()
        self.circular_obstacles = ()
        self.init_obstacles()

    def init_goal(self) -> None:
        area = self.np_random.choice(self.track.spawn_area)
        x_coordinate = self.np_random.uniform(area[0][0], area[0][1])
        y_coordinate = self.np_random.uniform(area[1][0], area[1][1])
        self.goal = Point(x_coordinate, y_coordinate)

    def init_robot_pose(self) -> None:
        while True:
            area = self.np_random.choice(self.track.spawn_area)
            x_coordinate = self.np_random.uniform(area[0][0], area[0][1])
            y_coordinate = self.np_random.uniform(area[1][0], area[1][1])
            position = Point(x_coordinate, y_coordinate)
            distance_from_goal = position.calculate_distance(self.goal)
            if distance_from_goal > self.MINIMUM_DISTANCE_ROBOT_GOAL:
                break

        start_position_robot_goal_line = Point(position.x_coordinate, position.y_coordinate)
        # ROBOT INITIAL ORIENTATION AND GOAL DIRECTION SETTINGS
        self.goal_direction = Line(start_position_robot_goal_line, self.goal)
        self.pose = Pose(position, 0)   # default orientation in y axis
        yaw = self.pose.calculate_angle_difference(self.goal)
        self.initial_yaw = yaw
        self.pose.rotate(yaw)

        self.distance_from_goal = self.pose.position.calculate_distance(self.goal)
        self.previous_distance_from_goal = self.distance_from_goal

    def init_obstacles(self) -> None:
        for _ in range(self.N_OBSTACLES):
            while True:
                obstacle_center = self.goal_direction.get_point()
                distance_from_robot = obstacle_center.calculate_distance(self.pose.position)
                distance_from_goal = obstacle_center.calculate_distance(self.goal)

                if distance_from_robot > self.MINIMUM_DISTANCE and distance_from_goal > self.MINIMUM_DISTANCE:
                    break
            self.circular_obstacles += (obstacle_center,)

    def draw(self, canvas: Surface) -> None:
        # BACKGROUND
        canvas.fill(Color.WHITE.value)

        # WALLS
        for wall in self.world:
            pygame.draw.line(canvas,
                             Color.BLACK.value,
                             self.convert_point(wall.start),
                             self.convert_point(wall.end),
                             self.WIDTH)
        # INITIAL GOAL DIRECTION
        pygame.draw.line(canvas,
                         Color.YELLOW.value,
                         self.convert_point(self.goal_direction.start),
                         self.convert_point(self.goal_direction.end),
                         self.WIDTH)

        # CIRCULAR OBSTACLES
        for obstacle in self.circular_obstacles:
            pygame.draw.circle(canvas,
                               Color.BLUE.value,
                               self.convert_point(obstacle),
                               self.OBSTACLE_RADIUS * self.RESOLUTION)

        # BUG ROBOT
        pygame.draw.circle(canvas,
                           Color.GREEN.value,
                           self.convert_point(self.pose.position),  # center
                           self.COLLISION_THRESHOLD * self.RESOLUTION)  # radius

        # GOAL
        pygame.draw.circle(canvas,
                           Color.RED.value,
                           self.convert_point(self.goal),
                           self.GOAL_THRESHOLD * self.RESOLUTION)

    # Converte punti per essere disegnati in window
    def convert_point(self, point: Point) -> Tuple[int, int]:
        pygame_x = (round(point.x_coordinate * self.RESOLUTION) + self.X_OFFSET)
        pygame_y = (self.window_size - round(point.y_coordinate * self.RESOLUTION) + self.Y_OFFSET)
        return pygame_x, pygame_y
