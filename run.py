from server import server
from mesa import Model
from model import Traffic
import time
from data import Data

import matplotlib.pyplot as plt

print("Do you want to launch the server for visualization? (Type yes/no)")
choiche = input()
# choiche = "yes"

if choiche == "yes":
    # launch at default port
    server.port = 8522
    server.launch()
else:
    print('How many iterations?')
    iterations = int(input())
    print("How many steps?")
    steps = int(input())
    print("Okay then, running your model now...")

    results = Data()
    t0 = time.time()

    for i in range(iterations):
        # printProgressBar(i, iterations)
        model = Traffic()
        model.run_model(steps, results)
        simulation_info = model.datacollector.get_model_vars_dataframe()

        results.write_info(simulation_info)

    print(time.time() - t0)
    print("Terminated normally! Have fun with your data ;-)")
