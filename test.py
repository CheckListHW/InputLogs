import numpy as np
from matplotlib import pyplot as plt

if __name__ == '__main__':
    series1_start = np.array([3])
    series1_end = np.array([3])
    series2_start = np.array([1])
    series2_end = np.array([1])
    series3_start = np.array([2])
    series3_end = np.array([2])

    index = np.arange(1)
    plt.axis([-0.5, 3.5, 0, 15])
    plt.title('A Multiseries Stacked Bar Chart')
    plt.bar(index, series1_start, color='r', bottom=series1_end)
    plt.bar(index, series2_start, color='b', bottom=series2_end)
    plt.bar(index, series3_start, color='g', bottom=series3_end)
    plt.xticks(index, ['0'])
    plt.show()
