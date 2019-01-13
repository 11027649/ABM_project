from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule

from model import Traffic
from agent import Car, Pedestrian, RandomWalker

# You can change this to whatever you want. Make sure to make the different types
# of agents distinguishable
def agent_portrayal(agent):
    portrayal = {"Shape": "circle",
                 "Color": "blue" if type(agent) is Pedestrian else "green",
                 "Filled": "true",
                 "Layer": 0,
                 "r": 0.5}
    return portrayal

# Create a grid of 20 by 20 cells, and display it as 500 by 500 pixels
grid = CanvasGrid(agent_portrayal, 20, 20, 500, 500)

# Create the server, and pass the grid and the graph
server = ModularServer(Traffic,
                       [grid],
                       "Traffic Model",
                       {})
