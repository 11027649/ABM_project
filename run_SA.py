from server import server
from mesa import Model
from model import Traffic
import time
from data import Data
from progressBar import printProgressBar
from SALib.sample import saltelli

import matplotlib.pyplot as plt

total_time = 0
steps = 13000

# Set the repetitions, the amount of steps, and the amount of distinct values per variable
replicates = 5
distinct_samples = 10
# parameter bounds
bounds = [[120, 220], # vision_angle, smaller?
          [2,30], #N, smaller?
          [2,6],# vision range in meters
          [.1, 1.5],# Ek
          [.1, 1.5], #Ok
          [.1, 1.5], #Pk
          [.1, 1.5], #Ak
          [.1, 1.5], #Ik
          [.1,.16], #speed mean
          [.03, .04], # speeds sd,
          [.8, 2.2], # gamma
          [4, 7], # max density
          [.2, .8], # crossing mean
          [.05, .25], #crossing sd
          [10,60], #max peds
          [1,8], #max_cars
          [.001, .05], #spawn rate car
          [.001, .2], #spawn rate peds
          [.01, .3], #stoch variable
          [.6, 1.2]] # max car speed

# We define our variables and bounds
problem = {
    'num_vars': len(bounds),
    'names': ["vision_angle", "N", "vision_range",
        "Ek_w", "Ok_w", "Pk_w", "Ak_w", "Ik_w",
        "speed_mean", "speed_sd", "gamma", "max_density",
        "crossing_mean", "crossing_sd", "max_peds", "max_cars", "spawn_rate_car", "spawn_rate_pedes"],
    'bounds': bounds
}

# Indices of the parameters that should be integers
ints = [1, 14, 15]

# Create the sample set
param_values = saltelli.sample(problem, distinct_samples)

count = 0
# Vals is one sample with values for each of the parameters
count_val = 0
for vals in param_values: 
    t0 = time.time()
    results = Data()

    # Change parameters that should be integers
    vals = list(vals)
    for i in ints:
        vals[i] = int(vals[i])

    # Replicate this experiment 'replicates' times
    for i in range(replicates):
        # TODO: add parameter for SA count
        # SOMETHING WITH THE MODEL THAT LETS US GET A DF
        # CONSISTING OF ROWS WITH THE PARAMETER VALUES FROM VALS
        # AND THE 5 OUTPUT RESULTS
        # Run model with these parameters
        model = Traffic()
        model.set_parameters(*vals)
        model.run_model(steps, results)
    
    count_val += 1
    total_time += time.time() - t0 

count += 1


print("It took me", total_time, "s to run your model", replicates, "times with", steps, "steps")
print("Terminated normally! Find your data in the data folder. Have fun with it! ;-)")
