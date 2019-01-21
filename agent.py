from mesa import Agent
from mesa import space
from mesa.space import ContinuousSpace
import random
import math
import numpy as np

from light import Light

class Pedestrian(Agent):
    def __init__(self, unique_id, model, pos, dir, speed = 1, time=0):
        super().__init__(unique_id, model)
        self.pos = pos
        self.dir = dir
        self.speed = speed
        self.time = time

        # Liu, 2014 parameters
        self.vision_angle = 170  # Degrees
        self.walls_x = [20, 30] # TODO: correct walls?

        # parameters TODO: optimization?
        self.N = 16 # Should be >= 2!
        self.R_vision_range = 3 # Meters
        self.des_speed = 1 # Meters per time step
        # Weights (for equation 1)
        # What is We' for equation 7??
        self.Ek_w = 1
        self.Ok_w = 1
        self.Pk_w = 1
        self.Ak_w = 1
        self.Ik_w = 1
        # TODO: assign target point randomly (preference to right side?)
        self.target_point = (10,0)
        self.speed_free = random.gauss(.134, .0342) # normal distribution of N(1.34, 0.342) m/s, but per (1/10s) timesteps

        # Set direction in degrees
        if self.dir == "up":
            self.direction = 270
        elif self.dir == "down":
            self.direction = 90
        else:
            raise ValueError("invalid direction, choose 'up' or 'down'")


    def step_new(self):
        """
        stepfunction based on Liu, 2014
        """
        # Check traffic light and decide to move or not
        # Returns True if light is red
        # Move if not red (TODO: decide what to do with orange)
        if self.traffic_red() is False:
            # TODO: decide what their choice is if on midsection or on middle of the road. Move to the spot where there is space?

            # Get list of pedestrians in the vision field
            peds_in_vision = self.pedestrians_in_field(self.vision_angle, self.R_vision_range)
            # Set desired_speed
            self.des_speed = self.desired_speed(len(peds_in_vision))

            # TODO: delete printstatements at some point :p
            # print(self.dir, self.pos, self.direction)
            # Get new position and update direction
            next_pos, self.direction = self.choose_direction()
            # print(self.dir, self.pos, next_pos, self.direction)
            # print()

            # # TODO: de-comment this if we're running this step function
            # # Move to new position
            # self.model.space.move_agent(self, next_pos)
            # # Finalize this step
            # self.time += 1


    def desired_speed(self, n_agents_in_cone, gamma=1.913, max_density=5.4):
        """
        Returns desired speed, using equation 8
        Takes as input the number of agents in vision field
        """
        # TODO: Only works for vision angle of 170 degrees, is that okay?
        if self.vision_angle == 170:
            # cone_area_170 = 13.3517
            # agent_area: pi*(0.4**2) = 0.5027
            # dens = agent_area/cone_area
            dens = 0.0376
        else:
            raise ValueError('Code only works for 170 degrees vision range for now')

        # Errorcheck for division by zero
        if n_agents_in_cone <= 0:
            return self.speed_free

        # Calculate cone density
        cone_density = n_agents_in_cone * dens
        # Calculate the desired speed (see eq. 8)
        des_speed = self.speed_free*(1 - np.exp(-gamma*((1/cone_density)-(1/max_density))))

        # Check if speed is not negative
        if des_speed >= 0:
            return des_speed
        else:
            return 0


    def choose_direction(self):
        """
        Picks the direction with the highest utility
        """

        # For getting the neighbours in the front 180 degrees within vision range; for calc_utility
        peds_in_180 = self.pedestrians_in_field(180, self.R_vision_range)

        # Loop over the possible directions
        # TODO: Is it okay for the utility to return a negative value? Should we check for that? (Now weights are just set at 1)
        max_util = [-10**6, None, None]
        pos_directions = self.possible_directions()  
        for direction in pos_directions:
            # Calculate utility
            util, next_pos = self.calc_utility(direction, peds_in_180)
            # Check if this utility is higher than the previous
            if util > max_util[0]:
                max_util = [util, next_pos, direction]

        # Return next position and the direction
        return max_util[1], max_util[2]


    def possible_directions(self):
        """
        Returns the possible directions for theta and N.
        Includes outer directions of the vision range
        """

        # Calculate the lower angle and the upper angle
        lower_angle = self.direction - (self.vision_angle / 2)

        # Get list of possible directions
        theta_N = self.vision_angle/(self.N)
        pos_directions = []
        for i in range(self.N+1):
            pos_directions.append(lower_angle+i*theta_N)

        return pos_directions


    def calc_utility(self, direction, peds_in_180):
        """
        Calculate the utility (equation 1 for now. Whats omega_e' in eq. 7?)
        """

        # List of pedestrians in that direction
        peds_in_dir = self.pedestrian_intersection(peds_in_180, direction, .7)

        # Get closest pedestrian in this directions
        if len(peds_in_dir) > 0:
            # Get closest pedestrian: min_distance, min_pedestrian.pos
            # TODO: returning the pedestrian.pos not necessary? (then also update code for this)
            closest_ped = self.closest_pedestrian(peds_in_dir)[0]
        # If no pedestrians in view, closest_ped distance is set at vision range
        else:
            closest_ped = self.R_vision_range
        
        # Distance to road 'wall'
        # TODO: IMPLEMENT: Check if wall is within vision range and get the distance to it and coordinates
        # If no pedestrians in view, closest_ped is set at vision range
        closest_wall = self.R_vision_range

        # Determine possible new position
        chosen_velocity = min(self.des_speed, closest_ped, closest_wall)
        next_pos = self.new_pos(chosen_velocity, direction)

        # Calculate distance from possible next_pos to target point
        # TODO: CHANGE TO DISTANCE TO PROJECTION TARGET POINT
        target_dist = self.model.space.get_distance(next_pos, self.target_point)

        # Calculate factors
        Ek = 1 - (target_dist - self.R_vision_range - self.speed_free)/(2*self.speed_free) # Efficiency of approaching target point
        Ok =  min(self.R_vision_range, closest_wall)/self.R_vision_range # distance to closest obstacle/vision range
        Pk =  min(self.R_vision_range, closest_ped)/self.R_vision_range # distance to closest person/vision range
        # Theta_vj is the angle between directions of this pedestrian and the pedestrian closest to the trajectory
        # # TODO: Use for the trajectory the line between current postion and possible next_pos? Or R_vision_range?
        # # TODO: in radians or degrees?
        theta_vj = 0
        Ak = 1 - theta_vj/math.pi # flocking
        Ik = abs(self.direction-direction) / (self.vision_angle/2) # Difference in angle of current and possible directions

        # # Using equation 1 for now:
        # TODO: Do we want to change to equation 7? I don't quite understand 7..
        # TODO: can utility become <0? Should we check? (also dependent on weights; optimization?)
        return self.Ek_w * Ek + self.Ok_w * Ok + \
                self.Pk_w * Pk + self.Ak_w * Ak + \
                self.Ik_w * Ik, next_pos


    def within_wall(self, direction):
        """
        Returns True if 
        """
        max_x_pos = self.pos[0] + self.R_vision_range*np.cos(math.radians(direction))
        if max_x_pos < self.walls_x[0] or max_x_pos > self.walls_x[1]:
            return False
        else:
            return True

    def new_pos(self, chosen_velocity, theta_chosen):
        """
        Returns new position using self.pos, the velocity and angle
        """
        return (self.pos[0] + chosen_velocity*np.cos(math.radians(theta_chosen)), self.pos[1]+chosen_velocity*np.sin(math.radians(theta_chosen)))


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
        # math.radians(180*3.5)%(2*math.pi) (TODO: useful or no?)
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
        Offset: 1.5*radius_of_pedestrian to both sides of the direction line
        """

        # Checks if the agent is looking straight up or down
        neighbours = conal_neighbours
        inter_neighbors = []

        if (angle == 270 or angle == 90):
            for neigh in neighbours:
                if (neigh.pos[0] > self.pos[0] - offset and neigh.pos[0] < self.pos[0] + offset):
                    inter_neighbors.append(neigh)

        # Checks if the agent is looking left uor right
        elif (angle == 0 or angle == 180):
            for neigh in neighbours:
                if (neigh.pos[1] > self.pos[1] - offset and neigh.pos[1] < self.pos[1] + offset):
                    inter_neighbors.append(neigh)

                    # The agent is looking at an different non-exeption angle
        else:
            # calculate the linear formula for the line
            m = math.tan(math.radians(angle))
            b = self.pos[1] - (m * self.pos[0])

            # calcuate the y offset of the range of lines
            b_offset = offset / math.cos(angle)

            # calcuate the new intersection points based off the offset of the line
            b_top = b + b_offset
            b_bot = b - b_offset

            for neigh in neighbours:
                if ((neigh.pos[1] - ((m * neigh.pos[0]) + b_top)) <= 0 and (
                        neigh.pos[1] - ((m * neigh.pos[0]) + b_bot)) >= 0):
                    inter_neighbors.append(neigh)

        # Prints the position, dir and direction of the current agent and the positions of the agents it sees
        # print('ped_intersect', self.pos, self.dir, self.direction, 'sees:', [neigh.pos for neigh in inter_neighbors])

        return inter_neighbors

    def closest_ped_on_line(self, m, b, neighbours):
        """
        This would find the closest pedestrian to a path given a subset of pedestrians
        TODO: CHECK CODE FOR DIFFERENT SITUATIONS
        """
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
        """
        This is used to find the closest pedestrian of a given included list of neighbours
        TODO: CHECK CODE FOR DIFFERENT SITUATIONS
        Returns distance to and the position of the closest pedestrian
        """
        min_distance = self.model.space.get_distance(self.pos, inter_neigh[0].pos)
        #min_distance = math.sqrt((self.pos[0]-inter_neigh[0].pos[0])**2+(self.pos[1]-inter_neigh[0].pos[1])**2)
        min_pedestrian = inter_neigh[0]
        for i in range(1, len(inter_neigh)):
            #if math.sqrt((self.pos[0]-inter_neigh[i].pos[0])**2+(self.pos[1]-inter_neigh[i].pos[1])**2) < min_distance:
            cur_distance = self.model.space.get_distance(self.pos, inter_neigh[i].pos)
            if cur_distance < min_distance:
                min_pedestrian = inter_neigh[i]
                min_distance = cur_distance

        return min_distance, min_pedestrian.pos


    def traffic_red(self):
        """
        Returns true if light is red
        """
        # Check if agent is in front of the traffic light (correct_side=True)
        # TODO: Add light checking for midsection (and add midsection)
        correct_side = False
        if self.dir == "up":
            own_light = 2
            if self.pos[1] > int(self.model.space.y_max/2 + 2):
                correct_side = True
        else:
            own_light = 6
            if self.pos[1] < int(self.model.space.y_max/2 - 2):
                correct_side = True

        # Iterate over all the agents
        for i in self.model.space.get_neighbors(self.pos, include_center = False, radius = 4):
            # If the agent is a light, which is red or orange, which is your own light and you're in front of the light
            if (isinstance(i,Light) and (i.state < 50 or i.state > 100) and i.light_id == own_light and correct_side == True):
                return True

        return False


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
            self.model.space.move_agent(self, next_pos)
        else:
            next_pos = (self.pos[0], self.pos[1] + self.speed)
            self.model.space.move_agent(self, next_pos)

        self.time += 1
        # DELETE
        self.step_new()

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
