"""
import gymnasium as gym

env = gym.make("LunarLander-v2", render_mode="human")
observation, info = env.reset(seed=42)
for _ in range(1000):
   action = env.action_space.sample()  # this is where you would insert your policy
   observation, reward, terminated, truncated, info = env.step(action)

   if terminated or truncated:
      observation, info = env.reset()
env.close()

"""

import gym

env = gym.make('gym_navigation:NavigationGoal-v1', render_mode='human', track_id=1)
env.action_space.seed(42)

observation, info = env.reset(seed=42)

for _ in range(1000):
    if observation == -1:
        observation, reward, terminated, truncated, info = env.step(0)
        print(f'observation={observation} info={info}')
    else:
        observation, reward, terminated, truncated, info = env.step(1)
        print(f'observation={observation} info={info}')

    if terminated:
        observation, info = env.reset()

env.close()

