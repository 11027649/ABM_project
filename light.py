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
        self.color = color # where color is Red, Green or Orange
        self.type = light # where light is either Ped or Traf#
        self.ped_light = True
        self.car_light = False
        self.closest = math.inf

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
            self.closest = self.closest_car()

    def simultaneous(self):
        if self.state <= 300:
            self.color = "Red"
        elif self.state <= 450:
            self.color = "Green"
        else:
            self.color = "Orange"

    def simultaneous_step(self):
        """Simultaneaous step function updated"""
        #checks which type of light it is
        if self.type == "Traf":
            #checks to see if its red and needs to change
            if self.color == "Red" and (self.car_light):
                self.color = "Green"
            self.simultaneous_car()
        elif self.type == "Ped":
            #checks if its red and needs to change
            if self.color == "Red" and (self.ped_light):
                self.color = "Green"
            self.simultaneous_ped()

    def staggered_step(self):
        """Updates for staggered step functions"""
        """Simultaneaous step function updated"""
        #checks which type of light it is
        if self.type == "Traf":
            #checks to see if its red and needs to change
            if self.color == "Red" and (self.car_light):
                self.color = "Green"
            self.simultaneous_car()
        elif self.type == "Ped":
            #checks if its red and needs to change
            if self.color == "Red" and (self.ped_light):
                self.color = "Green"
            self.simultaneous_ped()



    def simultaneous_car(self):
        """The light profile for the car lights"""
        #Changes the lights color based on the number of steps
        if self.color == "Green":
            self.state += 1
            if self.state >= 40:
                self.color = "Orange"
                self.state = 0
        elif self.color == "Orange":
            self.state += 1
            # Placehodler ToDo Figure out when it should tip over
            if self.state >= 20:
                self.color = "Red"
                self.state = 0
                for light in self.model.lights:
                    light.car_light = False
                    light.ped_light = True

    def simultaneous_ped(self):
        """The light profile for the pedestrian lights"""
        # Changes the lights color based on the number of steps
        if self.color == "Green":
            self.state += 1
            if self.state >= 20 and (self.model.lights[0].closest_car()<=7 or self.model.lights[1].closest_car()<=7):
                self.color = "Orange"
                self.state = 0
        elif self.color == "Orange":
            self.state += 1
            # Placehodler ToDo Figure out when it should tip over
            if self.state >= 10:
                self.color = "Red"
                self.state = 0
                for light in self.model.lights:
                    light.ped_light = False
                    light.car_light = True

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
