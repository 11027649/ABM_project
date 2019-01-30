import random

from mesa import Model
from mesa.space import ContinuousSpace
from mesa.datacollection import DataCollector
from mesa.time import RandomActivation, RandomActivation

from progressBar import printProgressBar

from data import Data
from agent import Pedestrian, Car, Light

import math

class Traffic(Model):
    '''
    The actual model class!
    '''

    def __init__(self, y_max=33, x_max=99):

        super().__init__()

        # Do I need this?
        self.car_light = False
        self.ped_light = True
        self.sense_car = False

        self.y_max = y_max
        self.x_max = x_max

        # self.strategy = "Free"
        self.strategy = "Simultaneous"

        # Add a schedule for cars and pedestrians seperately to prevent race-conditions
        self.schedule_Car = RandomActivation(self)
        self.schedule_Pedestrian = RandomActivation(self)
        self.schedule_Light = RandomActivation(self)

        self.datacollector = DataCollector(
             {"Pedestrians": lambda m: self.schedule_Pedestrian.get_agent_count(),
              "Cars": lambda m: self.schedule_Car.get_agent_count(),
              "Midsection": lambda m: self.check_median()})

        self.space = ContinuousSpace(self.x_max, self.y_max, torus=False, x_min=0, y_min=0)

        self.lights = []
        self.place_lights()

        # we don't want to collect data when running the visualization
        self.data = False

        # this is required for the datacollector to work
        self.running = True
        self.datacollector.collect(self)

    def place_lights(self):
        '''
        Method that places the ligths for the visualization. The lights keep
        the agents from crossing when they are red.
        The ligths are agents, but they never move (so their positions are
        hardcoded here.)
        '''

        # car lights
        self.new_light((44.5, 22.4), 0, "Traf", "Red")
        self.new_light((54.5, 10.6), 0, "Traf", "Red")

        # "Down" lights
        self.new_light((53.5, 10.6), 250, "Ped", "Green")
        self.new_light((53.5, 16.2), 250, "Ped", "Green") #Median

        # "Up" Lights
        self.new_light((45.5, 16.8), 250, "Ped", "Green") #Median
        self.new_light((45.5, 22.4), 250, "Ped", "Green")


    def new_light(self, pos, state, type, color):
        '''
        Method that creates a new agent, and adds it to the correct scheduler.
        '''
        light = Light(self.next_id(), self, pos, state, type, color)
        self.lights.append(light)
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

        if self.data:
            # save level of service by saving spended time in list
            self.data.write_row_hist(type(agent).__name__, agent.unique_id, agent.time)

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
        # TODO: remove the pedestrian schedule from here if we use the new pedestrian step
        for schedule in [self.schedule_Car.agents, self.schedule_Pedestrian.agents]:
            for current_agent in schedule:
                if current_agent.dir == "up" and current_agent.pos[1] - current_agent.speed + 1 <= 0:
                    self.remove_agent(current_agent)
                if current_agent.dir == "right" and current_agent.pos[0] + current_agent.speed + 3 >= self.x_max:
                    self.remove_agent(current_agent)
                if current_agent.dir == "left" and current_agent.pos[0] -  current_agent.speed - 1 <= 0:
                    self.remove_agent(current_agent)
                if current_agent.dir == "down" and current_agent.pos[1] + current_agent.speed + 1 >= self.y_max:
                    self.remove_agent(current_agent)

        # out of bounds checks for pedestrians
        for schedule in [self.schedule_Pedestrian.agents]:
            for current_agent in schedule:
                if (current_agent.dir == "up" and current_agent.pos[1] - current_agent.speed_free< 0) or current_agent.remove == True:
                    self.remove_agent(current_agent)
                elif (current_agent.dir == "down" and current_agent.pos[1] + current_agent.speed_free >= self.y_max) or current_agent.remove == True:
                    self.remove_agent(current_agent)


        if random.random() < 0.5:

            # if there's place place a new car with probability 0.7
            pos = (0, 19.5)

            car_near = False
            for i in range(5):
                if self.space.get_neighbors((pos[0] + 5 * i, pos[1]), include_center = True, radius = 2.5):
                    car_near = True

            if random.random() < 0.5 and car_near == False:
                self.new_car(pos, "right")

        else:
            # if there's place place a new car with probability 0.7
            pos = (self.x_max - 1, 13.5)

            car_near = False
            for i in range(5):
                if self.space.get_neighbors((pos[0] - 5 * i, pos[1]), include_center = True, radius = 2.5):
                    car_near = True
            if random.random() < 0.5 and car_near == False:
                self.new_car(pos, "left")


        # # either up or down
        if random.random() < 0.5:
        #     # if there's place, place a new pedestrian with a certain probability
            pos = (self.x_max / 2 - 1 , self.y_max - 1)
        #     pos = (random.uniform(24*2,26*2),  self.y_max - 1)

            if random.random() < 0.1 and not self.space.get_neighbors(pos, include_center = True, radius = 0.8):
                self.new_pedestrian(pos, "up")

        # else:
            pos = (self.x_max / 2 + 1, 0)
        #     pos = (random.uniform(24*2,26*2),  0)

            if random.random() < 0.1 and not self.space.get_neighbors(pos, include_center = True, radius = 0.8):
                self.new_pedestrian(pos, "down")


        # Save the statistics
        self.datacollector.collect(self)

    def check_median(self, middle_pos = (50,16.5), median_width = 3, median_height = 1):
        """Used for getting the number of pedestrians in the median, though it could be used for any height band."""

        # Starts by getting the neighbours in the desired area
        neighbours = self.space.get_neighbors(middle_pos, radius=median_width+2, include_center=True)

        median_neighbours = []

        # Cycle through the neighbours checking for pedestrians and for their positions to be within the desired area.

        for neigh in neighbours:
            if type(neigh) == Pedestrian and neigh.pos[1]>=middle_pos[1]-(.5*median_height) and neigh.pos[1]<=middle_pos[1]+(.5*median_height):
                median_neighbours.append(neigh)

        # Returns the number of pedestrians found in the area.
        return len(median_neighbours)


    def run_model(self, step_count, data):
        '''
        Method that runs the model for a specific amount of steps.
        '''
        self.data = data

        for i in range(step_count):
            self.step()

        # return the data object so we can write all info from the datacollector too
        self.data.write_end_line()
