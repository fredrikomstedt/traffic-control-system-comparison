from generate_routefile import *
import trivial_traffic_light as trivial
import deterministic_traffic_light as deterministic
import learning_traffic_light as learning

TEST_CASES = 100
LEARNING_RUNS = 20

def run_tests():
    for i in range(4):
        demand = (i+1)*1./20
        results = []
        trivial_20_wait = 0
        trivial_20_wait_squared = 0
        trivial_30_wait = 0
        trivial_30_wait_squared = 0
        trivial_40_wait = 0
        trivial_40_wait_squared = 0
        deterministic_wait = 0
        deterministic_wait_squared = 0
        learning_wait = 0
        learning_wait_squared = 0

        for _ in range(TEST_CASES):
            #Generate vehicles
            generate_routefile(demand)

            #Trivial with GREEN_TIME 20
            t_20_w, t_20_w2 = trivial.run(20)
            trivial_20_wait += t_20_w
            trivial_20_wait_squared += t_20_w2

            #Trivial with GREEN_TIME 30
            t_30_w, t_30_w2 = trivial.run(30)
            trivial_30_wait += t_30_w
            trivial_30_wait_squared += t_30_w2

            #Trivial with GREEN_TIME 40
            t_40_w, t_40_w2 = trivial.run(40)
            trivial_40_wait += t_40_w
            trivial_40_wait_squared += t_40_w2

            #Deterministic
            d_w, d_w2 = deterministic.run()
            deterministic_wait += d_w
            deterministic_wait_squared += d_w2

            #Learning
            learning_value, learning_value_squared = 0
            for _ in range(LEARNING_RUNS):
                l_v, l_v2 = learning.run()
                learning_value += l_v
                learning_value_squared += l_v2
            learning_wait += learning_value / LEARNING_RUNS
            learning_wait_squared += learning_value_squared / LEARNING_RUNS

        trivial_20_wait /= TEST_CASES
        trivial_20_wait_squared /= TEST_CASES
        trivial_30_wait /= TEST_CASES
        trivial_30_wait_squared /= TEST_CASES
        trivial_40_wait /= TEST_CASES
        trivial_40_wait_squared /= TEST_CASES
        deterministic_wait /= TEST_CASES
        deterministic_wait_squared /= TEST_CASES
        learning_wait /= TEST_CASES
        learning_wait_squared /= TEST_CASES

        results.add((0, demand, trivial_20_wait, trivial_20_wait_squared))
        results.add((1, demand, trivial_30_wait, trivial_30_wait_squared))
        results.add((2, demand, trivial_40_wait, trivial_40_wait_squared))
        results.add((3, demand, deterministic_wait, deterministic_wait_squared))
        results.add((4, demand, learning_wait, learning_wait_squared))
    with open('results.txt', 'w') as results_file:
        for result in results:
            print(result, results_file)

if __name__ == '__main__':
    run_tests()
