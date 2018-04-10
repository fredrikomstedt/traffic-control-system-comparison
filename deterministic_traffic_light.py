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
    listener = traffic_analyzer.WaitingTimeListener()
    traci.addStepListener(listener)

    #Density for all incoming roads
    density = {}
    density["west"] = 0
    density["north"] = 0
    density["east"] = 0
    density["south"] = 0

    #Time needed for cars on incoming roads to pass through
    time = {}
    time["west"] = 0
    time["north"] = 0
    time["east"] = 0
    time["south"] = 0

    yellow = False
    yellow_timer = 0

    green_timer = GREEN_TIME
    green_time = GREEN_TIME

    max_density = 0
    max_density_edge = "west"

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

        #Switching between roads
        if yellow:
            if yellow_timer < YELLOW_TIME:
                yellow_timer += 1
            else:
                yellow_timer = 0
                yellow = False
                if max_density_edge == "west" or max_density_edge == "east":
                    traci.trafficlight.setRedYellowGreenState("intersection", WE_GREEN_STATE)
                else:
                    traci.trafficlight.setRedYellowGreenState("intersection", NS_GREEN_STATE)
        #Light is green
        elif green_timer < green_time:
            green_timer += 1
        #Determine which road that should get green light
        else:
            green_timer = 0

            #Set current green road's values to 0
            if max_density_edge == "west" or max_density_edge == "east":
                density["west"] = 0
                density["east"] = 0
                time["west"] = 0
                time["east"] = 0
            else:
                density["north"] = 0
                density["south"] = 0
                time["north"] = 0
                time["south"] = 0

            previous_edge = max_density_edge
            max_density = 0

            #Get highest density
            for edge in density:
                if density[edge] > max_density:
                    max_density = density[edge]
                    max_density_edge = edge

            #All roads have been taken, recalculate values
            if max_density == 0:
                density["west"], time["west"] = traffic_analyzer.getDensityAndTimeOnEdge("west_right")
                density["north"], time["north"] = traffic_analyzer.getDensityAndTimeOnEdge("north_down")
                density["east"], time["east"] = traffic_analyzer.getDensityAndTimeOnEdge("east_left")
                density["south"], time["south"] = traffic_analyzer.getDensityAndTimeOnEdge("south_up")

                #Get highest density, again
                for edge in density:
                    if density[edge] > max_density:
                        max_density = density[edge]
                        max_density_edge = edge

            if max_density_edge == "west" or max_density_edge == "east":
                green_time = min(max(time["west"], time["east"]), GREEN_TIME)
                if previous_edge != "west" and previous_edge != "east":
                    yellow = True
                    traci.trafficlight.setRedYellowGreenState("intersection", NS_YELLOW_STATE)
            else:
                green_time = min(max(time["north"], time["south"]), GREEN_TIME)
                if previous_edge != "north" and previous_edge != "south":
                    yellow = True
                    traci.trafficlight.setRedYellowGreenState("intersection", WE_YELLOW_STATE)


    waiting_time = traffic_analyzer.getWaitingTimes() - waiting_time
    waiting_time2 = traffic_analyzer.getSquaredWaitingTimes() - waiting_time2
    vehicle_amount = traffic_analyzer.getVehicleAmount() - vehicle_amount
    print("Average waiting time: " + str(float(waiting_time) / vehicle_amount))
    print("Average squared waiting time: " + str(float(waiting_time2) / vehicle_amount))
    traci.close()
    sys.stdout.flush()
    traffic_analyzer.reset()
    return float(waiting_time) / vehicle_amount, float(waiting_time2) / vehicle_amount

def run():
    #Get the binary for SUMO
    sumoBinary = checkBinary('sumo')

    #Connect to SUMO via TraCI
    traci.start([sumoBinary, "-c", "intersection.sumocfg", "--waiting-time-memory", "1000"])

    return run_algorithm()

if __name__ == '__main__':
    run()
