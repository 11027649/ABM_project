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
        self.walls_x = [45.54, 53.46] # TODO: correct walls?
        self.neighbours = []
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
        # isn't it plusmines 0.342, so it's supposed to be half of it?


        # Set direction in degrees
        # TODO: assign target point with preference to right side?
        if self.dir == "up":
            self.direction = 270
            self.target_point = (random.uniform(24*2,26*2), 0)
            self.own_light = 5
        elif self.dir == "down":
            self.direction = 90
            self.target_point = (random.uniform(24*2,26*2), 50)
            self.own_light = 2
        else:
            raise ValueError("invalid direction, choose 'up' or 'down'")

        # Check if walls are far enough for dist_walls function
        if abs(self.walls_x[0]-self.walls_x[1])<2*self.R_vision_range:
            raise ValueError("Walls are too close together for the dist_walls function to work correctly")


    def step(self):
        """
        stepfunction based on Liu, 2014
        This is a stepfunction based on Liu, 2014. The stepfunction checks if the
        the pedestrian is on the road side and if the traffic light is green.
        The pedestrians always go on green, and never go on red or orange. They will
        walk through orange if they're already on the road.
        """

        # check if traffic light is green or if on road side
        if not self.on_road_side() or self.traffic_green():
            # get list of pedestrians in the vision field
            # TODO: check if we can do it with only 180
            self.neighbours = self.model.space.get_neighbors(self.pos, include_center=False, radius=self.R_vision_range)

            peds_in_vision = self.pedestrians_in_field(self.vision_angle)

            # get desired_speed
            self.des_speed = self.desired_speed(len(peds_in_vision))

            # get new position and update direction
            next_pos, self.direction = self.choose_direction()

            # try to move agent
            try:
                self.model.space.move_agent(self, next_pos)
            except:
                # if it gave an exeption and it is trying to go in the wrong direction
                if ((self.dir == "up" and self.direction%360 <180) or
                    (self.dir == "down" and self.direction%360 >180)):
                    # let it be removed by the step function in model.py
                    self.remove = True


            # self test, this should never happen: if it does, something is wrong in our code
            neighbors = self.model.space.get_neighbors(self.pos, include_center=False, radius=self.radius)
            if len(neighbors) > 0:
                for i in neighbors:
                    if type(i) != Light:
                        print('error pos', self.pos)
                        print('error dir', self.dir)
                        print('waar hij in loopt', i.pos)
                        print(i)
                        print('dist', math.sqrt((self.pos[0]-i.pos[0])**2+(self.pos[1]-i.pos[1])**2))
                        raise ValueError("COLLISION")

            # Finalize this step
            self.time += 1

    def on_road_side(self):
        """
        This is a function that checks if the pedestrian is near the road. If
        it's not, it never has to stop.
        """
        # TODO: Use light coordinates?
        # if the direction is up, and it's near the road sides or in the middle part
        if self.dir == "up":
            if self.pos[1] > 22.2 and self.pos[1] < 22.6:
                return True
            elif self.pos[1] < 16.4 and self.pos[1] > 16:
                return True
        # same for down
        elif self.dir == "down":
            if self.pos[1] < 10.8 and self.pos[1] > 10.4:
                return True
            elif self.pos[1] < 17 and self.pos[1] > 16.6:
                return True
        # not on road side
        else:
            return False

    def traffic_green(self):
        """
        Returns true if the light the pedestrian is supposed to be looking at, is green.
        """
        # TODO: Hardcoded coordinates (use actual light attribute?)
        correct_side = True

        # check where the pedestrian is and assign it to the right traffic light
        if self.dir == "up" and not self.pos[1] < 16:
            if self.pos[1] > 21:
                correct_side = False
            elif self.pos[1] >= 16 and self.pos[1] <= 17:
                self.own_light = 4
                correct_side = False
        elif self.dir == "down" and not self.pos[1] > 17:
            if self.pos[1] < 11:
                correct_side = False
            elif self.pos[1] >= 16 and self.pos[1] <= 17:
                self.own_light = 3
                correct_side = False


        if not correct_side and not self.model.lights[self.own_light].color is "Green":
            return False

        return True
    def pedestrians_in_field(self, vision_angle):
        """
            Returns the pedestrians that are in the cone that the pedestrian can
            actually see in a certain vision_angle (which usually is 170, but
            can also be a bit heigher to check the most outer parts.).
        """

        # get all surrounding neighbors

        rotatedNeighList = []
        i = -1
        # rotate all the neigbours facing either up or down
        for neigh in self.neighbours:
            i = i + 1

            if isinstance(neigh, Pedestrian):
                rotatedNeighList.append(self.rotate(self.pos, neigh.pos, i))

        cone_neigh = []

        # calculate if the pedestrians are within the 'viewing triangle'
        for rotatedNeigh in rotatedNeighList:
            if rotatedNeigh[1] - self.pos[1] < -math.tan(math.radians(90 - (vision_angle / 2))) * abs(rotatedNeigh[0] - self.pos[0]):
                cone_neigh.append(self.neighbours[rotatedNeigh[2]])

        return cone_neigh

    def rotate(self, origin, point, i):
        """
        Rotate a point counterclockwise by a given angle around a given origin.
        The angle should be given in radians.
        # TODO: Move this function to a helper functions file?
        """

        # if self.dir == 'up':
        rot_angle = self.direction - 270
        # else:
        #     angle = self.direction - 90

        if rot_angle < 0:
            rot_angle += 360

        angle_rad = math.radians(rot_angle)

        ox, oy = origin
        px, py = point

        qx = ox + math.cos(angle_rad) * (px - ox) - math.sin(angle_rad) * (py - oy)
        qy = oy + math.sin(angle_rad) * (px - ox) + math.cos(angle_rad) * (py - oy)

        return (qx, qy, i)

    def desired_speed(self, n_agents_in_cone, gamma=1.913, max_density=5.4):
        """
        Returns desired speed, using equation 8 of Liu. Input is the number of
        agents in the vision field. This number is used to calculate the density
        of the pedestrians in the field. Works for vision angle of 170 degrees,
        which is the range in which the pedestrians can see.
        """

        # sanity check
        if self.vision_angle == 170:
            dens = 0.0376
        else:
            raise ValueError('Code only works for 170 degrees vision range for now')

        # if there are no agents, you can walk freely
        if n_agents_in_cone <= 0:
            return self.speed_free

        # calculate cone density
        cone_density = n_agents_in_cone * dens
        # calculate the desired speed (see eq. 8, Liu)
        des_speed = self.speed_free*(1 - np.exp(-gamma*((1/cone_density)-(1/max_density))))

        # if the pedestrian wants to go backwards, return 0.
        if des_speed >= 0:
            return des_speed
        else:
            return 0

    def choose_direction(self):
        """
        Picks the direction with the highest utility
        """

        # for getting the neighbours in the front 180 degrees within vision range; for calc_utility
        peds_in_180 = self.pedestrians_in_field(170)

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
        Includes outer directions of the vision range.
        """

        # calculate the lower angle and the upper angle
        lower_angle = self.direction - (self.vision_angle / 2)

        # get list of possible directions
        theta_N = self.vision_angle/(self.N-1)
        pos_directions = []
        for i in range(self.N):
            pos_directions.append((lower_angle+i*theta_N)%360)

        return pos_directions

    def calc_utility(self, direction, peds_in_180):
        """
        Calculate the utility for one out of possible directions.
        """

        # list of pedestrians in that direction
        # DEBUG (put in all surrounding neighbours)
        # peds_in_180 = self.model.space.get_neighbors(self.pos, include_center = False, radius = self.R_vision_range)
        peds_in_dir = self.pedestrian_intersection(direction, self.radius*2 + 0.01)

        # DEBUG
        # print('True angle', direction)
        # print()
        # get closest pedestrian in this directions
        if len(peds_in_dir) > 0:
            # get closest pedestrian: min_distance, min_pedestrian.pos
            closest_ped = self.closest_pedestrian(peds_in_dir, direction) - 2 * self.radius
            # set negative distance to 0
            if closest_ped < 0:
                closest_ped = 0
            # if no pedestrians in view, closest_ped distance is set at vision range
        else:
            closest_ped = self.R_vision_range-2*self.radius

        # distance to road 'wall', if no pedestrians in view, closest_ped is set at vision range
        closest_wall = self.dist_wall(direction) - 4*self.radius
        # set negative distance to 0
        if closest_wall < 0:
            closest_wall = 0

        # determine possible new position
        chosen_velocity = min(self.des_speed, closest_ped, closest_wall)
        next_pos = self.new_pos(chosen_velocity, direction)
        # print('velocities', chosen_velocity, self.des_speed, closest_ped, closest_wall)

        # finds the pedestrians in the next step length
        if len(peds_in_180)>0:
            cpil = self.closest_ped_on_line(peds_in_180, direction)[1:]
            theta_vj = self.theta_angle(direction, cpil[0],cpil[1])
        else:
            theta_vj = 0

        # if the target point is not within vision:
        if self.model.space.get_distance(self.pos, self.target_point) > self.R_vision_range:
            # calculate distance from possible next_pos to target point projection on vision field
            target_proj = self.target_projection()
            target_dist = self.model.space.get_distance(next_pos, target_proj)
        # if Target point is within the vision field, calculate the distance to the real target point
        else:
            target_dist = self.model.space.get_distance(next_pos, self.target_point)

        # calculate factors
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
        TODO: This function is never called?????????
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

    def theta_angle(self, direction, ped, side):
        """Returns the angle between direction and the angle of the closest
        pedestrian to that line. If the velocities do not cross, theta=0.
        """

        # Errorcheck
        if side != "left" and side != "right":
            raise ValueError("side should be 'left' or 'right', not", side)

        # For pedestrian on left side with angle to the right (i.e. crossing direction)
        elif side == "left":
            # If area for angle is in two pieces (divided by radian=0 line)
            if direction > 180:
                # If angle and direction are on the same side of division
                if ped.direction > direction:
                    return ped.direction-direction
                # If angle and direction are NOT on the same side of division
                elif ped.direction < (direction+180)%360:
                    return 360-direction + ped.direction

            # If area for angle is in ONE piece
            else:
                if ped.direction > direction and ped.direction < (direction+180):
                    return ped.direction-direction


        # For pedestrian on right side with angle to the left (i.e. crossing direction)
        elif side == "right":
            # If area for angle is in two pieces (divided by radian=0 line)
            if direction < 180:
                # If angle and direction are on the same side of division
                if ped.direction < direction:
                    return direction-ped.direction
                # If angle and direction are NOT on the same side of division
                elif ped.direction > direction+180:
                    return direction + 360-ped.direction

            # If area for angle is in ONE piece
            else:
                if ped.direction < direction and ped.direction > (direction+180)%360:
                    return direction-ped.direction

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

    def pedestrian_intersection(self, angle, offset):
        """
        Input: conal_neighbours, the neighbours that the pedestrian can see.
        The function will check for intersections on the given angle. For this we
        need an offset, because the pedestrians have a radius. The function
        returns a list of intersecting neighbours.
        Angle: the direction k that we're calculating utility for.
        Offset: 1.5*radius_of_pedestrian to both sides of the direction line: 0.3.
        """

        intersecting = []
        for neighbour in self.neighbours:
            rotatedPed = self.rotate_intersection(self.pos, neighbour.pos, angle)
            if rotatedPed[0] >= self.pos[0] - self.radius and rotatedPed[1] >= self.pos[1] - offset and rotatedPed[1] <= self.pos[1] + offset:
                intersecting.append(neighbour)
        # print('aaa')
        # print(intersecting)
        return intersecting

    def closest_ped_on_line(self, neighboursList, direction):
        """intersecting
        This would find the closest pedestrian to a path given a subset of pedestrians
        """
        # Find the terms for the equation for the line that will be passing through the current point in direction
        a = math.tan(math.radians(direction))
        b = self.pos[1]

        # y = a * (x - self.pos[0]) + b
        min_distance = math.inf
        for neighbour in neighboursList:

            # calculate the distance of the current neighbour https://en.wikipedia.org/wiki/Distance_from_a_point_to_a_line
            cur_distance = abs(a * neighbour.pos[0] - neighbour.pos[1] + b)/math.sqrt(a**2 + 1)

            # Checks distance against that stored
            if cur_distance < min_distance:
                if self.rotatePedestrian(self.pos, neighbour.pos, direction)[0] < self.pos[0]:
                    side = 'right'
                else:
                    side = 'left'
                min_pedestrian = neighbour
                min_distance = cur_distance

            # if equal checks to see which is closer to the current position.
            elif cur_distance == min_distance:
                if self.model.space.get_distance(self.pos, min_pedestrian.pos) > self.model.space.get_distance(self.pos, neighbour.pos):
                    if self.rotatePedestrian(self.pos, neighbour.pos, direction)[0] < self.pos[0]:
                        side = 'right'
                    else:
                        side = 'left'
                    min_pedestrian = neighbour
                    min_distance = cur_distance
        # print(side)
        # Returns the min distance and the corresponding pedestrian
        return min_distance, min_pedestrian, side

    # TODO: can prob be in 1 function

    def rotate_intersection(self, origin, point, angle):
        """
        Rotate a point counterclockwise by a given angle around a given origin.

        The angle should be given in radians.
        """

        if angle < 0:
            angle += 360
        angle_rad = math.radians(angle)
        ox, oy = origin
        px, py = point

        qx = ox + math.cos(angle_rad) * (px - ox) + math.sin(angle_rad) * (py - oy)
        qy = oy - math.sin(angle_rad) * (px - ox) + math.cos(angle_rad) * (py - oy)
        return (qx, qy)

    def rotatePedestrian(self, origin, point, direction):
        """
        Rotate a point counterclockwise by a given angle around a given origin.

        The angle should be given in radians.
        """

        angle = direction - 270
        if angle < 0:
            angle += 360
        angle_rad = math.radians(angle)
        ox, oy = origin
        px, py = point

        qx = ox + math.cos(angle_rad) * (px - ox) - math.sin(angle_rad) * (py - oy)
        qy = oy + math.sin(angle_rad) * (px - ox) + math.cos(angle_rad) * (py - oy)
        return (qx, qy)

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

        # b = self.closest_ped_on_line([min_neigh], direction)[0]
        # min_distance = math.sqrt(c**2 + b**2)
        min_distance = c
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



class Car(Agent):
    # a traffic jam like in the NS model doesn't happen, (because the time steps are to small?)
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
            self.own_light = 0
        else:
            self.direction = -1
            self.own_light = 1

    def step(self):
        # cars go straight for now.
        self.speed_changed = False
        light = self.model.lights[self.own_light]

        # determines if the agent has passed his own traffic light
        if self.correct_side == False and (self.vision_range > (light.pos[0] - self.pos[0]) * self.direction):

            # if the light is orange and there is time to slow down regularly
            if light.color == "Orange":
                if self.dir == "right":
                    if self.braking_distance() > ((light.pos[0] - 1) - self.pos[0]):
                        self.speed_change(-0.8/40)
                else:
                    if self.braking_distance() > self.pos[0] - (light.pos[0] + 1):
                        self.speed_change(-0.8/40)

                # if the light is red, make sure to stop, by slowing down twice the normal rate
            elif light.color == "Red":
                    if self.dir == "right":
                        if self.braking_distance() > ((light.pos[0] - 1) - self.pos[0]):
                            self.speed_change(-0.8/20)
                    else:
                        if self.braking_distance() > self.pos[0] - (light.pos[0] + 1):
                            self.speed_change(-0.8/20)


        # if there is a car in front and within speed, stop right behind it
        if self.check_front() > 0 and self.check_front() < self.braking_distance() and self.speed > 0:
            self.speed_change(-0.8/40)

        elif self.check_front() > 0 and self.check_front() > self.braking_distance():
            self.speed_change(0.8/40)

        # if there are no cars ahead and no traffic lights, speed up till max speed
        elif (self.speed < self.max_speed and self.correct_side == True):
            self.speed_change(0.8/40)

        elif self.speed < self.max_speed and self.correct_side == False and (self.vision_range > (light.pos[0] - self.pos[0]) * self.direction):
            if light.color == "Green":
                self.speed_change(0.8/40)

        # take a step
        next_pos = (self.pos[0] + self.speed * self.direction, self.pos[1])
        self.model.space.move_agent(self, next_pos)

        # checks if the traffic light has been passed (this information is used in next time step)
        if self.correct_side == False:
            if self.dir == "right":
                if self.pos[0] > (light.pos[0] - 1):
                    self.correct_side = True
            else:
                if self.pos[0] < (light.pos[0] + 1):
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
                if type(neigh) is Car or type(neigh) is Pedestrian:
                    car_neighbours.append(neigh)
            # if there are cars
            if car_neighbours:
                min_dist = 99999
                for neigh in car_neighbours:
                    new_dist = self.model.space.get_distance(self.pos, neigh.pos)
                    # Find the closest one
                    if (new_dist < min_dist and self.dir is neigh.dir) or (type(neigh) is Pedestrian and (neigh.pos[1] > 11 and neigh.pos[1] < 16) or (neigh.pos[1] > 17 and neigh.pos[1] < 22)):
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
