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

def sensorValues(q_w, q_n, q_e, q_s, p_t):
    queue_w = 0
    queue_n = 0
    queue_e = 0
    queue_s = 0
    phase_time = 0
    #Discretisize the continuous values
    #N
    if q_n < 4:
        queue_n = 0
    elif q_n < 8:
        queue_n = 1
    elif q_n < 12:
        queue_n = 2
    elif q_n < 16:
        queue_n = 3
    elif q_n < 20:
        queue_n = 4
    else:
        queue_n = 5

    #E
    if q_e < 4:
        queue_e = 0
    elif q_e < 8:
        queue_e = 1
    elif q_e < 12:
        queue_e = 2
    elif q_e < 16:
        queue_e = 3
    elif q_e < 20:
        queue_e = 4
    else:
        queue_e = 5

    #S
    if q_s < 4:
        queue_s = 0
    elif q_s < 8:
        queue_s = 1
    elif q_s < 12:
        queue_s = 2
    elif q_s < 16:
        queue_s = 3
    elif q_s < 20:
        queue_s = 4
    else:
        queue_s = 5

    #W
    if q_w < 4:
        queue_w = 0
    elif q_w < 8:
        queue_w = 1
    elif q_w < 12:
        queue_w = 2
    elif q_w < 16:
        queue_w = 3
    elif q_w < 20:
        queue_w = 4
    else:
        queue_w = 5

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

    return queue_w, queue_n, queue_e, queue_s, phase_time

def run_algorithm(not_trained):
    wait_listener = traffic_analyzer.WaitingTimeListener()
    traci.addStepListener(wait_listener)
    delayListener = traffic_analyzer.DelayListener()
    traci.addStepListener(delayListener)
    queueListener = traffic_analyzer.QueueListener()
    traci.addStepListener(queueListener)

    #Reinforcement Learning
    Q = np.zeros([6, 6, 6, 6, 7, 2])
    try:
        Q = np.load('q.npy')
        print("Q matrix loaded")
    except:
        pass
    # Set learning parameters
    lr = .0001
    y = .01
    #

    switched = False

    yellow = False
    yellow_time = 0

    green_time = 0
    green_time_at_switch = 0

    west_east = True
    traci.trafficlight.setRedYellowGreenState("intersection", WE_GREEN_STATE)

    state = [0, 0, 0, 0, 0]
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
                #Reinforcement learning

                #Get state
                q_w, q_n, q_e, q_s, p_t = sensorValues(traffic_analyzer.queue_lengths["west"], traffic_analyzer.queue_lengths["north"], traffic_analyzer.queue_lengths["east"], traffic_analyzer.queue_lengths["south"], green_time)
                state = [q_w, q_n, q_e, q_s, p_t]

                #Get reward
                waiting_times = traffic_analyzer.getDelay()
                r = waiting_times - previous_waiting_times
                previous_waiting_times = waiting_times

                #Update Q-Table with new knowledge
                Q[previous_state[0], previous_state[1], previous_state[2], previous_state[3], previous_state[4], action] = Q[previous_state[0], previous_state[1], previous_state[2], previous_state[3], previous_state[4], action] + lr*(r + y*np.min(Q[state[0], state[1], state[2], state[3], state[4],:]) - Q[previous_state[0], previous_state[1], previous_state[2], previous_state[3], previous_state[4], action])

                #Get action and execute it
                explore = 0.1
                if not_trained:
                    explore += (7800 - step)/7800
                if explore > 1:
                    explore = 1
                action = None
                if random.uniform(0, 1) > explore:
                    action = np.argmin(Q[state[0], state[1], state[2], state[3], state[4],:])
                else:
                    action = random.randint(0, 1)
                if action == 1 and not west_east:
                    switched = True
                    GREEN_TIME = green_time + 10
                elif action == 0 and west_east:
                    switched = True
                    GREEN_TIME = green_time + 10
                previous_state = state

                green_time += 1
            elif switched:
                if green_time < GREEN_TIME:
                    green_time += 1
                else:
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

    if not_trained:
        print("Training...")
    return run_algorithm(not_trained)

if __name__ == '__main__':
    run(True)
