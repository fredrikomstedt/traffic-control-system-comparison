import os, sys
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Please declare environment variable 'SUMO_HOME'")
from sumolib import checkBinary
import traci
import traffic_analyzer

YELLOW_TIME = 3
GREEN_TIME = 60
NS_GREEN_STATE = "GGgrrrGGgrrr"
NS_YELLOW_STATE = "YYyrrrYYyrrr"
WE_GREEN_STATE = "rrrGGgrrrGGg"
WE_YELLOW_STATE = "rrrYYyrrrYYy"

def run_algorithm():
    wait_listener = traffic_analyzer.WaitingTimeListener()
    traci.addStepListener(wait_listener)
    density_listener = traffic_analyzer.DensityListener()
    traci.addStepListener(density_listener)

    switched = False

    yellow = False
    yellow_time = 0

    green_time = 0
    green_time_at_switch = 0

    west_east = True

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
                #TODO: Reinforcement learning
            elif switched:
                if green_time < green_time_at_switch + 10:
                    green_time += 1
                else:
                    green_time = 0
                    switched = False
                    yellow = True
                    if west_east:
                        traci.trafficlight.setRedYellowGreenState("intersection", WE_YELLOW_STATE)
                    else:
                        traci.trafficlight.setRedYellowGreenState("intersection", NS_YELLOW_STATE)



    print("Average waiting time: " + str(traffic_analyzer.getAverageWaitingTime()))
    print("Average squared waiting time: " + str(traffic_analyzer.getAverageSquaredWaitingTime()))
    traci.close()
    sys.stdout.flush()

if __name__ == '__main__':
    #Get the binary for SUMO
    sumoBinary = checkBinary('sumo-gui')

    #Connect to SUMO via TraCI
    traci.start([sumoBinary, "-c", "intersection.sumocfg", "--waiting-time-memory", "1000"])

    run_algorithm()
