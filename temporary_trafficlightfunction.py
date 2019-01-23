    def traffic_green(self):
        """
        Returns true if light is red
        """
        # TODO: Hardcoded coordinates (use actual light attribute?)
        correct_side = True

        if self.dir == "up" and not self.pos[1] < 24.65:

            # check where the pedestrian is and assign it to the right traffic light
            if self.pos[1] > 29:
                own_light = 4
                correct_side = False
            elif self.pos[1] >= 24.65 and self.pos[1] <= 25.35:
                own_light = 3
                correct_side = False

        # so direction is false
        elif self.dir == "down" and not self.pos[1] > 25.35:
            if self.pos[1] < 21:
                own_light = 5
                correct_side = False
            elif self.pos[1] >= 24.65 and self.pos[1] <= 25.35:
                own_light = 6
                correct_side = False

        if not correct_side:

            # Iterate over all the agents to find the correct light
            for i in self.model.space.get_neighbors(self.pos, include_center = False, radius = 9):
                # If the agent is a light, which is red or orange, which is your own light and you're in front of the light
                if (isinstance(i,Light) and (i.state < 50 or i.state > 100) and i.light_id == own_light):
                    return False

        return True
