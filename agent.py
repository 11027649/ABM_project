from mesa import Agent
from mesa.space import ContinuousSpace
import random


class Road(Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        
        self.pos = pos

class Light(Agent):
    def __init__(self, unique_id, model, pos, state):
        super().__init__(unique_id, model)
        
        self.pos = pos
        self.state = state

    def step(self):
        '''
        This method should move the Sheep using the `random_move()` method implemented earlier, then conditionally reproduce.
        '''
        self.state = (self.state + 1) % 150




class Pedestrian(Agent):
    def __init__(self, unique_id, model, pos, dir, speed = 1):
        super().__init__(unique_id, model)
        self.pos = pos
        self.dir = dir
        self.speed = speed
    def step(self):
        '''
        This method should move the Sheep using the `random_move()` method implemented earlier, then conditionally reproduce.
        '''
        for i in self.model.space.get_neighbors(self.pos, include_center = False, radius = 1):            
            if isinstance(i,Light) and i.state < 50:
                self.speed = 0
            else:
                self.speed = 1

        # take a step
        if self.dir is "up":
            next_pos = (self.pos[0], self.pos[1] + self.speed)
            self.model.space.move_agent(self, next_pos)
        else:
            next_pos = (self.pos[0], self.pos[1] - self.speed)
            self.model.space.move_agent(self, next_pos)


class Car(Agent):
    def __init__(self, unique_id, model, pos, dir, speed = 1):
        super().__init__(unique_id, model)

        self.pos = pos
        self.dir = dir
        self.speed = speed
    def step(self):
        '''
        Cars go straight for now.
        '''
        for i in self.model.space.get_neighbors(self.pos, include_center = False, radius = 1):
        # not only affected by 1 light
            if isinstance(i,Light) and i.state > 50:
                # if self.speed > 0:
                self.speed = 0
            else:
                # if self.speed < 1:
                self.speed = 1

        # take a step
        if self.dir is "left":
            next_pos = (self.pos[0] - self.speed, self.pos[1])
            self.model.space.move_agent(self, next_pos)
        else:
            next_pos = (self.pos[0] + self.speed, self.pos[1])
            self.model.space.move_agent(self, next_pos)
