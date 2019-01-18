from mesa import Agent
from mesa import space
from mesa.space import ContinuousSpace
import random
import math
import numpy as np

class Light(Agent):
    def __init__(self, unique_id, model, pos, state, light_id):
        super().__init__(unique_id, model)

        self.pos = pos
        self.state = state
        self.light_id = light_id

    def step(self):
        '''
        This method should move the goat using the `random_move()` method implemented earlier, then conditionally reproduce.
        '''
        self.state = (self.state + 1) % 130
