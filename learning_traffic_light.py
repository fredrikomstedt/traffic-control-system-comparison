import os, sys
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Please declare environment variable 'SUMO_HOME'")
from sumolib import checkBinary
import traci
import traffic_analyzer

#Reinforcement learning
from traffic_task import TrafficTask
from traffic_environment import TrafficEnvironment
from pybrain.rl.learners.valuebased import ActionValueTable
from pybrain.rl.agents import LearningAgent
from pybrain.rl.learners import Q
from pybrain.rl.experiments.continuous import Experiment
from pybrain.rl.explorers import EpsilonGreedyExplorer
import numpy as np


YELLOW_TIME = 4
GREEN_TIME = 60
NS_GREEN_STATE = "GGgrrrGGgrrr"
NS_YELLOW_STATE = "YYyrrrYYyrrr"
WE_GREEN_STATE = "rrrGGgrrrGGg"
WE_YELLOW_STATE = "rrrYYyrrrYYy"

def run_algorithm():
    wait_listener = traffic_analyzer.WaitingTimeListener()
    traci.addStepListener(wait_listener)
    delayListener = traffic_analyzer.DelayListener()
    traci.addStepListener(delayListener)

    #Reinforcement Learning
    action_value_table = ActionValueTable(350, 2)
    action_value_table.initialize(0.)
    learner = Q()
    agent = LearningAgent(action_value_table, learner)

    environment = TrafficEnvironment()
    task = TrafficTask(environment)
    experiment = Experiment(task, agent)

    prev_reward = -traffic_analyzer.getAverageSquaredWaitingTimes()
    #

    switched = False

    yellow = False
    yellow_time = 0

    green_time = 0
    green_time_at_switch = 0

    west_east = True
    traci.trafficlight.setRedYellowGreenState("intersection", WE_GREEN_STATE)

    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()

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
                        reward = -traffic_analyzer.getAverageSquaredWaitingTimes()
                        task.setReward(reward - prev_reward)
                        prev_reward = reward
                        environment.setSensorValues(traffic_analyzer.delay["north_south"], traffic_analyzer.delay["west_east"], green_time, west_east)
                        experiment.doInteractions(1)
                        agent.learn()
                        agent.reset()
                        if environment.set_west_east != west_east:
                            switched = True

                    else:
                        green_time += 1
            elif switched:
                green_time = 0
                switched = False
                yellow = True
                if west_east:
                    traci.trafficlight.setRedYellowGreenState("intersection", WE_YELLOW_STATE)
                else:
                    traci.trafficlight.setRedYellowGreenState("intersection", NS_YELLOW_STATE)



    print("Average waiting time: " + str(traffic_analyzer.getAverageWaitingTimes()))
    print("Average squared waiting time: " + str(traffic_analyzer.getAverageSquaredWaitingTimes()))
    traci.close()
    sys.stdout.flush()

if __name__ == '__main__':
    #Get the binary for SUMO
    sumoBinary = checkBinary('sumo-gui')

    #Connect to SUMO via TraCI
    traci.start([sumoBinary, "-c", "intersection.sumocfg", "--waiting-time-memory", "1000"])

    run_algorithm()
