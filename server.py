from mesa.space import ContinuousSpace
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule
from HistogramModule import HistogramModule
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

    portrayal = {"Shape": "circle" if type(agent) is Car else "circle",
                 "Color": "Blue" if type(agent) is Pedestrian
                 else current_color if type(agent) is Light
                 else "Pink",
                 "Filled": "true",
                 "w": 10,
                 "h": 10,
                 "r": 17 if type(agent) is Car else 2}
    return portrayal

# Create a grid of 20 by 20 cells, and display it as 500 by 500 pixels
space = SimpleCanvas(agent_portrayal)

# Create a dynamic histogram
histogram = HistogramModule(list(range(10)))
# chart = ChartModule([{"Label": "Cars and Pedestrians",
#                       "Color": "green"}],
#                       data_collector_name='datacollector')

# Create the server, and pass the grid and the graph
server = ModularServer(Traffic,
                       [space, histogram],
                       "Traffic Model",
                       {})
