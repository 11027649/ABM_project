from mesa import Agent
from mesa import space
from mesa.space import ContinuousSpace
import random
import math
import numpy as np

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
        self.vision_angle = 170  # Degrees
        self.N_directions = 17 # Should be >= 2!
        self.R_vision_range = 3 # Meters
        self.desired_speed = 1 # Meters per time step
        self.pre_pos = pos
        self.direction = 90
        self.speed_free = 1 #normal distribution of N(1.34, 0.342)
        self.density = None


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
        # Check traffic light and decide to move or not
        if traffic_red() is False:
            # Later: choice if on midsection or on middle of the road

            # Set desired_speed

            # Choose direction
            direction = self.choose_direction()

        # # This is testing the pedestrians in view
        # self.pedestrians_in_field(170,3)

        # Get new position

        # Update previous position
        self.pre_pos = self.pos

        # Move to new position
        raise NotImplementedError
        # Update angle
        self.update_angle()

    def desired_speed(self, gamma=1.913, max_density=5.4):
        #Parameters: Normal speed,
        return self.speed_free * (1 - np.exp(-gamma * ((1/self.density)-(1/max_density))))

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

    #def get_current_view(self, ):

    def update_angle(self):
        """
        Updates the angle to the new direction
        """
        # Find the current heading
        if (self.pos != self.pre_pos):

            # Get heading
            deltapos = self.model.space.get_heading(self.pos, self.pre_pos)
            # If the heading has a non-zero angle
            if (deltapos[0] != 0):
                # Calculate new angle
                cur_angle = math.degrees(math.atan((deltapos[1] / deltapos[0])))
                self.direction = cur_angle
            # If angle is zero, set the direction according to 'up' or 'down'
            else:
                if(self.dir == "up"):
                    self.direction = 90
                elif(self.dir == "down"):
                    self.direction = 270


    def pedestrians_in_field(self, vision_angle, vis_range):
        """
        returns the number of pedestrians in the field
        """
        # Calculate the lower angle and the upper angle
        lower_angle = self.direction - (vision_angle / 2)
        upper_angle = self.direction + (vision_angle / 2)

        # Change the current points to an np array for simplicity
        p0 = np.array(self.pos)

        # Convert to radians for angle calcuation
        u_rads = math.radians(upper_angle)
        l_rads = math.radians(lower_angle)
        # Calculate the end angles
        dx1 = math.cos(l_rads) * vis_range
        dy1 = math.sin(l_rads) * vis_range
        dx2 = math.cos(u_rads) * vis_range
        dy2 = math.sin(u_rads) * vis_range

        # Calculate the points
        p1 = np.array([p0[0] + dx1, p0[1] + dy1])
        p2 = np.array([p0[0] + dx2, p0[1] + dy2])
        # Calculate the vectors
        v1 = p1-p0
        v2 = p2-p1

        # Get the current neighbors
        neighbours = self.model.space.get_neighbors(self.pos, include_center=False, radius=vis_range)
        cone_neigh = []
        # Loop to find if neighbor is within the cone
        for neigh in neighbours:
            v3 = np.array(neigh.pos) - p0
            # Append object to cone_neigh if its within vision cone
            if (np.cross(v1, v3) * np.cross(v1, v2) >= 0 and np.cross(v2, v3) * np.cross(v2, v1) >= 0 and type(neigh) == Pedestrian):
                cone_neigh.append(neigh)

        return cone_neigh

    def pedestrian_intersection(self, conal_neighbours, angle, offset):
        """This fucntion will check the map for intersections from the given angle and the offset
        and return a list of neighbours that match those crieria
        Conal_neighbours: the objects within the vision field
        Angle: the direction k
        Offset: 1.5*radius to both sides of the direction line"""
        # calculate the linear formula for the line
        m = math.tan(radians(angle))
        b = self.pos[1] - (m*self.pos(0))

        # calcuate the y offset of the range of lines
        b_offset = offset/math.cos(angle)

        # calcuate the new intersection points based off the offset of the line
        b_top = b+b_offset
        b_bot = b-b_offset

        neighbours = conal_neighbours
        inter_neighbors = []
        for neigh in neighbours:
            if ((neigh.pos[1] - ((m*neigh.pos[0])+b_top)) <= 0 and (neigh.pos[1] - ((m*neigh.pos[0])+b_bot)) >= 0):
                inter_neighbors.append(neigh)

        return inter_neighbors

    def closest_ped_on_line(self, m, b, neighbours):
        """This would find the closest pedestrian to a path given a subset of pedestrians"""
        min_distance = abs((m*neighbours[0].pos[0])-neighbours[0].pos[1]+b)/math.sqrt((m**2) + 1)
        min_pedestrian = neighbours[0]
        for i in range(1, len(inter_neigh)):
            cur_distance = abs((m * neighbours[i].pos[0]) - neighbours[i].pos[1] + b) / math.sqrt((m ** 2) + 1)
            #if math.sqrt((self.pos[0]-inter_neigh[i].pos[0])**2+(self.pos[1]-inter_neigh[i].pos[1])**2) < min_distance:
            if cur_distance < min_distance:
                min_pedestrian = neighbours[i]
                min_distance = cur_distance
            elif cur_distance == min_distance:
                if self.model.space.get_distance(self.pos, min_pedestrian.pos) > self.model.space.get_distance(self.pos, neighbours.pos):
                    min_pedestrian = neighbours[i]
                    min_distance = cur_distance

        return min_distance, min_pedestrian

    def closest_pedestrian(self, inter_neigh):
        """This is used to find the closest pedestrian of a given included list of neighbours"""
        min_distance = self.model.space.get_distance(self.pos, inter_neigh[0].pos)
        #min_distance = math.sqrt((self.pos[0]-inter_neigh[0].pos[0])**2+(self.pos[1]-inter_neigh[0].pos[1])**2)
        min_pedestrian = inter_neigh[0]
        for i in range(1, len(inter_neigh)):
            #if math.sqrt((self.pos[0]-inter_neigh[i].pos[0])**2+(self.pos[1]-inter_neigh[i].pos[1])**2) < min_distance:
            cur_distance = self.model.space.get_distance(self.pos, inter_neigh[i].pos)
            if cur_distance < min_distance:
                min_pedestrian = inter_neigh[i]
                min_distance = cur_distance

        return min_distance, min_pedestrian


    def traffic_red(self):
        """
        Returns true if light is red
        """
        # Check if agent is in front of the traffic light (correct_side=True)
        # TODO: Add light for midsection (and add midsection)
        correct_side = False
        if self.dir == "up":
            own_light = 2
            if self.pos[1] > int(self.model.space.y_max/2 + 2 ):
                correct_side = True
        else:
            own_light = 3
            if self.pos[1] < int(self.model.space.y_max/2 - 2):
                correct_side = True

        # Iterate over all the agents
        for i in self.model.space.get_neighbors(self.pos, include_center = False, radius = 4):
            # If the agent is a light, which is red or orange, which is your own light and you're in front of the light
            if (isinstance(i,Light) and (i.state < 50 or i.state > 100) and i.light_id == own_light and correct_side == True):
                return True

        return False

        # # If an agent is in front, set speed to 0
        # self.speed = 1
        # if self.check_front() > 0:
        #     self.speed = 0
        # # else, check if their light is orange or red
        # else:
        #     # Iterate over all agents in the neighbourhood
        #     for i in self.model.space.get_neighbors(self.pos, include_center = False, radius = 2):
        #         # If the agent is a light, which is red or orange, which is your own light and you're in front of the light
        #         if (isinstance(i,Light) and (i.state < 50 or i.state > 100) and i.light_id == own_light and correct_side == True):
        #             # Stop moving
        #             self.speed = 0
        #             break


    def step(self):
        '''
        This method should move the Sheep using the `random_move()` method implemented earlier, then conditionally reproduce.
        '''

        # check if there's a traffic light (and adjust speed accordingly)
        changed = 0
        correct_side = False
        if self.dir == "up":
            own_light = 6
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
            self.pre_pos = self.pos
            self.model.space.move_agent(self, next_pos)
        else:
            next_pos = (self.pos[0], self.pos[1] + self.speed)
            self.pre_pos = self.pos
            self.model.space.move_agent(self, next_pos)

        # TODO has to be moved to new step function
        self.time += 1

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
            own_light = 2
            if self.pos[0] > int(self.model.space.x_max/2 + 2):
                correct_side = True

        # very inefficient code right here if we notice if the run time is too long

        for i in self.model.space.get_neighbors(self.pos, include_center = False, radius = 4):
        # not only affected by 1 light
            if changed == 0 and (self.check_front() > 0 or (isinstance(i,Light) and (i.state < 50 or i.state > 100) and i.light_id == own_light and correct_side == True)):
                self.speed = 0
                break

            elif (changed == 0 and self.check_front() == 0) or (changed == 0 and self.check_front() == 0 and correct_side == False):
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
