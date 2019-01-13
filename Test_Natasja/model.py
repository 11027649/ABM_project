import random

from mesa import Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from mesa.time import RandomActivation

from agent import Pedestrian, Car, RandomWalker
import math

class Traffic(Model):
    '''
    '''

    def __init__(self, height=20, width=20,
                 initial_cars=2, initial_pedestrians=0):

        super().__init__()

        self.height = height
        self.width = width
        self.initial_cars = initial_cars
        self.initial_pedestrians = initial_pedestrians

        # Add a schedule for cars and pedestrians seperately to prevent race-conditions
        self.schedule_Car = RandomActivation(self)
        self.schedule_Pedestrian = RandomActivation(self)

        self.grid = MultiGrid(self.width, self.height, torus=True)

        # Create cars and pedestrians
        self.init_population(Car, self.initial_cars)
        self.init_population(Pedestrian, self.initial_pedestrians)

    def init_population(self, agent_type, n):
        '''
        Method that provides an easy way of making a bunch of agents at once.
        '''

        # a car that starts on the right
        x = self.width - 1
        y = math.ceil(self.height/2 + 1)

        self.new_car((x, y), "left")

        # a car that starts on the left
        x = 0
        y = math.ceil(self.height/2 - 2)
        self.new_car((x, y), "right")

    def new_car(self, pos, dir):
        '''
        Method that creates a new agent, and adds it to the correct scheduler.
        '''
        car = Car(self.next_id(), self, pos, dir)

        self.grid.place_agent(car, pos)
        getattr(self, 'schedule_Car').add(car)

    def remove_agent(self, agent):
        '''
        Method that removes an agent from the grid and the correct scheduler.
        '''
        self.grid.remove_agent(agent)
        getattr(self, f'schedule_{type(agent).__name__}').remove(agent)

    def step(self):
        '''
        Method that calls the step method for each car.
        '''

        # let existing cars take a step
        self.schedule_Car.step()

        # TODO: if there are no more cars in the beginning of the lanes, add cars with a probability


    def run_model(self, step_count=100):
        '''
        Method that runs the model for a specific amount of steps.
        '''
        for i in range(step_count):
            self.step()
