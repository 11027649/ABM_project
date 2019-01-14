import random

from mesa import Model
from mesa.space import ContinuousSpace
from mesa.datacollection import DataCollector
from mesa.time import RandomActivation

from agent import Pedestrian, Car, Road, Light
import math

class Traffic(Model):
    '''
    '''

    def __init__(self, y_max=30, x_max=30,
                 initial_cars=0, initial_pedestrians=0):

        super().__init__()

        self.y_max = y_max
        self.x_max = x_max
        self.initial_cars = initial_cars
        self.initial_pedestrians = initial_pedestrians

        # Add a schedule for cars and pedestrians seperately to prevent race-conditions
        self.schedule = RandomActivation(self)
        self.schedule_light = RandomActivation(self)

        self.space = ContinuousSpace(self.x_max, self.y_max, torus=False, x_min=0, y_min=0)

        # Create cars and pedestrians
        self.init_population(Car, self.initial_cars)
        # self.init_population(Pedestrian, self.initial_pedestrians)

    def init_population(self, agent_type, n):
        '''
        Method that provides an easy way of making a bunch of agents at once.
        '''
        self.new_road()
        print((int(self.y_max/2) + 2, int(self.x_max/2 + 2)))
        self.new_light((int(self.y_max/2) + 2, int(self.x_max/2 + 2)))
        self.new_light((int(self.y_max/2) - 2, int(self.x_max/2 - 3)))

        # a car that starts on the left
        x = 0
        y = math.ceil(self.y_max/2 - 2)
        self.new_car((x, y), "right")
        print(x,y)
        # a car that starts on the right
        x = self.x_max - 1
        y = math.ceil(self.y_max/2 + 1)
        self.new_car((x, y), "left")
        
        # a pedestrian that starts on the bottom
        x = int(self.x_max / 2 - 1)
        y = 0
        self.new_pedestrian((x, y), "up")

        # a pedestrian that starts on the top
        x = int(self.x_max / 2 + 1)
        y = self.y_max - 1
        self.new_pedestrian((x, y), "down")

    def new_road(self):
        '''
        Method that creates the roads.
        '''
        # creates an horizontal road with size 4
        for i in range(int(self.y_max/2 - 2), int(self.y_max/2 + 2)):
            for j in range(self.x_max):
                road = Road(self.next_id(), self, (j,i))
                self.space.place_agent(road, (j,i))

    def new_light(self, pos):
        '''
        Method that creates a new agent, and adds it to the correct scheduler.
        '''
        light = Light(self.next_id(), self, pos, state = 0)

        self.space.place_agent(light, pos)
        getattr(self, 'schedule_light').add(light)

    def new_car(self, pos, dir):
        '''
        Method that creates a new agent, and adds it to the correct scheduler.
        '''
        car = Car(self.next_id(), self, pos, dir)

        self.space.place_agent(car, pos)
        getattr(self, 'schedule').add(car)

    def new_pedestrian(self, pos, dir):
        '''
        Method that creates a new agent, and adds it to the correct scheduler.
        '''
        pedestrian = Pedestrian(self.next_id(), self, pos, dir)

        self.space.place_agent(pedestrian, pos)
        getattr(self, 'schedule').add(pedestrian)

    def remove_agent(self, agent):
        '''
        Method that removes an agent from the grid and the correct scheduler.
        '''

        # do we need the seperate schedulers for this?

        self.space.remove_agent(agent)
        getattr(self, f'schedule').remove(agent)
        # getattr(self, f'schedule_{type(agent).__name__}').remove(agent)


    def step(self):
        '''
        Method that calls the step method for each car.
        '''

        # let existing cars take a step
        self.schedule_light.step()
        self.schedule.step()
        
        for current_agent in self.schedule.agents:
            if current_agent.dir == "up" and current_agent.pos[1] + current_agent.speed >= self.y_max:
                self.remove_agent(current_agent)       
            if current_agent.dir == "right" and current_agent.pos[0] + current_agent.speed >= self.x_max:
                self.remove_agent(current_agent)
            if current_agent.dir == "left" and current_agent.pos[0] + current_agent.speed <= 1:
                self.remove_agent(current_agent)
            if current_agent.dir == "down" and current_agent.pos[1] + current_agent.speed <= 1:
                self.remove_agent(current_agent)    


        # self.schedule_Pedestrian.step()
        # TODO: if there are no more cars in the beginning of the lanes, add cars with a probability


    def run_model(self, step_count=100):
        '''
        Method that runs the model for a specific amount of steps.
        '''
        for i in range(step_count):
            self.step()
