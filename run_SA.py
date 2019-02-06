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


total_time = 0
steps = 1000

strategy = "Free"
# strategy = "Simultaneous"
# strategy = "Reactive"

max_peds = 10        
# max_peds = 20        
# max_peds = 30        
# max_peds = 40        

# Set the repetitions, the amount of steps, and the amount of distinct values per variable
replicates = 2
distinct_samples = 3
# parameter bounds
bounds = [[.2, .8], # crossing_mean
          [2,30], #N
          [2,6],# vision range in meters
          [.01, .3]] # stoch var

# File names
filepath_spent_time = "data/SA_hist" + strategy+ ".csv"
filepath_info = "data/SA_info" + strategy + ".csv"

# We define our variables and bounds
problem = {
    'num_vars': len(bounds),
    'names': ["crossing_mean", "N", "vision_range",
        "stoch_variable"],
    'bounds': bounds
}

# Set headers for the datafile
# TODO: add data headers
headers = ["run"] + problem["names"] + ["strategy", "max_peds", "mean"]
output_file_name = "SA_" + strategy +"_"+ datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".csv"
# If file does not yet exist, write columnheaders first 
with open(output_file_name, "w") as f:
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
        if problem['names'][i] == "N":
            param_dict[problem['names'][i]] = int(vals[i])
        else:
            param_dict[problem['names'][i]] = vals[i]
    print(param_dict)
    print(vals)

    # Replicate this experiment 'replicates' times
    for i in range(replicates):
        # TODO: add parameter for SA count
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

        # Get mean
        df = pd.read_csv(filepath_info, header=4)
        mean = df[df['iteration'] == 0]['pedestrians_left'].mean()

        # Write data to SA file
        # vals correct?
        values_row = [count] + list(vals) + [strategy, max_peds, mean]
        print(values_row)
        # Write values_row
        with open(output_file_name, "a", newline='') as f:
            writer = csv.writer(f)
            print(values_row)
            writer.writerow(values_row)

        count += 1


        
print("It took me", total_time, "s to run your model", replicates, "times with", steps, "steps")
print("Terminated normally! Find your data in the data folder. Have fun with it! ;-)")
