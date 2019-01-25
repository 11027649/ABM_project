##############################
# This is a class to gather and store data from a model run.
#############################

import csv
import datetime
import os

class Data():
    def __init__(self):
        self.generate_filepaths()
        self.generate_headers()

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

    def generate_headers(self):
        with open(self.filepath_spent_time, 'w', newline='') as csvfile:
            datawriter = csv.writer(csvfile)

            datawriter.writerow(['# This is a generated file to store info about the model'])
            datawriter.writerow(['# This header might contain more information if we actually changing parameters'])
            datawriter.writerow(['agent_type', 'unique_id', 'time_spent'])

        with open(self.filepath_info, 'w', newline='') as csvfile:
            datawriter = csv.writer(csvfile)

            datawriter.writerow(['# This is a generated file to store info about the model'])
            datawriter.writerow(['# This header might contain more information if we actually changing parameters'])
            datawriter.writerow(['time_step', 'pedestrian_count', 'car_count'])

    def write_row_hist(self, agent_type, agent_id, time_spent):
        with open(self.filepath_spent_time, 'a', newline='') as csvfile:
            datawriter = csv.writer(csvfile)

            datawriter.writerow([agent_type, agent_id, time_spent])


    def write_end_line(self):
        with open(self.filepath_spent_time, 'a', newline='') as csvfile:
            datawriter = csv.writer(csvfile)

            datawriter.writerow(["# Next iteration"])


    def write_info(self, datacollector_data):
        # datacollector_data is a pandas dataframe so
        datacollector_data.to_csv(path_or_buf=self.filepath_info, mode='a', header=False)

        with open(self.filepath_info, 'a', newline='') as datafile:
            datawriter = csv.writer(datafile)
            datawriter.writerow(["# Next iteration"])
