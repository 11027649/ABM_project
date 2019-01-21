##############################
# This is a class to gather and store data from a model run.
#############################

import csv
import datetime
import os

class Data():
    def __init__(self):
        self.generate_filepath()

    def generate_filepath(self):
        """
        Generate a filepath for the file that will be used to save the data self.
        Also generates a header for the file.
        """

        date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")

        # if directory doesn't exist, create one
        if not os.path.exists("./data/"):
            os.makedirs("data")

        self.filepath = str(date) + ".csv"

        with open("data/" + self.filepath, 'w', newline='') as csvfile:
            datawriter = csv.writer(csvfile)

            datawriter.writerow(['# This is a generated file to store info about the model'])
            datawriter.writerow(['# This header might contain more information if we actually changing parameters'])
            datawriter.writerow(['agent_type', 'unique_id', 'time_spent'])

    def write_row(self, agent_type, agent_id, time_spent):
        with open("data/" + self.filepath, 'a', newline='') as csvfile:
            datawriter = csv.writer(csvfile)

            datawriter.writerow([agent_type, agent_id, time_spent])
