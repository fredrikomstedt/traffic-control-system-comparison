import os, sys
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Please declare environment variable 'SUMO_HOME'")
from sumolib import checkBinary
import traci
import traffic_analyzer
import random

#Reinforcement learning
import numpy as np


YELLOW_TIME = 4
GREEN_TIME = 60
NS_GREEN_STATE = "GGgrrrGGgrrr"
NS_YELLOW_STATE = "YYyrrrYYyrrr"
WE_GREEN_STATE = "rrrGGgrrrGGg"
WE_YELLOW_STATE = "rrrYYyrrrYYy"

def sensorValues(d_ns, d_we, p_t, w_e):
    delay_ns = 0
    delay_we = 0
    phase_time = 0
    we = 0
    #Discretisize the continuous values
    #NS
    if d_ns < 2000:
        delay_ns = 0
    elif d_ns < 4000:
        delay_ns = 1
    elif d_ns < 6000:
        delay_ns = 2
    elif d_ns < 8000:
        delay_ns = 3
    else:
        delay_ns = 4

    #WE
    if d_we < 2000:
        delay_we = 0
    elif d_we < 4000:
        delay_we = 1
    elif d_we < 6000:
        delay_we = 2
    elif d_we < 8000:
        delay_we = 3
    else:
        delay_we = 4

    #Time
    if p_t < 10:
        phase_time = 0
    elif p_t < 20:
        phase_time = 1
    elif p_t < 30:
        phase_time = 2
    elif p_t < 40:
        phase_time = 3
    elif p_t < 50:
        phase_time = 4
    elif p_t < 60:
        phase_time = 5
    else:
        phase_time = 6

    if w_e:
        we = 1
    else:
        we = 0
    return delay_ns, delay_we, phase_time, we

def run_algorithm(not_trained):
    wait_listener = traffic_analyzer.WaitingTimeListener()
    traci.addStepListener(wait_listener)
    delayListener = traffic_analyzer.DelayListener()
    traci.addStepListener(delayListener)

    #Reinforcement Learning
    Q = np.zeros([5, 5, 7, 2, 2])
    try:
        Q = np.load('q.npy')
        print("Q matrix loaded")
    except:
        pass
    # Set learning parameters
    lr = .8
    y = .95
    #

    switched = False

    yellow = False
    yellow_time = 0

    green_time = 0
    green_time_at_switch = 0

    west_east = True
    traci.trafficlight.setRedYellowGreenState("intersection", WE_GREEN_STATE)

    state = [0, 0, 0, 1]
    previous_state = state
    action = 0
    previous_waiting_times = 0

    step = 0

    waiting_time = 0
    waiting_time2 = 0
    vehicle_amount = 0
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        step += 1

        if step == 600:
            waiting_time = traffic_analyzer.getWaitingTimes()
            waiting_time2 = traffic_analyzer.getSquaredWaitingTimes()
            vehicle_amount = traffic_analyzer.getVehicleAmount()

        if yellow:
            if yellow_time < YELLOW_TIME:
                yellow_time += 1
            else:
                yellow_time = 0
                yellow = False
                if west_east:
                    west_east = False
                    traci.trafficlight.setRedYellowGreenState("intersection", NS_GREEN_STATE)
                else:
                    west_east = True
                    traci.trafficlight.setRedYellowGreenState("intersection", WE_GREEN_STATE)
        else:
            if green_time < 10:
                green_time += 1
            elif not switched:
                if green_time >= GREEN_TIME:
                    switched = True
                else:
                    if green_time % 10 == 0:
                        #Reinforcement learning

                        #Get state
                        d_ns, d_we, p_t, w_e = sensorValues(traffic_analyzer.delay["north_south"], traffic_analyzer.delay["west_east"], green_time, west_east)
                        state = [d_ns, d_we, p_t, w_e]

                        #Get reward
                        waiting_times = traffic_analyzer.getSquaredWaitingTimes()
                        if waiting_times < previous_waiting_times:
                            waiting_times = previous_waiting_times
                        r = waiting_times - previous_waiting_times
                        previous_waiting_times = waiting_times

                        #Update Q-Table with new knowledge
                        Q[previous_state[0], previous_state[1], previous_state[2], previous_state[3], action] = Q[previous_state[0], previous_state[1], previous_state[2], previous_state[3], action] + lr*(r + y*np.min(Q[state[0], state[1], state[2], state[3],:]) - Q[previous_state[0], previous_state[1], previous_state[2], previous_state[3], action])

                        #Get action and execute it
                        explore = 0.1
                        if not_trained:
                            explore += (14400 - step)/14400
                        if explore > 1:
                            explore = 1
                        action = None
                        if random.uniform(0, 1) > explore:
                            action = np.argmin(Q[state[0], state[1], state[2], state[3],:])
                        else:
                            action = random.randint(0, 1)
                        if action == 1 and not west_east:
                            switched = True
                        elif action == 0 and west_east:
                            switched = True
                        previous_state = state

                    green_time += 1
            elif switched:
                green_time = 0
                switched = False
                yellow = True
                if west_east:
                    traci.trafficlight.setRedYellowGreenState("intersection", WE_YELLOW_STATE)
                else:
                    traci.trafficlight.setRedYellowGreenState("intersection", NS_YELLOW_STATE)


    waiting_time = traffic_analyzer.getWaitingTimes() - waiting_time
    waiting_time2 = traffic_analyzer.getSquaredWaitingTimes() - waiting_time2
    vehicle_amount = traffic_analyzer.getVehicleAmount() - vehicle_amount
    np.save('q.npy', Q)
    print("Q matrix stored")
    print("Average waiting time: " + str(float(waiting_time) / vehicle_amount))
    print("Average squared waiting time: " + str(float(waiting_time2) / vehicle_amount))
    traci.close()
    sys.stdout.flush()
    traffic_analyzer.reset()
    return float(waiting_time) / vehicle_amount, float(waiting_time2) / vehicle_amount

def run(not_trained):
    #Get the binary for SUMO
    sumoBinary = checkBinary('sumo')

    #Connect to SUMO via TraCI
    traci.start([sumoBinary, "-c", "intersection.sumocfg", "--waiting-time-memory", "1000"])

    return run_algorithm(not_trained)

if __name__ == '__main__':
    run(True)
