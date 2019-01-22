from mesa.visualization.ModularVisualization import VisualizationElement

class SimpleCanvas(VisualizationElement):
    local_includes = ["SimpleContinuousModule.js"]
    portrayal_method = None

    def __init__(self, portrayal_method):
        '''
        Instantiate a new SimpleCanvas
        '''
        self.portrayal_method = portrayal_method
        self.canvas_height = 750
        self.canvas_width = 1500
        new_element = ("new SimpleContinuousModule({}, {})".
                       format(self.canvas_width, self.canvas_height))
        self.js_code = "elements.push(" + new_element + ");"

    def render(self, model):
        space_state = []

        # draw pedestrians and cars
        for schedule in [model.schedule_Light.agents, model.schedule_Car.agents, model.schedule_Pedestrian.agents]:
            for obj in schedule:
                portrayal = self.portrayal_method(obj)
                x, y = obj.pos
                x = ((x - model.space.x_min) /
                     (model.space.x_max - model.space.x_min))
                y = ((y - model.space.y_min) /
                     (model.space.y_max - model.space.y_min))
                portrayal["x"] = x
                portrayal["y"] = y
                space_state.append(portrayal)

        # return the drawing
        return space_state
