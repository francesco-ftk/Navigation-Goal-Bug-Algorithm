""" This __init__ file is used to register the environments """
from gym.envs.registration import register

register(
    id='NavigationGoal-v0',
    entry_point='gym_navigation.envs.navigation_goal:NavigationGoal')

register(
    id='NavigationGoal-v1',
    entry_point='gym_navigation.envs.navigation_goal_wall-e:NavigationGoalDisney')



