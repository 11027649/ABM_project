from mesa import Agent
import random

class RandomWalker(Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)

        self.pos = pos

    def random_move(self):
        '''
        This method should get the neighbouring cells (Moore's neighbourhood), select one, and move the agent to this cell.
        '''
        # get surrounding positions
        surrounding_pos = self.model.grid.get_neighborhood(self.pos, True)

        # pick next position at random
        surrounding_tiles = len(surrounding_pos) - 1
        next_pos = surrounding_pos[random.randint(0,surrounding_tiles)]

        # move agent to next position
        self.model.grid.move_agent(self, next_pos)

class Pedestrian(RandomWalker):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model, pos)

    def step(self):
        '''
        This method should move the Sheep using the `random_move()` method implemented earlier, then conditionally reproduce.
        '''

        # do a step
        self.random_move()

class Car(Agent):
    def __init__(self, unique_id, model, pos, dir):
        super().__init__(unique_id, model)

        self.pos = pos
        self.dir = dir

    def step(self):
        '''
        Cars go straight for now.
        '''

        # take a step
        if self.dir is "left":
            next_pos = (self.pos[0] - 1, self.pos[1])
            self.model.grid.move_agent(self, next_pos)
        else:
            next_pos = (self.pos[0] + 1, self.pos[1])
            self.model.grid.move_agent(self, next_pos)
