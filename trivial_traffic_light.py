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
GREEN_TIME = 30
NS_GREEN_STATE = "GGgrrrGGgrrr"
NS_YELLOW_STATE = "YYyrrrYYyrrr"
WE_GREEN_STATE = "rrrGGgrrrGGg"
WE_YELLOW_STATE = "rrrYYyrrrYYy"

def run_algorithm(gt):
    GREEN_TIME = gt
    green = 0
    yellow = 0
    west_east = True
    yellow_phase = False
    listener = traffic_analyzer.WaitingTimeListener()
    traci.addStepListener(listener)
    step = 0

    waiting_time = 0
    waiting_time2 = 0
    vehicle_amount = 0

    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        step += 1

        if step == 10800:
            waiting_time = traffic_analyzer.getWaitingTimes()
            waiting_time2 = traffic_analyzer.getSquaredWaitingTimes()
            vehicle_amount = traffic_analyzer.getVehicleAmount()

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


    waiting_time = traffic_analyzer.getWaitingTimes() - waiting_time
    waiting_time2 = traffic_analyzer.getSquaredWaitingTimes() - waiting_time2
    vehicle_amount = traffic_analyzer.getVehicleAmount() - vehicle_amount
    print("Average waiting time: " + str(float(waiting_time) / vehicle_amount))
    print("Average squared waiting time: " + str(float(waiting_time2) / vehicle_amount))
    traci.close()
    sys.stdout.flush()
    traffic_analyzer.reset()
    return float(waiting_time) / vehicle_amount, float(waiting_time2) / vehicle_amount

def run(gt):
    #Get the binary for SUMO
    sumoBinary = checkBinary('sumo')

    #Connect to SUMO via TraCI
    traci.start([sumoBinary, "-c", "intersection.sumocfg", "--waiting-time-memory", "1000"])

    return run_algorithm(gt)

if __name__ == '__main__':
    run(30)
