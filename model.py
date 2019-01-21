import random

from mesa import Model
from mesa.space import ContinuousSpace
from mesa.datacollection import DataCollector
from mesa.time import RandomActivation, RandomActivation

from collections import defaultdict

from agent import Pedestrian, Car, Light
import math

class Traffic(Model):
    '''
    The actual model class!
    '''

    def __init__(self, y_max=50, x_max=50):

        super().__init__()

        self.y_max = y_max
        self.x_max = x_max
        self.time_list = defaultdict(list)

        # Add a schedule for cars and pedestrians seperately to prevent race-conditions
        self.schedule_Car = RandomActivation(self)
        self.schedule_Pedestrian = RandomActivation(self)
        self.schedule_Light = RandomActivation(self)

        self.datacollector = DataCollector(
             {"Cars and pedestrians": lambda m: self.schedule_Pedestrian.get_agent_count()})

        self.space = ContinuousSpace(self.x_max, self.y_max, torus=False, x_min=0, y_min=0)
        self.place_lights()

        # This is required for the datacollector to work
        self.running = True
        self.datacollector.collect(self)

    def place_lights(self):
        '''
        Method that places the ligths for the visualization. The lights keep
        the agents from crossing when they are red.
        '''

        # car lights
        self.new_light((20,30), 0, 1)
        self.new_light((30,20), 0, 2)

        # pedestrian lights
        self.new_light((27, 20), 75, 3)
        self.new_light((23, 30), 75, 6)

        # lights in the middle, not assigned for now and simultaneous with the
        # other pedestrian lights
        self.new_light((27, 24.65), 75, 4)
        self.new_light((23, 25.35), 75, 5)


    def new_light(self, pos, state, light_id):
        '''
        Method that creates a new agent, and adds it to the correct scheduler.
        '''
        light = Light(self.next_id(), self, pos, state, light_id)
        self.space.place_agent(light, pos)
        getattr(self, 'schedule_Light').add(light)

    def new_car(self, pos, dir):
        '''
        Method that creates a new agent, and adds it to the correct scheduler.
        '''
        car = Car(self.next_id(), self, pos, dir)

        self.space.place_agent(car, pos)
        getattr(self, 'schedule_Car').add(car)

    def new_pedestrian(self, pos, dir):
        '''
        Method that creates a new agent, and adds it to the correct scheduler.
        '''
        pedestrian = Pedestrian(self.next_id(), self, pos, dir)

        self.space.place_agent(pedestrian, pos)
        getattr(self, 'schedule_Pedestrian').add(pedestrian)

    def remove_agent(self, agent):
        '''
        Method that removes an agent from the grid and the correct scheduler.
        '''

        # save level of service by saving spended time in list
        self.time_list[type(agent).__name__].append(agent.time)

        # if we remove the agents, save the time they spended in the grid
        self.space.remove_agent(agent)
        getattr(self, f'schedule_{type(agent).__name__}').remove(agent)


    def step(self):
        '''
        Method that calls the step method for each car.
        '''

        # let existing cars take a step
        self.schedule_Light.step()
        self.schedule_Pedestrian.step()
        self.schedule_Car.step()

        # out of bounds checks for cars and pedestrians
        for schedule in [self.schedule_Car.agents, self.schedule_Pedestrian.agents]:
            for current_agent in schedule:
                if current_agent.dir == "up" and current_agent.pos[1] - current_agent.speed + 1 <= 0:
                    self.remove_agent(current_agent)
                if current_agent.dir == "right" and current_agent.pos[0] + current_agent.speed + 1 >= self.x_max:
                    self.remove_agent(current_agent)
                if current_agent.dir == "left" and current_agent.pos[0] -  current_agent.speed + 1 <= 0:
                    self.remove_agent(current_agent)
                if current_agent.dir == "down" and current_agent.pos[1] + current_agent.speed + 1 >= self.y_max:
                    self.remove_agent(current_agent)

        if random.random() < 0.5:

            # if there's place place a new car with probability 0.7
            pos = (2, self.y_max/2 + 2.5)
            if random.random() < 0.7 and not self.space.get_neighbors(pos, include_center = True, radius = 4):
                self.new_car(pos, "right")

        else:
            # if there's place place a new car with probability 0.7
            pos = (self.x_max - 3, self.y_max/2 - 2.5)
            if random.random() < 0.7 and not self.space.get_neighbors(pos, include_center = True, radius = 4):
                self.new_car(pos, "left")


        if random.random() < 0.5:

            # if there's place place a new car with probability 0.7
            x = int(self.x_max / 2 - 1)
            y = self.y_max - 1
            pos = (x,y)
            if random.random() < 0.7 and not self.space.get_neighbors(pos, include_center = True, radius = 2):
                self.new_pedestrian(pos, "up")

        else:
            # if there's place place a new car with probability 0.7

            x = int(self.x_max / 2 + 1)

            y = 0
            pos = (x,y)
            if random.random() < 0.7 and not self.space.get_neighbors(pos, include_center = True, radius = 2):
                self.new_pedestrian(pos, "down")

        # Save the statistics
        self.datacollector.collect(self)

    def run_model(self, step_count=1):
        '''
        Method that runs the model for a specific amount of steps.
        '''
        for i in range(step_count):
            self.step()

        return self.time_list
