from server import server
from mesa import Model
from model import Traffic
import time
from data import Data
from progressBar import printProgressBar

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
    total_time = 0

    for i in range(iterations):
        print("Run number:", i)

        model = Traffic()
        model.run_model(steps, results)
        simulation_info = model.datacollector.get_model_vars_dataframe()

        results.write_info(simulation_info)
        print("\nEnd time of this run: ", time.time() - t0)
        total_time += t0

    print("It took me", total_time, "s to run your model", iterations, "times with", steps, "steps")
    print("Terminated normally! Find your data in the data folder. Have fun with it! ;-)")
