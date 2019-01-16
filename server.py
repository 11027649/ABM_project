from mesa.space import ContinuousSpace
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule
# from HistogramModule import HistogramModule
from SimpleContinuousModule import SimpleCanvas
from model import Traffic
from agent import Car, Pedestrian, Road, Light

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

    portrayal = {"Shape": "circle" if type(agent) is Road else "circle",
                 "Color": "Blue" if type(agent) is Pedestrian
                 else "Grey" if type(agent) is Road
                 else current_color if type(agent) is Light
                 else "Pink",

                 "Filled": "true",
                 # draw road on layer 0 and everything else on 1
                 "Layer": 0 if type(agent) is Road else 1,
                 "w": 10,
                 "h": 10,
                 "r": 10}
    return portrayal

# Create a grid of 20 by 20 cells, and display it as 500 by 500 pixels
space = SimpleCanvas(agent_portrayal, 750, 750)

import numpy as np
from mesa.visualization.ModularVisualization import VisualizationElement

class HistogramModule(VisualizationElement):
    package_includes = ["Chart.min.js"]
    local_includes = ["HistogramModule.js"]

    def __init__(self, bins, canvas_height, canvas_width):
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width
        self.bins = bins
        new_element = "new HistogramModule({}, {}, {})"
        new_element = new_element.format(bins,
                                         canvas_width,
                                         canvas_height)
        self.js_code = "elements.push(" + new_element + ");"

    def render(self, model):
        print(model.time_list)
        hist = np.histogram(model.time_list, bins=self.bins)[0]
        print(hist)
        return [int(x) for x in hist]

# Create a dynamic linegraph
# chart = ChartModule([{"Label": "Time spend passing the conjunction (by cars)",
#                       "Color": "green"}],
#                     data_collector_name='datacollector')
histogram = HistogramModule(list(range(100)), 100, 100)

# Create the server, and pass the grid and the graph
server = ModularServer(Traffic,
                       [space, histogram],
                       "Traffic Model",
                       {})
