from mesa import Agent
from mesa import space
from mesa.space import ContinuousSpace
import random
import math
import numpy as np

class Light(Agent):
    def __init__(self, unique_id, model, pos, state, light, color):
        super().__init__(unique_id, model)

        self.pos = pos
        self.state = state
        self.color = color #Where color is Red or Green
        self.type = light #where light is either Ped or Traf

    def step(self):
        '''
        Update the state of the light.
        '''
        self.state = (self.state + 1) % 500

        if self.model.strategy == "Simultaneous":
            self.simultaneous_step()
        elif self.model.strategy == "Free":
            self.free()

        if self.unique_id == 1 or self.unique_id == 2:
            self.closest_car()

    def simultaneous(self):
        if self.state <= 300:
            self.color = "Red"
        elif self.state <= 450:
            self.color = "Green"
        else:
            self.color = "Orange"

    def simultaneous_step(self):
        """Not sure if this will be needed"""
        if self.closest_car()<30:
            self.model.sense_car = True
        if self.color == "Red" and self.type == "Ped" and self.model.ped_light:
            self.color = "Green"
        elif self.color == "Red" and self.type == "Traf" and self.model.car_light:
            self.color = "Green"
        if self.type == "Car":
            self.simultaneous_car()
        elif self.type == "Ped":
            self.simultaneous_ped()


    def simultaneous_car(self):
        """The light profile for the car lights"""
        if self.color == "Green":
            self.state += 1
            if self.state == 40:
                self.color = "Orange"
        elif self.color == "Orange":
            self.state += 1
            # Placehodler ToDo Figure out when it should tip over
            if self.state == 60:
                self.color = "Red"
                self.state = 0
                self.model.car_light = False
                self.model.ped_light = True

    def simultaneous_ped(self):
        """The light profile for the pedestrian lights"""
        if self.color == "Green":
            self.state += 1
            if self.state >= 15 and self.model.sense_car:
                self.color = "Orange"
        elif self.color == "Orange":
            self.state += 1
            # Placehodler ToDo Figure out when it should tip over
            if self.state == 20:
                self.color = "Red"
                self.state = 0
                self.model.ped_light = False
                self.model.cer_light = True


    def check_lights(self):
        """Update the bolleans for the lights"""



    def free(self):
        self.color = "Green"

    def closest_car(self):

        center = 2.5
        if self.unique_id == 1:
            direction = -1
        elif self.unique_id == 2:
            direction = 1
        # checks for neighbors 10 times with a radius of 2.6 in steps of 5 (sees entire road)
        for i in range(10):
            neighbours = self.model.space.get_neighbors((self.pos[0] + (center + i * (2.5 * 2)) * direction, 16.5 - 3 * direction), include_center = True, radius = 2.6)

            if len(neighbours) > 0:
                min_distance = math.inf
                for neigh in neighbours:
                    cur_distance = abs(self.pos[0] - neigh.pos[0])
                    if cur_distance < min_distance:
                        min_distance = cur_distance
                return min_distance

            
# simultaneous strategy
# 3 & 4 are the same
# 5 & 6 are the same
