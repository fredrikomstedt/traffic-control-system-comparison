import matplotlib.pyplot as plt
import numpy as np
import math

def getDataFromFile(file):
    data = np.zeros([4, 5])
    data_amount = np.zeros([4, 5])
    with open(file, 'r') as results:
        for result in results:
            result = eval(result)
            if math.isclose(result[1], 0.05, rel_tol=1e-5):
                data[0][result[0]] += result[3]
                data_amount[0][result[0]] += 1
            elif math.isclose(result[1], 0.1, rel_tol=1e-5):
                data[1][result[0]] += result[3]
                data_amount[1][result[0]] += 1
            elif math.isclose(result[1], 0.15, rel_tol=1e-5):
                data[2][result[0]] += result[3]
                data_amount[2][result[0]] += 1
            elif math.isclose(result[1], 0.2, rel_tol=1e-5):
                data[3][result[0]] += result[3]
                data_amount[3][result[0]] += 1
    for i in range(4):
        for j in range(5):
            data[i][j] /= data_amount[i][j]
    return data

def plotData(data):
    t_20, = plt.plot([0.05, 0.1, 0.15, 0.2], data[:,0], 'r', label='Trivial 20')
    plt.plot([0.05, 0.1, 0.15, 0.2], data[:,0], 'ro')
    t_30, = plt.plot([0.05, 0.1, 0.15, 0.2], data[:,1], 'b', label='Trivial 30')
    plt.plot([0.05, 0.1, 0.15, 0.2], data[:,1], 'bo')
    t_40, = plt.plot([0.05, 0.1, 0.15, 0.2], data[:,2], 'k', label='Trivial 40')
    plt.plot([0.05, 0.1, 0.15, 0.2], data[:,2], 'ko')
    d, = plt.plot([0.05, 0.1, 0.15, 0.2], data[:,3], 'y', label='Deterministic')
    plt.plot([0.05, 0.1, 0.15, 0.2], data[:,3], 'yo')
    l, = plt.plot([0.05, 0.1, 0.15, 0.2], data[:,4], 'g', label='Learning')
    plt.plot([0.05, 0.1, 0.15, 0.2], data[:,4], 'go')
    plt.legend(handles=[t_20, t_30, t_40, d, l])
    plt.axis([0.04, 0.21, 0, 7500])
    plt.xlabel('Demand per second')
    plt.ylabel('Average squared waiting time')
    plt.show()

if __name__ == '__main__':
    data = getDataFromFile('results.txt')
    plotData(data)
