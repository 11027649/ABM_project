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

        self.remove = False

        # Liu, 2014 parameters
        self.vision_angle = 170  # Degrees
        self.walls_x = [23*2, 27*2] # TODO: correct walls?

        # parameters
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
        elif self.dir == "down":
            self.direction = 90
            self.target_point = (random.uniform(24*2,26*2), 50)
        else:
            raise ValueError("invalid direction, choose 'up' or 'down'")

        # Check if walls are far enough for dist_walls function
        if abs(self.walls_x[0]-self.walls_x[1])<2*self.R_vision_range:
            raise ValueError("Walls are too close together for the dist_walls function to work correctly")



    def step(self):
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

            # Get new position and update direction
            next_pos, self.direction = self.choose_direction()

            # TODO: de-comment this if we're running this step function
            # Move to new position
            # self.model.space.move_agent(self, next_pos)

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
        peds_in_180 = self.pedestrians_in_field(180, self.R_vision_range)

        # Loop over the possible directions
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
        theta_N = self.vision_angle/(self.N-1)
        pos_directions = []
        for i in range(self.N):
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
            closest_ped = self.closest_pedestrian(peds_in_dir)
            cpil = self.closest_ped_on_line(peds_in_dir, direction)[1]
            theta_vj = self.direction - cpil.direction
            # If no pedestrians in view, closest_ped distance is set at vision range
        else:
            closest_ped = self.R_vision_range
            theta_vj = 0
        
        # Distance to road 'wall', if no pedestrians in view, closest_ped is set at vision range
        closest_wall = self.dist_wall(direction)

        # Determine possible new position
        chosen_velocity = min(self.des_speed, closest_ped, closest_wall)
        next_pos = self.new_pos(chosen_velocity, direction)

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


        # Equation 7
        # return -self.Ok_w_7 * (1-Ok) - \
        # self.Pk_w_7 * (1-Pk) - self.Ak_w_7 * (1-Ak) - \
        # self.Ik_w * (1-Ik), next_pos

        # # Using equation 1 for now:
        # TODO: Do we want to change to equation 7? I don't quite understand 7..
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

        return inter_neighbors


    def closest_ped_on_line(self, neighbours, direction):
        """
        This would find the closest pedestrian to a path given a subset of pedestrians
        """
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
                    if self.model.space.get_distance(self.pos, min_pedestrian.pos) > self.model.space.get_distance(self.pos, neighbours.pos):
                        min_pedestrian = neighbours[i]
                        min_distance = cur_distance

        # Returns the min distance and the corresponding pedestrian
        return min_distance, min_pedestrian


    def closest_pedestrian(self, inter_neigh):
        """
        This is used to find the closest pedestrian of a given included list of neighbours
        Returns distance to and the position of the closest pedestrian
        """
        min_distance = self.model.space.get_distance(self.pos, inter_neigh[0].pos)
        for i in range(1, len(inter_neigh)):
            cur_distance = self.model.space.get_distance(self.pos, inter_neigh[i].pos)
            if cur_distance < min_distance:
                min_distance = cur_distance

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


    def step_old(self):
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
    def __init__(self, unique_id, model, pos, dir, speed=5, time=0):
        super().__init__(unique_id, model)

        self.max_speed = 5
        self.pos = pos
        self.dir = dir
        self.speed = speed
        self.time = time
        self.vision_range = self.braking_distance() + self.speed

        # the correct_side is the side where the car is heading
        self.correct_side = False
        if self.dir == "right":
            self.direction = 1
            self.own_light = (int(0.45 * model.x_max), int(0.6 * model.y_max))
        else:
            self.direction = -1
            self.own_light = (int(0.55 * model.x_max), int(0.4 * model.y_max))

    def step(self):
        '''
        Cars go straight for now.
        '''
        # deteremines if the agent has passed his own traffic light
        if self.correct_side == False and (self.vision_range > (self.own_light[0] - self.pos[0]) * self.direction):
            for i in self.model.space.get_neighbors(self.own_light, include_center = True, radius = 0):

                # if the light is orange and there is time to slow down, slow down in steps of 1
                current_state = i.state
                if current_state > 100:
                    if self.dir == "right":
                        if self.braking_distance() > ((self.own_light[0] - 1) - self.pos[0]):
                            self.speed = self.speed - 1
                        
                    else:
                        if self.braking_distance() > self.pos[0] - (self.own_light[0] + 1):
                            self.speed = self.speed - 1
                

                # if the light is red, make sure to stop, even by slowing down more than 1 speed per step
                elif current_state < 50:
                    if self.dir == "right":
                        if self.braking_distance() > ((self.own_light[0] - 1) - self.pos[0]):
                            self.speed = self.speed - 1

                    else:
                        if self.braking_distance() > self.pos[0] - (self.own_light[0] + 1):
                            self.speed = self.speed - 1

        # if there is a car in front and within speed, stop right behind it
        if self.check_front() > 0:
            if self.speed > 0:
                self.speed = self.check_front() - 4
                if self.speed < 0:
                    self.speed = 0
        
        # if there are no cars ahead and no traffic lights, speed up till max speed
        elif (self.speed == 0 and ((self.own_light[0] - 1) - self.pos[0]) > 0) or (self.speed < self.max_speed and self.correct_side == True):
            self.speed = self.speed + 1

        elif self.speed < self.max_speed and self.correct_side == False and (self.vision_range > (self.own_light[0] - self.pos[0]) * self.direction):
            if current_state > 50 and current_state < 100:
                self.speed = self.speed + 1
        
        elif self.speed < self.max_speed and self.correct_side == False:
            self.speed = self.speed + 1
        

        if self.check_front() > 0:
            if self.speed > 0:
                self.speed = self.check_front() - 4
                if self.speed < 0:
                    self.speed = 0
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


    def check_front(self):
        '''
        Function to see if there is a car closeby in front of a car
        '''
        for i in range(0, self.speed + 4):
            for agent in self.model.space.get_neighbors((self.pos[0] + self.direction * (i + 1), self.pos[1]), radius = 0):
                if isinstance(agent, Car) or isinstance(agent, Pedestrian):
                    return i + 1
        
        return 0

    def braking_distance(self):
        distance = 0
        for i in range(1, self.speed + 1):
            distance = distance + i
        return distance
