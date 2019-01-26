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

        # Radius
        self.radius = .2

        self.remove = False

        # Liu, 2014 parameters
        self.vision_angle = 170  # Degrees
        self.walls_x = [23*2, 27*2] # TODO: correct walls?

        # parameters
        self.N = 16 # Should be >= 2!
        self.R_vision_range = 3 # Meters
        self.des_speed = None # Meters per time step
        # Weights (for equation 1)
        # What is We' for equation 7??
        self.Ek_w = 1
        self.Ok_w = .4
        self.Pk_w = .6
        self.Ak_w = .3
        self.Ik_w = .1

        self.Ok_w_7 = .4
        self.Pk_w_7 = .6
        self.Ak_w_7 = .3
        self.Ik_w_7 = .1
        self.speed_free = random.gauss(.134, .0342) # normal distribution of N(1.34, 0.342) m/s, but per (1/10s) timesteps

        # Set direction in degrees
        # TODO: assign target point with preference to right side?
        if self.dir == "up":
            self.direction = 270
            self.target_point = (random.uniform(24*2,26*2), 0)
            self.own_light1 = (45.54, 22.4)
            self.own_light2 = (45.54, 16.8)
        elif self.dir == "down":
            self.direction = 90
            self.target_point = (random.uniform(24*2,26*2), 50)
            self.own_light1 = (53.46, 10.6)
            self.own_light2 = (53.46, 16.2)
        else:
            raise ValueError("invalid direction, choose 'up' or 'down'")

        # Check if walls are far enough for dist_walls function
        if abs(self.walls_x[0]-self.walls_x[1])<2*self.R_vision_range:
            raise ValueError("Walls are too close together for the dist_walls function to work correctly")

    def on_road_side(self):
        if self.dir == "up":
            # check where the pedestrian is and assign it to the right traffic light
            if self.pos[1] > 22.2 and self.pos[1] < 22.6:
                return True
            elif self.pos[1] < 16.4 and self.pos[1] > 16:
                return True
        elif self.dir == "down":
            if self.pos[1] < 10.8 and self.pos[1] > 10.4:
                return True
            elif self.pos[1] < 17 and self.pos[1] > 16.6:
                return True
        else:
            return False

    def step(self):
        """
        stepfunction based on Liu, 2014
        """
        # Check traffic light and decide to move or not
        # Returns True if light is red
        # Move if not red (TODO: decide what to do with orange)
        if self.traffic_green() or not self.on_road_side():
            # TODO: decide what their choice is if on midsection or on middle of the road. Move to the spot where there is space?

            # Get list of pedestrians in the vision field
            peds_in_vision = self.pedestrians_in_field(self.vision_angle)

            # Set desired_speed
            self.des_speed = self.desired_speed(len(peds_in_vision))

            # Get new position and update direction
            next_pos, self.direction = self.choose_direction()

            # Try to move agent
            try:
                self.model.space.move_agent(self, next_pos)
            except:
                # If it gave an exeption and it is trying to go in the wrong direction
                if ((self.dir == "up" and self.direction%360 <180) or
                    (self.dir == "down" and self.direction%360 >180)):
                    # Let it be removed by the step function in model.py
                    self.remove = True

            # Finalize this step
            self.time += 1


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
        peds_in_180 = self.pedestrians_in_field(180)

        # Loop over the possible directions
        max_util = [-10**6, None, None]
        pos_directions = self.possible_directions()

        for direction in pos_directions: #TODO I think this is where something may be going wrong
            # Calculate utility for every possible direction
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
        theta_N = self.vision_angle/(self.N-1)
        pos_directions = []
        for i in range(self.N):
            pos_directions.append(lower_angle+i*theta_N)

        return pos_directions


    def calc_utility(self, direction, peds_in_180):
        """
        Calculate the utility for one out of possible directions.
        """

        # List of pedestrians in that direction
        peds_in_dir = self.pedestrian_intersection(peds_in_180, direction, .7)

        # Get closest pedestrian in this directions
        if len(peds_in_dir) > 0:
            # Get closest pedestrian: min_distance, min_pedestrian.pos
            # TODO: check if negative
            # TODO: WHY DOES THIS NOT WORK? DDDDDD:::::

            # print('peds', peds_in_dir)
            closest_ped = self.closest_pedestrian(peds_in_dir, direction) - 2*self.radius
            # If no pedestrians in view, closest_ped distance is set at vision range
        else:
            closest_ped = self.R_vision_range-self.radius

        # Distance to road 'wall', if no pedestrians in view, closest_ped is set at vision range
        closest_wall = self.dist_wall(direction)-self.radius

        # Determine possible new position
        chosen_velocity = min(self.des_speed, closest_ped, closest_wall)
        next_pos = self.new_pos(chosen_velocity, direction)


        #Finds the pedestrians in the next step length
        if len(peds_in_180)>0:
            cpil = self.closest_ped_on_line(peds_in_180, direction)[1]
            theta_vj = self.theta_calc(cpil,direction)
        else:
            theta_vj = 0


        # If the target point is not within vision:
        if self.model.space.get_distance(self.pos, self.target_point) > self.R_vision_range:
            # Calculate distance from possible next_pos to target point projection on vision field
            target_proj = self.target_projection()
            target_dist = self.model.space.get_distance(next_pos, target_proj)
        # If Target point is within the vision field, calculate the distance to the real target point
        else:
            target_dist = self.model.space.get_distance(next_pos, self.target_point)

        # Calculate factors
        Ek = 1 - (target_dist - self.R_vision_range - self.speed_free)/(2*self.speed_free) # Efficiency of approaching target point
        Ok =  closest_wall/self.R_vision_range # distance to closest obstacle/vision range
        Pk =  closest_ped/self.R_vision_range # distance to closest person/vision range
        # Theta_vj is the angle between directions of this pedestrian and the pedestrian closest to the trajectory

        Ak = 1 - math.radians(theta_vj)/math.pi  # flocking, kinda if it was true flocking then it would have more agents being examined, we can look at this later.
        Ik = abs(self.direction-direction) / (self.vision_angle/2) # Difference in angle of current and possible directions


        return self.Ek_w * Ek + self.Ok_w * Ok + \
                self.Pk_w * Pk + self.Ak_w * Ak + \
                self.Ik_w * Ik, next_pos

    def traject_angle(self, direction, peds_in_180, next_pos):
        """
        Returns the traject angle
        """
        # Get the visible neighbours (180)
        # Get the end of the trajectory from the next_position
        # Get the closest neighbour in this trajectory from this pedestrian to the next position of this pedestrian
        # Should return False if there is no neighbour in view
        closest_neigh = self.closest_ped_on_line(peds_in_180, direction)[1]
        if closest_neigh is False:
            return 0
        else:
            # Return the angle of the closest neighbours direction and the current pedestrians direction
            return abs(closest_neigh.direction - direction)

    def theta_calc(self, ped, angle):
        """returns the angle given the pedestrians location and the directions"""
        m = math.tan(math.radians(angle))
        b = self.pos[1] - (m * self.pos[0])

        if ped.pos[1] - (m*ped.pos[0])+b < 0 and ped.direction>angle and ped.direction < angle+math.radians(180):
            return abs(angle - ped.direction)
        elif ped.pos[1] - (m*ped.pos[0])+b > 0 and (ped.direction<angle or ped.direction > angle+math.radians(180)):
            return abs(angle - ped.direction)
        else:
            return 0

    def target_projection(self):
        """
        Returns coordinates of the targets projection on the vision range
        """
        # Distance in x and y coordinates to the target
        dist_diff = [self.target_point[0]-self.pos[0], self.target_point[1]-self.pos[1]]
        # Distance to target
        dist = math.sqrt(dist_diff[0]**2 + dist_diff[1]**2)
        # Ratio of distance and projection
        ratio = self.R_vision_range/dist

        # Return position+distance to coordinates of the projection
        return (self.pos[0]+ratio*dist_diff[0], self.pos[1]+ratio*dist_diff[1])


    def dist_wall(self, direction):
        """
        Returns True if
        """
        # Calculate furthest point the pedestrian can see
        max_x_pos = self.pos[0] + self.R_vision_range*np.cos(math.radians(direction))
        # If the maximum x position is outside of the walls, return distance
        if max_x_pos < self.walls_x[0]:
            return (self.walls_x[0]-self.pos[0])/np.cos(math.radians(direction))
        elif max_x_pos > self.walls_x[1]:
            return (self.walls_x[1]-self.pos[0])/np.cos(math.radians(direction))
        # Else, return the vision range
        else:
            return self.R_vision_range


    def new_pos(self, chosen_velocity, theta_chosen):
        """
        Returns new position using self.pos, the velocity and angle
        """
        return (self.pos[0] + chosen_velocity*np.cos(math.radians(theta_chosen)), self.pos[1]+chosen_velocity*np.sin(math.radians(theta_chosen)))


    def pedestrians_in_field(self, vision_angle):
        """
            Returns the pedestrians that are in the cone that the pedestrian can
            actually see in a certain vision_angle (which usually is 170, but
            can also be a bit heigher to check the most outer parts.).
        """

        # get all surrounding neighbors
        neighbors = self.model.space.get_neighbors(self.pos, include_center=False, radius=self.R_vision_range)

        rotatedNeighList = []
        i = -1
        # rotate all the neigbours facing either up or down
        for neigh in neighbors:

            i = i + 1

            if isinstance(neigh, Pedestrian):
                rotatedNeighList.append(self.rotate(self.pos, neigh.pos, i))

        cone_neigh = []

        # calculate if the pedestrians are within the 'viewing triangle'
        for rotatedNeigh in rotatedNeighList:
            if self.dir == "down":
                if rotatedNeigh[1] - self.pos[1] > math.tan(math.radians(90 - (vision_angle / 2))) * abs(rotatedNeigh[0] - self.pos[0]):
                    cone_neigh.append(neighbors[rotatedNeigh[2]])

            else:
                if rotatedNeigh[1] - self.pos[1] < -math.tan(math.radians(90 - (vision_angle / 2))) * abs(rotatedNeigh[0] - self.pos[0]):
                    cone_neigh.append(neighbors[rotatedNeigh[2]])

        return cone_neigh


    def pedestrian_intersection(self, conal_neighbours, angle, offset):
        """
        Input: conal_neighbours, the neighbours that the pedestrian can see.
        The function will check for intersections on the given angle. For this we
        need an offset, because the pedestrians have a radius. The function
        returns a list of intersecting neighbours.
        Angle: the direction k that we're calculating utility for.
        Offset: 1.5*radius_of_pedestrian to both sides of the direction line: 0.3.
        """

        intersecting = []

        # checks if the agent is looking straight up or down
        if (angle == 270 or angle == 90):
            for neigh in conal_neighbours:
                if neigh.pos[0] >= (self.pos[0] - offset) and neigh.pos[0] <= (self.pos[0] + offset):
                    intersecting.append(neigh)

        # checks if the agent is looking left or right
        elif (angle == 0 or angle == 180):
            for neigh in conal_neighbours:
                if neigh.pos[1] >= (self.pos[1] - offset) and neigh.pos[1] <= (self.pos[1] + offset):
                    intersecting.append(neigh)

        else:
            # calculate the linear formula for the line
            slope = math.tan(math.radians(angle))
            b = self.pos[1] + (slope * self.pos[0])

            # calcuate the y offset of the range of lines
            ##### HELP (is this correct?)
            b_offset = offset / math.cos(math.radians(angle))

            # calcuate the new intersection points based off the offset of the line
            b_top = b + b_offset
            b_bot = b - b_offset

            for neigh in neighbours:
                # these are the heights of the offset lines at the x position of the neighbour
                y_top = slope * neigh.pos[0] + b_top
                y_bot = slope * neigh.pos[0] + b_bot

                if neigh.pos[1] >= y_top and neigh.pos[1] <= y_bot:
                    intersecting.append(neigh)

        return inter_neighbors

    def rotate(self, origin, point, i):
        """
        Rotate a point counterclockwise by a given angle around a given origin.

        The angle should be given in radians.
        """
        if self.dir == 'up':
            angle = self.direction - 270
        else:
            angle = self.direction - 90

        if angle < 0:
            angle += 360
        angle_rad = math.radians(angle)
        ox, oy = origin
        px, py = point

        qx = ox + math.cos(angle_rad) * (px - ox) - math.sin(angle_rad) * (py - oy)
        qy = oy + math.sin(angle_rad) * (px - ox) + math.cos(angle_rad) * (py - oy)
        return (qx, qy, i)

    def closest_ped_on_line(self, neighboursList, direction):
        """
        This would find the closest pedestrian to a path given a subset of pedestrians
        """
        for neighbours in neighboursList:

            # Find the terms for the equation for the line that will be passing through the current point in direction
            m = math.tan(math.radians(direction))
            b = self.pos[1] - (m*self.pos[0])
            # Calculate the first distance from the line (perpendicular distance and assign the min pedestrian
            min_distance = abs((m*neighbours[0].pos[0])-neighbours[0].pos[1]+b)/math.sqrt((m**2) + 1)
            min_pedestrian = neighbours[0]
            # If there are more, check the rest
            if len(neighbours)>1:
                for i in range(1, len(neighbours)):
                    # calculate the distance if the current neighbour
                    cur_distance = abs((m * neighbours[i].pos[0]) - neighbours[i].pos[1] + b) / math.sqrt((m ** 2) + 1)
                    # Checks distance against that stored
                    if cur_distance < min_distance:
                        min_pedestrian = neighbours[i]
                        min_distance = cur_distance
                    # if equal checks to see which is closer to the current position.
                    elif cur_distance == min_distance:
                        if self.model.space.get_distance(self.pos, min_pedestrian.pos) > self.model.space.get_distance(self.pos, neighbours[i].pos):
                            min_pedestrian = neighbours[i]
                            min_distance = cur_distance

                # Returns the min distance and the corresponding pedestrian
        return min_distance, min_pedestrian


    def closest_pedestrian(self, inter_neigh, direction):
        """
        This is used to find the closest pedestrian of a given included list of neighbours
        Returns distance to and the position of the closest pedestrian
        TODO: check
        """
        c = self.model.space.get_distance(self.pos, inter_neigh[0].pos)
        min_neigh = inter_neigh[0]
        for i in range(1, len(inter_neigh)):
            cur_distance = self.model.space.get_distance(self.pos, inter_neigh[i].pos)
            if cur_distance < c:
                c = cur_distance
                min_neigh = inter_neigh[i]

        b = self.closest_ped_on_line(min_neigh, direction)[0]

        min_distance = math.sqrt(c**2 + b**2)

        return min_distance

    def ped_velocity_interaction(self, neighbours):
        """Calculates the interaction between pedesrians based off the angle of their movement"""
        # Takes in a list of neighbours and returns a utility value
        # The start value
        Ak = 1
        # cycles through neighbours and adds the utility (this is for if we want to incorperate flocking later, we just pass it a larger list and bam! This part is done
        for neigh in neighbours:
            Ak = Ak - (abs(self.direction - neigh.direction)/math.pi)
        return Ak

    def traffic_green(self):
        """
        Returns true if light is green
        """
        # TODO: Hardcoded coordinates (use actual light attribute?)
        correct_side = True

        if self.dir == "up" and not self.pos[1] < 16:
            # check where the pedestrian is and assign it to the right traffic light
            if self.pos[1] > 21:
                own_light = self.own_light1
                correct_side = False
            elif self.pos[1] >= 16 and self.pos[1] <= 17:
                own_light = self.own_light2
                correct_side = False
        elif self.dir == "down" and not self.pos[1] > 17:
            if self.pos[1] < 11:
                own_light = self.own_light1
                correct_side = False
            elif self.pos[1] >= 16 and self.pos[1] <= 17:
                own_light = self.own_light2
                correct_side = False

        if not correct_side:
            # iterate over all the agents to find the correct light
            for i in self.model.space.get_neighbors(own_light, include_center = True, radius = 0):
                # if it's your own light, and it's not green
                if not i.color == "Green":
                    return False

        return True


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

    # Car test:
    # Can a traffic jam occur like in the NS model?
    # - create a very long road, and make the car in front slow down for a bit, and watch the emergent process througout ...
    # ... the rest of the traffic

    def __init__(self, unique_id, model, pos, dir, speed=0.8, time=0):
        super().__init__(unique_id, model)

        self.max_speed = 0.8
        self.pos = pos
        self.dir = dir
        self.speed = speed
        self.time = time
        self.vision_range = self.braking_distance() + self.speed + 2
        self.speed_changed = False

        # the correct_side is the side where the car is heading
        self.correct_side = False
        if self.dir == "right":
            self.direction = 1
            self.own_light = (44.54, 22.4)
        else:
            self.direction = -1
            self.own_light = (54.46, 10.6)

    def step(self):
        #Cars go straight for now.
        self.speed_changed = False
        # deteremines if the agent has passed his own traffic light
        if self.correct_side == False and (self.vision_range > (self.own_light[0] - self.pos[0]) * self.direction):
            for i in self.model.space.get_neighbors(self.own_light, include_center = True, radius = 0):

                # if the light is orange and there is time to slow down regularly
                if i.color == "Orange":
                    if self.dir == "right":
                        if self.braking_distance() > ((self.own_light[0] - 1) - self.pos[0]):
                            self.speed_change(-0.8/40)

                    else:
                        if self.braking_distance() > self.pos[0] - (self.own_light[0] + 1):
                            self.speed_change(-0.8/40)


                # if the light is red, make sure to stop, by slowing down twice the normal rate
                elif i.color == "Red":
                    if self.dir == "right":
                        if self.braking_distance() > ((self.own_light[0] - 1) - self.pos[0]):
                            self.speed_change(-0.8/20)

                    else:
                        if self.braking_distance() > self.pos[0] - (self.own_light[0] + 1):
                            self.speed_change(-0.8/20)


        # if there is a car in front and within speed, stop right behind it
        if self.check_front() > 0 and self.check_front() < self.braking_distance() and self.speed > 0:
            self.speed_change(-0.8/40)

        elif self.check_front() > 0 and self.check_front() > self.braking_distance():
            self.speed_change(0.8/40)

        # if there are no cars ahead and no traffic lights, speed up till max speed
        # (self.speed == 0 and ((self.own_light[0] - 1) - self.pos[0]) > 0) or
        elif (self.speed < self.max_speed and self.correct_side == True):
            self.speed_change(0.8/40)

        elif self.speed < self.max_speed and self.correct_side == False and (self.vision_range > (self.own_light[0] - self.pos[0]) * self.direction):
            if i.color == "Green":
                self.speed_change(0.8/40)

        # elif self.speed < self.max_speed and self.correct_side == True:
        #     self.speed_change(0.8/40)

        # take a step
        next_pos = (self.pos[0] + self.speed * self.direction, self.pos[1])
        self.model.space.move_agent(self, next_pos)

        # checks if the traffic light has been passed (this information is used in next time step)
        if self.correct_side == False:
            if self.dir == "right":
                if self.pos[0] > (self.own_light[0] - 1):
                    self.correct_side = True
            else:
                if self.pos[0] < (self.own_light[0] + 1):
                    self.correct_side = True

        self.time += 1


    def speed_change(self, amount):
        if self.speed_changed == False:
            self.speed = self.speed + amount
            self.speed_changed = True

        if self.speed < 0:
            self.speed = 0

        if self.speed > 0.8:
            self.speed = 0.8


    def check_front(self):
        '''
        Function to see if there is a car closeby in front of a car
        '''
        # Find all the neighbours
        # We may want to assign each car a car in front of it which we use instead of this.  That would be easier.
        neighbours = self.model.space.get_neighbors(self.pos, include_center = False, radius = self.vision_range)
        min_dist = self.vision_range + 1
        # if there are neighbours
        if neighbours:
            car_neighbours = []
            #Find those that are cars
            for neigh in neighbours:
                if (type(neigh) == Car):
                    car_neighbours.append(neigh)
            # if there are cars
            if car_neighbours:
                min_dist = 99999
                for neigh in car_neighbours:
                    new_dist = self.model.space.get_distance(self.pos, neigh.pos)
                    # Find the closest one
                    if new_dist < min_dist and self.dir == neigh.dir:
                        if (self.dir == "right" and self.pos[0] < neigh.pos[0]) or (self.dir == "left" and self.pos[0] > neigh.pos[0]):
                            min_dist = new_dist - 3
                if min_dist is not 99999:
                    return min_dist
                else:
                    return 0
            else:
                return 0
        else:
            return 0


    def braking_distance(self):
        distance = 0
        current_speed = self.speed
        # can be optimized
        while current_speed > 0:
            distance = distance + current_speed
            current_speed = current_speed - 0.02
        return distance + 3.5
