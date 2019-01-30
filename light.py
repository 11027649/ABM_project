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
        self.color = "Red"
        self.closest = math.inf
        
    def step(self):
        '''
        Update the state of the light.
        '''
        self.state = (self.state + 1) % 500

        if self.model.strategy == "Simultaneous":
            self.simultaneous()
        elif self.model.strategy == "Free":
            self.free()

        if self.unique_id == 1 or self.unique_id == 2:
            self.closest = self.closest_car()

    def simultaneous(self):
        if self.state <= 300:
            self.color = "Red"
        elif self.state <= 450:
            self.color = "Green"
        else:
            self.color = "Orange"

    def free(self):
        self.color = "Green"

    def closest_car(self):

        center = 15
        if self.unique_id == 1:
            print('unique id 1')       

            for i in range(16):
                neighbours = self.model.space.get_neighbors((self.pos[0] + center - i * 2.5 * 2, 16.5 + 3), include_center = True, radius = 2.6)
                if len(neighbours) > 0:
                    break


        elif self.unique_id == 2:
            print('unique id 2')       

            for i in range(16):
                neighbours = self.model.space.get_neighbors((self.pos[0] - center + i * 2.5 * 2, 16.5 - 3), include_center = True, radius = 2.6) 
                if len(neighbours) > 0:
                    break
                    
        if len(neighbours) > 0:
            min_distance = math.inf
            for neigh in neighbours:
                cur_distance = abs(self.pos[0] - neigh.pos[0])
                if cur_distance < min_distance:
                    min_distance = cur_distance
            print(min_distance)
            return min_distance
        return math.inf

            
# simultaneous strategy
# 3 & 4 are the same
# 5 & 6 are the same
