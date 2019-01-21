##############################
# This is a class to gather and store data from a model run.
#############################

import csv
import datetime
import os

class Data():
    def __init__(self, filepath):
        self.filepath = filepath

    def generate_filepath():
        """
        Generate a filepath for the file that will be used to save the dataself.
        """

        date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")

        # if directory doesn't exist, create one
        if not os.path.exits("./data/"):
            os.makedirs("data")

    def generate_header():

        with open(self.filepath, 'w', newline='') as csvfile:
            datawriter = csv.writer(csvfile)

            datawriter.write("# This is a generated file to store info about the model")
            datawriter.write("# If we're doing parameters, this header might contain more information")
