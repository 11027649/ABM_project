from server import server
from mesa import Model
from model import Traffic

import matplotlib.pyplot as plt
#
# print("Do you want to launch the server for visualization? (Type yes/no)")
# choiche = input()
#
# if choiche == "yes":
    # launch at default port
server.port = 8522
server.launch()
# else:
#     print("How many steps?")
#     steps = int(input())
#     model = Traffic()
#     times = model.run_model(steps)
#     print(times)
#     # plt.hist(times)
#     # plt.show()
