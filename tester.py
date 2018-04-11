from generate_routefile import *
import trivial_traffic_light as trivial
import deterministic_traffic_light as deterministic
import learning_traffic_light as learning
import argparse

LEARNING_RUNS = 5

def run_tests(d, t, g):
    demand = (d+1)*1./20
    wait = 0
    wait_squared = 0

    #Generate vehicles
    if g:
        print("Generating file...")
        generate_routefile(demand)

    if t == 0:
        #Trivial with GREEN_TIME 20
        print("Demand: " + str(demand*100) + "%/s, trivial 20")
        wait, wait_squared = trivial.run(20)
    elif t == 1:
        #Trivial with GREEN_TIME 30
        print("Demand: " + str(demand*100) + "%/s, trivial 30")
        wait, wait_squared = trivial.run(30)
    elif t == 2:
        #Trivial with GREEN_TIME 40
        print("Demand: " + str(demand*100) + "%/s, trivial 40")
        wait, wait_squared = trivial.run(40)
    elif t == 3:
        #Deterministic
        print("Demand: " + str(demand*100) + "%/s, deterministic")
        wait, wait_squared = deterministic.run()
    elif t == 4:
        #Learning
        print("Demand: " + str(demand*100) + "%/s, learning")
        wait, wait_squared = learning.run(False)

    with open('results.txt', 'a') as results_file:
        results_file.write(str((t, demand, wait, wait_squared)) + '\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Used to run tests for various traffic light algorithms.')
    parser.add_argument('demand', help='The demand of traffic, either 0, 1, 2 or 3.')
    parser.add_argument('type', help='The type of algorithm to be used, either 0, 1, 2, 3 or 4.')
    parser.add_argument('--generate_file', help="If used, new routefile will be generated.", action='store_true')

    #Extract parsed arguments
    args = parser.parse_args()
    d = int(args.demand)
    t = int(args.type)
    g = args.generate_file

    run_tests(d, t, g)
