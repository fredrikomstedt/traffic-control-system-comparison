import os, sys
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Please declare environment variable 'SUMO_HOME'")
from sumolib import checkBinary
import traci

YELLOW_TIME = 3
GREEN_TIME = 30
NS_GREEN_STATE = "GGgrrrGGgrrr"
NS_YELLOW_STATE = "YYyrrrYYyrrr"
WE_GREEN_STATE = "rrrGGgrrrGGg"
WE_YELLOW_STATE = "rrrYYyrrrYYy"

def run_algorithm():
    green = 0
    yellow = 0
    west_east = True
    yellow_phase = False
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()

        #Increment time for the different phases
        if yellow_phase:
            yellow += 1
            #Time maximized, switch state
            if yellow > YELLOW_TIME:
                yellow = 0
                yellow_phase = False
                if west_east:
                    traci.trafficlight.setRedYellowGreenState("intersection", NS_GREEN_STATE)
                    west_east = False
                else:
                    traci.trafficlight.setRedYellowGreenState("intersection", WE_GREEN_STATE)
                    west_east = True
        else:
            green += 1
            #Time maximized, switch state
            if green > GREEN_TIME:
                green = 0
                yellow_phase = True
                if west_east:
                    traci.trafficlight.setRedYellowGreenState("intersection", WE_YELLOW_STATE)
                else:
                    traci.trafficlight.setRedYellowGreenState("intersection", NS_YELLOW_STATE)

    traci.close()
    sys.stdout.flush()

if __name__ == '__main__':
    #Get the binary for SUMO
    sumoBinary = checkBinary('sumo-gui')

    #Connect to SUMO via TraCI
    traci.start([sumoBinary, "-c", "intersection.sumocfg"])

    run_algorithm()
