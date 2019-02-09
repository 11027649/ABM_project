from server import server
from mesa import Model
from model import Traffic
import time
from data import Data
from progressBar import printProgressBar
from SALib.sample import saltelli
import csv
import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd 
from copy import copy
from scipy import stats

"""
Runs a sobol sensitivity analysis, writing the mean flowing rate per simulation in an SA_...csv file
"""

# Number of steps per simulation
steps = 5000


# Number of runs will be:
# distrinct_samples*(number of params*2+2)*replicates
distinct_samples = 25
replicates = 1

# strategy = "Free"
# strategy = "Simultaneous"
strategy = "Reactive"

total_time = 0
# parameter bounds
bounds = [[.2, .8], # crossing_mean
          [20,60], # max_peds
          [2,6],# vision range in meters
          [.01, .3]] # stoch var

# We define our variables and bounds
problem = {
    'num_vars': len(bounds),
    'names': ["crossing_mean", "max_peds", "vision_range",
        "stoch_variable"],
    'bounds': bounds
}

# File names
filepath_spent_time = "data/SA_hist" + strategy+ ".csv"
filepath_info = "data/SA_info" + strategy + ".csv"
# Set headers for the datafile
headers = ["run"] + problem["names"] + ["strategy", "mean"]
output_file_name = "SA_" + strategy +"_"+ datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".csv"
# If file does not yet exist, write columnheaders first 
with open(output_file_name, "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(headers)

# Create the sample set
param_values = saltelli.sample(problem, distinct_samples)

count = 0
# Vals is one sample with values for each of the parameters

for vals in param_values:
    # Create dictionary to give as input to model
    param_dict = {}
    for i in range(len(problem['names'])):
        # Set N as integer
        if problem['names'][i] == "max_peds":
            param_dict[problem['names'][i]] = int(vals[i])
            vals[i] = int(vals[i])
        else:
            param_dict[problem['names'][i]] = vals[i]
    param_dict["strategy"] = strategy
    print(param_dict)

    # Replicate this experiment 'replicates' times
    for i in range(replicates):
        # Initialize data
        results = Data()
        results.SA = True
        results.filepath_info = filepath_info
        results.filepath_spent_time = filepath_spent_time

        # Run model with these parameters
        t0 = time.time()
        model = Traffic()
        model.set_parameters(**param_dict)
        model.run_model(steps, results)
        print("\nEnd time of this run: ", time.time() - t0)
        print('count', count)

        # Get mean
        df = pd.read_csv(filepath_info, header=4)
        mean = df[df['iteration'] == 0]['pedestrians_left'].mean()
        print(mean)

        # Write data to SA file
        # vals correct?
        values_row = [count] + list(vals) + [strategy, mean]
        # Write values_row
        with open(output_file_name, "a", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(values_row)

        count += 1


        
print("It took me", total_time, "s to run your model", replicates, "times with", steps, "steps")
print("Terminated normally! Find your data in the data folder. Have fun with it! ;-)")
