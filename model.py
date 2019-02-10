import random

from mesa import Model
from mesa.space import ContinuousSpace
from mesa.datacollection import DataCollector
from mesa.time import RandomActivation, RandomActivation

from progressBar import printProgressBar

from data import Data
from agent import Pedestrian
from agent import Car
from agent import Light

import math

class Traffic(Model):
    '''
    The actual model class!
    '''

    def __init__(self, y_max=33, x_max=99):

        super().__init__()

        self.y_max = y_max
        self.x_max = x_max

        # self.strategy = "Free"
        self.strategy = "Simultaneous"
        # self.strategy = "Reactive"

        


        # Add a schedule for cars and pedestrians seperately to prevent race-conditions
        self.schedule_Car = RandomActivation(self)
        self.schedule_Pedestrian = RandomActivation(self)
        self.schedule_Light = RandomActivation(self)

        self.pedestrian_removed = 0
        self.cars_removed = 0

        self.space = ContinuousSpace(self.x_max, self.y_max, torus=False, x_min=0, y_min=0)

        self.lights = []
        self.place_lights()

        # Agents parameters
        self.vision_angle = 170  # Degrees
        self.N = 16 #  number of possible directions Should be >= 2!
        self.R_vision_range = 3 # Meters
        # Weights (for equation 1)
        self.Ek_w = 1
        self.Ok_w = .4
        self.Pk_w = 1
        self.Ak_w = .6
        self.Ik_w = .1
        # Speed parameters
        self.speed_mean = .134 # for max speed
        self.speed_sd = .0342
        self.gamma = 1.913 # gamma for desired speed
        self.max_density = 5.4 # maximum density in the cone
        # Crossing through red
        self.crossing_mean = .5
        self.crossing_sd = .15

        self.max_peds = 60

        self.max_peds = 110 # 10 - 20 - 40
        self.max_cars = 8 # 2 - 4 - 8

        self.spawn_rate_car = .01
        self.spawn_rate_pedes = 0.1
        # we don't want to collect data when running the visualization
        self.data = False

        self.stoch_variable = .2
        # TODO: SET CORRECTLY in agent.py
        self.max_car_speed = .8

        self.crowdedness = str(self.max_peds)

    def set_parameters(self, vision_angle=170, N=16, vision_range=3,
        Ek_w=1, Ok_w=.4, Pk_w=1, Ak_w=.6, Ik_w=.1,
        speed_mean=.134, speed_sd=.0342, gamma=1.913, max_density=5.4,
        crossing_mean=.5, crossing_sd=.15, max_cars=8,
        spawn_rate_car=.01, spawn_rate_pedes=.1, stoch_variable=.2, max_car_speed=.8,
        strategy="Simultaneous", max_peds=60):
        """ This is a function so we can set the parameters for a run. For the visualization,
        the standards are used, which are set in the init function of this model class. """


        self.N = N
        self.vision_angle = vision_angle
        self.R_vision_range

        # Weights (for equation 1)
        self.Ok_w = Ok_w
        self.Pk_w = Pk_w
        self.Ak_w = Ak_w
        self.Ik_w = Ik_w

        # Speed parameters
        self.speed_mean = speed_mean # for max speed
        self.speed_sd = speed_sd
        self.gamma = gamma # gamma for desired speed
        self.max_density = max_density # maximum density in the cone # TODO: Check what this means exactly
        # Crossing through red
        self.crossing_mean = crossing_mean
        self.crossing_sd = crossing_sd

        self.max_peds = max_peds
        self.max_cars = max_cars

        # spawn rates
        self.spawn_rate_car = spawn_rate_car
        self.spawn_rate_pedes = spawn_rate_pedes

        self.pedestrian_removed = 0
        self.cars_removed = 0

        self.stoch_variable = stoch_variable
        self.max_car_speed = max_car_speed
        self.strategy = strategy


    def place_lights(self):
        '''
        Method that places the ligths for the visualization. The lights keep
        the agents from crossing when they are red.
        The ligths are agents, but they never move (so their positions are
        hardcoded here.)
        '''

        # car lights
        self.new_light((44.5, 22.4), 0, "Car", "Red", "Bottom")
        self.new_light((54.5, 10.6), 0, "Car", "Red", "Top")

        # "Down" lights
        self.new_light((53.5, 10.6), 250, "Ped", "Green", "Top")
        self.new_light((53.5, 16.2), 250, "Ped", "Green", "Top") #Median

        # "Up" Lights
        self.new_light((45.5, 16.8), 250, "Ped", "Green", "Bottom") #Median
        self.new_light((45.5, 22.4), 250, "Ped", "Green", "Bottom")


    def new_light(self, pos, state, type, color, lane):
        '''
        Method that creates a new agent, and adds it to the correct scheduler.
        '''
        light = Light(self.next_id(), self, pos, state, type, color, lane)
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

        if type(agent) is Car:
            self.cars_removed += 1

        elif type(agent) is Pedestrian:
            self.pedestrian_removed += 1


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

        self.pedestrian_removed = 0
        self.cars_removed = 0

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


        if self.schedule_Car.get_agent_count() < self.max_cars:


            # if there's place place a new car with probability 0.7
            pos = (0, 19.5)

            car_near = False
            for i in range(5):
                if self.space.get_neighbors((pos[0] + 5 * i, pos[1]), include_center = True, radius = 2.5):
                    car_near = True

            if random.random() < self.spawn_rate_car and car_near == False:
                self.new_car(pos, "right")

            # if there's place place a new car with probability 0.7
            pos = (self.x_max - 1, 13.5)

            car_near = False
            for i in range(5):
                if self.space.get_neighbors((pos[0] - 5 * i, pos[1]), include_center = True, radius = 2.5):
                    car_near = True
            if random.random() < self.spawn_rate_car and car_near == False:
                self.new_car(pos, "left")

        if self.schedule_Pedestrian.get_agent_count() < self.max_peds:
            # # either up or down
            #     # if there's place, place a new pedestrian with a certain probability
                # pos = (self.x_max / 2 - 1 , self.y_max - 1)
            pos = (random.uniform(24*2,26*2),  self.y_max - 1)

            if random.random() < self.spawn_rate_pedes and not self.space.get_neighbors(pos, include_center = True, radius = 0.4):
                self.new_pedestrian(pos, "up")

            # pos = (self.x_max / 2 + 1, 0)
            pos = (random.uniform(24*2,26*2),  0)

            if random.random() < self.spawn_rate_pedes and not self.space.get_neighbors(pos, include_center = True, radius = 0.4):
                self.new_pedestrian(pos, "down")


        # save the statistics
        if self.data:
            self.data.write_row_info(self.schedule_Pedestrian.get_agent_count(), self.schedule_Car.get_agent_count(), self.check_median(), self.pedestrian_removed, self.cars_removed)


    def check_median(self, middle_pos = (50,16.5), median_width = 3, median_height = 1):
        """Used for getting the number of pedestrians in the median, though it could be used for any height band."""

        # Starts by getting the neighbours in the desired area
        neighbours = self.space.get_neighbors(middle_pos, radius=median_width+2, include_center=True)

        median_neighbours = []

        # cycle through the neighbours checking for pedestrians and for their positions to be within the desired area.

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
        if data.iteration is 0:
            data.generate_headers(self.strategy, step_count, self.crowdedness)

        for i in range(step_count):
            printProgressBar(i, step_count)
            self.step()

        # return the data object so we can write all info from the datacollector too
        self.data.next_iteration()
