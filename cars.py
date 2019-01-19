class Car(Agent):
    def __init__(self, unique_id, model, pos, dir, speed=3, time=0):
        super().__init__(unique_id, model)

        self.max_speed = 3
        self.pos = pos
        self.dir = dir
        self.speed = speed
        self.time = time
        self.vision_range = self.braking_distance() + self.speed

        # the correct_side is the side where the car is heading
        self.correct_side = False
        if self.dir == "right":
            self.direction = 1
            self.own_light = (20, 30)
        else:
            self.direction = -1
            self.own_light = (30,20)

    def step(self):
        '''
        Cars go straight for now.
        '''
        # deteremines if the agent has passed his own traffic light
        if self.correct_side == False and (self.vision_range > (self.own_light[0] - self.pos[0]) * self.direction):
            for i in self.model.space.get_neighbors(self.own_light, include_center = True, radius = 0):

                # if the light is orange and there is time to slow down, slow down in steps of 1
                if i.state > 100:
                    if self.dir == "right":
                        if self.braking_distance() < ((self.own_light[0] - 1) - self.pos[0]):
                            self.speed = self.speed - 1
                    else:
                        if self.braking_distance() < self.pos[0] - (self.own_light[0] + 1):
                            self.speed = self.speed - 1

                # if the light is red, make sure to stop, even by slowing down more than 1 speed per step
                elif i.state < 50:
                    if self.dir == "right":
                        if self.braking_distance() < ((self.own_light[0] - 1) - self.pos[0]):
                            self.speed = self.speed - 1
                        elif:

                    else:
                        if self.braking_distance() < self.pos[0] - (self.own_light[0] + 1):
                            self.speed = self.speed - 1

                            self.speed = (self.own_light[0] - self.pos[0]) - 1

        # if there is a car in front and within speed, stop right behind it
        if self.check_front() > 0:
            self.speed = self.check_front() - 1
        
        # if there are no cars ahead and no traffic lights, speed up till max speed
        elif self.speed < self.max_speed:
            self.speed = self.speed + 1
        
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
        for i in range(0, self.speed):
            for agent in self.model.space.get_neighbors((self.pos[0] + self.direction * (i + 1), self.pos[1]), radius = 0):
                if isinstance(agent, Car) or isinstance(agent, Pedestrian):
                    return i + 1
        return 0

    def braking_distance(self):
        distance = 0
        for i in range(1, self.speed + 1):
            distance = distance + i
        return distance
