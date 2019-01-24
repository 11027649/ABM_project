from mesa.space import ContinuousSpace
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule
from SimpleContinuousModule import SimpleCanvas
from model import Traffic
from agent import Car, Pedestrian, Light

# You can change this to whatever you want. Make sure to make the different types
# of agents distinguishable
def agent_portrayal(agent):
    if type(agent) is Light:
        if agent.state < 50:
            current_color = "Red"
        elif agent.state < 100:
            current_color = "Green"
        else:
            current_color = "Orange"

    if type(agent) is Pedestrian:
        if agent.dir == "up":
            pedest_color = "Blue"
        else:
            pedest_color = "Purple"

    portrayal = {"Shape": "rect" if type(agent) is Car else "circle",
                 "Color": pedest_color if type(agent) is Pedestrian
                 else current_color if type(agent) is Light
                 else "Pink",
                 "Filled": "true",
                 "w": 25 if type(agent) is Car else None,
                 "h": 25 if type(agent) is Car else None,
                 "r": 3 if type(agent) is not Car else None}
    return portrayal


# Create a grid of 20 by 20 cells, and display it as 500 by 500 pixels
space = SimpleCanvas(agent_portrayal)

# Create the server, and pass the grid and the graph
server = ModularServer(Traffic,
                       [space],
                       "Traffic Model",
                       {})
