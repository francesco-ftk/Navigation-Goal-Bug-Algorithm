""" This module contains the lines to build the walls of the environment map """

from enum import Enum
from typing import Tuple

from gym_navigation.geometry.line import Line
from gym_navigation.geometry.point import Point


class Track(Enum):
    walls: Tuple[Line, ...]
    spawn_area: Tuple[Tuple[Tuple[float, float], Tuple[float, float]], ...]

    def __new__(cls,
                value: int,
                walls: Tuple[Line, ...] = (),
                spawn_area: Tuple[Tuple[Tuple[float, float], Tuple[float, float]], ...] = ()):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.walls = walls
        obj.spawn_area = spawn_area
        return obj

    """ numero dell'enumerazione """
    """ linee muri della mappa """
    """ area dove oggetti possono apparire (spawnare) """

    TRACK2 = (1,
              (
                  Line(Point(0, 0), Point(0, 20)),
                  Line(Point(0, 20), Point(20, 20)),
                  Line(Point(20, 20), Point(20, 0)),
                  Line(Point(20, 0), Point(0, 0))
              ),
              (
                  ((1, 19), (1, 19)),
              )
              )
