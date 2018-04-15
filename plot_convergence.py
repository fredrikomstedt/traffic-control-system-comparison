import matplotlib.pyplot as plt
import numpy as np
import math

def plotData(file):
    data = np.zeros([1200, 2])
    with open(file, 'r') as results:
        i = 0
        for result in results:
            result = eval(result)
            data[i][0] = i
            data[i][1] = result[3]
            i += 1
    l, = plt.plot(data[:,0], data[:,1], 'g', label='Convergence')
    plt.legend(handles=[l])
    plt.xlabel('Iteration')
    plt.ylabel('Average squared waiting time')
    plt.show()

if __name__ == '__main__':
    plotData('uniform/q_uniform_convergence_results.txt')
