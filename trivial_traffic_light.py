import os, sys
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Please declare environment variable 'SUMO_HOME'")
from sumolib import checkBinary
import traci

def run_algorithm():
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()

    traci.close()
    sys.stdout.flush()

if __name__ == '__main__':
    #Get the binary for SUMO
    sumoBinary = checkBinary('sumo-gui')

    #Connect to SUMO via TraCI
    traci.start([sumoBinary, "-c", "intersection.sumocfg"])

    run_algorithm()
