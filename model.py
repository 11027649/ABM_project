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

        self.y_max = y_max
        self.x_max = x_max

        # Add a schedule for cars and pedestrians seperately to prevent race-conditions
        self.schedule_Car = RandomActivation(self)
        self.schedule_Pedestrian = RandomActivation(self)
        self.schedule_Light = RandomActivation(self)

        self.datacollector = DataCollector(
             {"Pedestrians": lambda m: self.schedule_Pedestrian.get_agent_count(),
              "Cars": lambda m: self.schedule_Car.get_agent_count()})

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
        # Simultaneous Strategy

        # car lights
        self.new_light((44.54, 22.4), 0, 1)
        self.new_light((54.46, 10.6), 0, 2)

        #"Up" lights
        self.new_light((45.54, 22.4), 250, 6)
        self.new_light((53.46, 16.2), 250, 4) #Median

        #"Down" Lights
        self.new_light((45.54, 16.8), 250, 5) #Median
        self.new_light((53.46, 10.6), 250, 3)

        #Alternating strategy
        """

        # car lights
        self.new_light((int(0.45 * self.x_max), int(0.6 * self.y_max)), 200, 1) #Bottom Light
        self.new_light((int(0.55 * self.x_max), int(0.4 * self.y_max)), 0, 2) #Top Light

        #"Up" lights
        self.new_light((23 * 2, 30), 200, 6)
        self.new_light((27 * 2, 24.65), 400, 4) #Median

        #"Down" Lights
        self.new_light((23 * 2, 25.35), 200, 5) #Median
        self.new_light((27 * 2, 20), 400, 3)

        """



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

        # if self.data:
        #     # save level of service by saving spended time in list
        #     self.data.write_row_hist(type(agent).__name__, agent.unique_id, agent.time)

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
                # print(current_agent.dir, current_agent.direction, current_agent.target_point, current_agent.pos[1], current_agent.speed_free, current_agent.pos[1] - current_agent.speed_free)
                if (current_agent.dir == "up" and current_agent.pos[1] - current_agent.speed_free< 0) or current_agent.remove == True:
                    self.remove_agent(current_agent)
                elif (current_agent.dir == "down" and current_agent.pos[1] + current_agent.speed_free >= self.y_max) or current_agent.remove == True:
                    self.remove_agent(current_agent)


        # if random.random() < 0.5:
        #
        #     # if there's place place a new car with probability 0.7
        #     pos = (0, 19.5)
        #
        #     car_near = False
        #     for i in range(5):
        #         if self.space.get_neighbors((pos[0] + 5 * i, pos[1]), include_center = True, radius = 2.5):
        #             car_near = True
        #
        #     if random.random() < 0.03 and car_near == False:
        #         self.new_car(pos, "right")
        #
        # else:
        #     # if there's place place a new car with probability 0.7
        #     pos = (self.x_max - 1, 13.5)
        #
        #     car_near = False
        #     for i in range(5):
        #         if self.space.get_neighbors((pos[0] - 5 * i, pos[1]), include_center = True, radius = 2.5):
        #             car_near = True
        #     if random.random() < 0.03 and car_near == False:
        #         self.new_car(pos, "left")


        # either up or down
        if random.random() < 1:
            # if there's place, place a new pedestrian with a certain probability
            pos = (self.x_max / 2 - 1 , self.y_max - 1)

            if random.random() < 1 and not self.space.get_neighbors(pos, include_center = True, radius = .5):
                self.new_pedestrian(pos, "up")

        else:
            pos = (self.x_max / 2 + 1, 0)

            if random.random() < 1 and not self.space.get_neighbors(pos, include_center = True, radius = .5):
                self.new_pedestrian(pos, "down")

        # Save the statistics
        self.datacollector.collect(self)

    def run_model(self, step_count, data):
        '''
        Method that runs the model for a specific amount of steps.
        '''
        self.data = data

        for i in range(step_count):
            self.step()

        # return the data object so we can write all info from the datacollector too
        self.data.write_end_line()
