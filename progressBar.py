# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# This file is part of the ABM simulation made by (insert team name here)
#
# It contains a function that can print a progress bar.
# 
# source: https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


def printProgressBar (iteration, total, prefix = 'Progress', suffix = 'Complete',
        decimals = 1, length = 30, fill = '█'):
    """ Call in a loop to create terminal progress. By calling this function, you
        need to give two parameters: iteration, which is the current iteration, and
        total, which is the total amount of iterations. """

    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength - 1)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete
    if iteration == total:
        print()
