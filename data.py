##############################
# This is a class to gather and store data from a model run.
#############################

import csv
import datetime
import os

class Data():
    def __init__(self):
        self.generate_filepaths()
        self.iteration = 0

    def generate_filepaths(self):
        """
        Generate a filepath for the file that will be used to save the data self.
        Also generates a header for the file.
        """

        date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # if directory doesn't exist, create one
        if not os.path.exists("data/"):
            os.makedirs("data")


        self.filepath_spent_time = "data/hist_" + str(date) + ".csv"
        self.filepath_info = "data/info_" + str(date) + ".csv"

    def generate_headers(self, strategy, iterations, crowdedness):
        with open(self.filepath_spent_time, 'w', newline='') as csvfile:
            datawriter = csv.writer(csvfile)

            datawriter.writerow(['# This is a generated file to store info about the model'])
            datawriter.writerow(['# Light strategy: ' + strategy])
            datawriter.writerow(['# Timesteps of each simulation: ' + str(iterations)])
            datawriter.writerow(['# Crowdedness: ' + crowdedness])
            datawriter.writerow(['iteration', 'agent_type', 'unique_id', 'time_spent'])

        with open(self.filepath_info, 'w', newline='') as csvfile:
            datawriter = csv.writer(csvfile)

            datawriter.writerow(['# This is a generated file to store info about the model'])
            datawriter.writerow(['# Light strategy: ' + strategy])
            datawriter.writerow(['# Timesteps of each simulation: ' + str(iterations)])
            datawriter.writerow(['# Crowdedness: ' + crowdedness])
            datawriter.writerow(['iteration', 'pedestrian_count', 'car_count', 'mid_section_count', 'pedestrians_left', 'cars_left'])

    def write_row_hist(self, agent_type, agent_id, time_spent):
        with open(self.filepath_spent_time, 'a', newline='') as csvfile:
            datawriter = csv.writer(csvfile)
            datawriter.writerow([self.iteration, agent_type, agent_id, time_spent])

    def write_row_info(self, pedestrian_count, car_count, mid_section_count, pedestrians_left, cars_left):
        with open(self.filepath_info, 'a', newline='') as datafile:
            datawriter = csv.writer(datafile)
            datawriter.writerow([self.iteration, pedestrian_count, car_count, mid_section_count, pedestrians_left, cars_left])

    def next_iteration(self):
        self.iteration += 1
