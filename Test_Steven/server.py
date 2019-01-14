from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule

from model import Traffic
from agent import Car, Pedestrian, Road, Light

# You can change this to whatever you want. Make sure to make the different types
# of agents distinguishable
def agent_portrayal(agent):
    if type(agent) is Light:
        if agent.state < 50:
            current_color = "red"
        elif agent.state < 100:
            current_color = "green"
        else:
            current_color = "orange"

    portrayal = {"Shape": "rect" if type(agent) is Road else "circle",

                 "Color": "blue" if type(agent) is Pedestrian 
                 else "black" if type(agent) is Road 
                 else current_color if type(agent) is Light 
                 else "pink",

                 "Filled": "true",
                 "Layer": 0 if type(agent) is Road else 1,
                 "w": 1,
                 "h": 1,
                 "r": 0.5}
    return portrayal

# Create a grid of 20 by 20 cells, and display it as 500 by 500 pixels
grid = CanvasGrid(agent_portrayal, 30, 30, 750, 750)

# Create the server, and pass the grid and the graph
server = ModularServer(Traffic,
                       [grid],
                       "Traffic Model",
                       {})
