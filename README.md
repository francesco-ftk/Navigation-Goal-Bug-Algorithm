# Navigation-Goal-Bug-Algorithm
Autonomous Agents &amp; Intelligent Robotics Exam Laboratory

In this project the Bug-2 navigation goal algorithm is simulated in two dimensions. 
As can be guessed from the name, this simple and trivial algorithm provides only two behaviors to achieve the goal:
  - go towards the goal while you can
  - skirt the obstacles until you find the direction of the goal free again

So our bug robot only knows where it has to go and has local tactile sensors for obstacles.
Despite its simplicity, this is a complete algorithm.

The implementation was done in Python language using the Gym (Gymnasium now) and Pygame libraries.

Gymnasium documentation: https://gymnasium.farama.org/ 
