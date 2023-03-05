""" This module contains the Line class """

from __future__ import annotations

import math
import random
from typing import Any

from gym_navigation.geometry.point import Point


class Line:
    """ A line (segment) in Cartesian plane """

    start: Point
    end: Point
    slope: float
    y_intercept: float

    def __init__(self, start: Point, end: Point) -> None:
        self.start = start
        self.end = end
        if start.x_coordinate == end.x_coordinate:  # Vertical line
            self.slope = 0
            self.y_intercept = math.inf
        elif start.y_coordinate == end.y_coordinate:  # Horizontal line
            self.slope = 0
            self.y_intercept = start.y_coordinate
        else:
            self.slope = ((start.y_coordinate - end.y_coordinate)
                          / (start.x_coordinate - end.x_coordinate))
            self.y_intercept = (
                    start.y_coordinate - self.slope * start.x_coordinate)

    def get_point(self) -> Point:
        while True:
            x = random.uniform(self.start.x_coordinate, self.end.x_coordinate)
            # y = mx + q
            y = self.slope * x + self.y_intercept
            if self.contains(Point(x, y)):
                break
        return Point(x, y)

    # Calculate if the line contains a given point
    def contains(self, point: Point) -> bool:
        contains_x = (
                min(self.start.x_coordinate, self.end.x_coordinate)
                <= point.x_coordinate
                <= max(self.start.x_coordinate, self.end.x_coordinate))
        contains_y = (
                min(self.start.y_coordinate, self.end.y_coordinate)
                <= point.y_coordinate
                <= max(self.start.y_coordinate, self.end.y_coordinate))
        return contains_x and contains_y
