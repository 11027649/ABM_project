from mesa.space import ContinuousSpace
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule
from SimpleContinuousModule import SimpleCanvas
from model import Traffic
from agent import Car, Pedestrian, Road, Light
import numpy as np
import math

# Where I got the method from http://totologic.blogspot.com/2014/01/accurate-point-in-triangle-test.html
def find_cone(self, vision_angle, num_dir, range):
    # Find the current heading
    my_angle = math.degrees(math.atan((self.pos[1]-self.prev_pos[1])/(self.pos[0]-self.prev_pos[0])))
    cur_angle = mesa.space.get_heading(self.pos, self.prev_pos)
    if (cur_angle==my_angle):
        print("all good")
    else:
        print("Well something fucked up")

    # Calculate the lower angle and the upper angle
    lower_angle = cur_angle-(vision_angle/2)
    upper_angle = cur_angle+(vision_angle/2)

    # Change the current points to an np array for simplicity
    p0 = np.array(self.pos)

    # Convert to radians for angle calcuation
    u_rads = math.radians(upper_angle)
    l_rads = math.radians(lower_angle)

    # Calculate the end angles
    dx1 = cos(l_rads) * range
    dy1 = sin(l_rads) * range
    dx2 = cos(u_rads) * range
    dy2 = sin(u_rads) * range

    # Calculate the vectors
    v1 = np.array([p0[0]+dx1, p0[1]+dy1])
    v2 = np.array([p0[0]-dx2, p0[1]+dy2])

    # Get the current neighbors
    neighbours = self.model.space.get_neighbors(self.pos, include_center = False, radius = range)
    cone_neigh = []
    # Loop to find if neighbor is within the cone
    for neigh in neighbours:
        v3 = np.array(neigh.pos) - p0
        if (np.cross(v1,v3)*np.cross(v1,v2)>=0 and np.cross(v2,v3)*np.cross(v2,v1)>=0):
            print("The pos", neigh.pos(), "is within the cone")
            cone_neigh.append(neigh)
        else:
            print("The pos", neigh.pos(), "is within the cone")

    return cone_neigh