from mesa import Agent
from mesa import space
from mesa.space import ContinuousSpace
import random
import math
import numpy as np

class Light(Agent):
    def __init__(self, unique_id, model, pos, state):
        super().__init__(unique_id, model)

        self.pos = pos
        self.state = state

        self.update_color()

    def step(self):
        '''
        Update the state of the light.
        '''
        self.state = (self.state + 1) % 500
        self.update_color()

    def update_color(self):
        if self.state <= 300:
            self.color = "Red"
        elif self.state <= 450:
            self.color = "Green"
        else:
            self.color = "Orange"

# simultaneous strategy
# 3 & 4 are the same
# 5 & 6 are the same
