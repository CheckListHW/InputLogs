import numpy as np
from matplotlib import pyplot as plt

from Model.map import Map

if __name__ == '__main__':
    fig = plt.figure()
    ax = fig.add_subplot(111)
    data_map = Map()
    data_map.load_map('C:/Users/KosachevIV/PycharmProjects/InputData/lay_name133.json')

    names = set(name for z, name in data_map.get_column(13, 12))
    for name, color in zip(names, ['r', 'b', 'g', 'y']):
        value = [z for z, data_name in data_map.get_column(13, 12) if name == data_name]
        print(value)
        for v in value:
            plt.bar(np.arange(1), 1, color=color, bottom=v)

    plt.show()
