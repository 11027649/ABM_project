from mesa import Agent
from mesa.space import ContinuousSpace
import random


class Road(Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)

        self.pos = pos

class Light(Agent):
    def __init__(self, unique_id, model, pos, state, light_id):
        super().__init__(unique_id, model)

        self.pos = pos
        self.state = state
        self.light_id = light_id

    def step(self):
        '''
        This method should move the goat using the `random_move()` method implemented earlier, then conditionally reproduce.
        '''
        self.state = (self.state + 1) % 130




class Pedestrian(Agent):
    def __init__(self, unique_id, model, pos, dir, speed = 1, time=0):
        super().__init__(unique_id, model)
        self.pos = pos
        self.dir = dir
        self.speed = speed
        self.time = time

        # Liu, 2014 parameters
        self.theta_field = 170  # Degrees
        self.N_directions = 17
        self.R_vision_range = 3 # Meters
        self.desired_speed = 1 # Meters per time step
        self.pre_pos = pos

        # Weights (for equation 1)
        # What is We' for equation 7??
        self.Ek_w = 1
        self.Ok_w = 1
        self.Pk_w = 1
        self.Ak_w = 1
        self.Ik_w = 1

    def step_new(self):
        """
        stepfunction based on Liu, 2014
        """
        # Check traffic light and decide to more or not

        # Later: choice if on midsection or on middle of the road

        # If not on midsection:
        # Choose direction
        direction = self.choose_direction()    
        # Get new position   

        # Update previous position
        self.pre_pos = self.pos
        # Move to new position
        raise NotImplementedError

    def choose_direction(self):
        """
        Picks the direction with the highest utility
        """
        # Get list of nearest objects/pedestrians per direction
        obj_per_k = objects_per_direction(self)        
        # Loop over directions and calculate the highest utility
        # Save highest utility and that direction

        # Return direction with highest utility
        raise NotImplementedError

    def calc_utility(self, closest_obj):
        """
        Calculate the utility (equation 7? Whats omega_e'?)
        """
        # Calculate distance to target point
        # or ContinuousSpace
        distance_to_obj = self.Space.get_distance(self.pos, closest_obj.pos)
        Dk_target = min(self.desired_speed, distance_to_obj)
        # Calculate distance pedestrian can move
        Rk_step = None

        # Calculate factors
        Ek = 1 - (Dk_target - self.R_vision_range - Rk_step)/(2*Rk_step)
        Ok = None
        Pk = None
        Ak = None
        Ik = None

        raise NotImplementedError

        # Using equation 1 for now:
        return self.Ek_w * Ek + self.Ok_w * Ok + \
                self.Pk_w * Pk + self.Ak_w * Ak + \
                self.Ik_w * Ik


    def objects_per_direction(self):
        """
        returns a list of a list of nearest objects
        and a list of nearest pedestrians
        """
        raise NotImplementedError

    def pedestrians_in_field(self):
        """
        returns the number of pedestrians in the field
        --Jordan
        """
        raise NotImplementedError

    def step(self):
        '''
        This method should move the Sheep using the `random_move()` method implemented earlier, then conditionally reproduce.
        '''

        # check if there's a traffic light (and adjust speed accordingly)
        changed = 0
        correct_side = False
        if self.dir == "up":
            own_light = 2
            if self.pos[1] > int(self.model.space.y_max/2 + 2 ):
                correct_side = True
        else:
            own_light = 3
            if self.pos[1] < int(self.model.space.y_max/2 - 2):
                correct_side = True

        # very inefficient code right here if we notice if the run time is too long

        for i in self.model.space.get_neighbors(self.pos, include_center = False, radius = 2):
            if self.check_front() > 0 or (isinstance(i,Light) and (i.state < 50 or i.state > 100) and i.light_id == own_light and correct_side == True):
                self.speed = 0
                changed = 1
            elif (changed == 0 and self.check_front() == 0) or (changed == 0 and self.check_front() == 0 and correct_side == False):
                self.speed = 1

        # take a step
        if self.dir is "up":
            next_pos = (self.pos[0], self.pos[1] - self.speed)
            self.model.space.move_agent(self, next_pos)
        else:
            next_pos = (self.pos[0], self.pos[1] + self.speed)
            self.model.space.move_agent(self, next_pos)

    # this function is in both pedestrian and agent -> more efficient way?
    def check_front(self):
        '''
        Function to see if there is a Pedestrian closeby in front
        '''

        if self.dir == "up":
            direction = -1
        else:
            direction = 1

        # the Pedestrian has a vision range of 1 tile for now (can be changed to its max speed?)
        for i in range(1, 2):
            for agent in self.model.space.get_neighbors((self.pos[0], self.pos[1] + direction * i), radius = 0):
                if isinstance(agent, Car) or isinstance(agent, Pedestrian):
                    return i
        return 0


class Car(Agent):
    def __init__(self, unique_id, model, pos, dir, speed=1, time=0):
        super().__init__(unique_id, model)

        self.pos = pos
        self.dir = dir
        self.speed = speed
        self.time = time

    def step(self):
        '''
        Cars go straight for now.
        '''
        changed = 0
        correct_side = False
        if self.dir == "right":
            own_light = 1
            if self.pos[0] < int(self.model.space.x_max/2 - 2):
                correct_side = True
        else:
            own_light = 4
            if self.pos[0] > int(self.model.space.x_max/2 + 2):
                correct_side = True

        # very inefficient code right here if we notice if the run time is too long

        for i in self.model.space.get_neighbors(self.pos, include_center = False, radius = 2):
        # not only affected by 1 light
            if self.check_front() > 0 or (isinstance(i,Light) and (i.state < 50 or i.state > 100) and i.light_id == own_light and correct_side == True):
                # if self.speed > 0:
                self.speed = 0
                changed = 1
            elif (changed == 0 and self.check_front() == 0) or (changed == 0 and self.check_front() == 0 and correct_side == False):
                # if self.speed < 1:
                self.speed = 1


        # take a step
        if self.dir is "left":
            next_pos = (self.pos[0] - self.speed, self.pos[1])
            self.model.space.move_agent(self, next_pos)
        else:
            next_pos = (self.pos[0] + self.speed, self.pos[1])
            self.model.space.move_agent(self, next_pos)

        self.time += 1


    def check_front(self):
        '''
        Function to see if there is a car closeby in front of a car
        '''

        if self.dir == "right":
            direction = 1
        else:
            direction = -1

        # the car has a vision range of 1 tile for now (can be changed to its max speed?)
        for i in range(1, 2):
            for agent in self.model.space.get_neighbors((self.pos[0] + direction * i, self.pos[1]), radius = 0):
                if isinstance(agent, Car) or isinstance(agent, Pedestrian):
                    return i
        return 0
