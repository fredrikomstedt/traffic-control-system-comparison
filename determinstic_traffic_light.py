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

    green_timer = 0
    green_time = GREEN_TIME
    second_green_time = 0

    west_east = True

    calculated_values = False
    switched = False

    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()

        if calculated_values:
            if yellow:
                yellow_timer += 1
                if yellow_timer > YELLOW_TIME:
                    yellow_timer = 0
                    yellow = False

                    #Switch lights
                    if west_east and not switched:
                        #During this iteration, WE has already been green
                        traci.trafficlight.setRedYellowGreenState("intersection", NS_GREEN_STATE)
                        green_time = min(second_green_time, GREEN_TIME)
                        west_east = False
                        switched = True
                    elif not switched:
                        #During this iteration, NS has already been green
                        traci.trafficlight.setRedYellowGreenState("intersection", WE_GREEN_STATE)
                        green_time = min(second_green_time, GREEN_TIME)
                        west_east = True
                        switched = True
                    else:
                        switched = False
                        calculated_values = False
            else:
                if green_timer < green_time:
                    green_timer += 1
                else:
                    green_timer = 0
                    yellow = True
                    if west_east:
                        traci.trafficlight.setRedYellowGreenState("intersection", WE_YELLOW_STATE)
                    else:
                        traci.trafficlight.setRedYellowGreenState("intersection", NS_YELLOW_STATE)
        else:
            density["west"], time["west"] = traffic_analyzer.getDensityAndTimeOnEdge("west_right")
            density["north"], time["north"] = traffic_analyzer.getDensityAndTimeOnEdge("north_down")
            density["east"], time["east"] = traffic_analyzer.getDensityAndTimeOnEdge("east_left")
            density["south"], time["south"] = traffic_analyzer.getDensityAndTimeOnEdge("south_up")
            calculated_values = True

            #Determine order of lights
            max_density = 0
            max_density_edge = "west"
            for edge in density:
                if density[edge] > max_density:
                    max_density = density[edge]
                    max_density_edge = edge
            if edge is "west" or edge is "east":
                west_east = True
                green_time = min(max(time["west"], time["east"]), GREEN_TIME)
                second_green_time = max(time["north"], time["south"])
                traci.trafficlight.setRedYellowGreenState("intersection", WE_GREEN_STATE)
            else:
                west_east = False
                green_time = min(max(time["north"], time["south"]), GREEN_TIME)
                second_green_time = max(time["west"], time["east"])
                traci.trafficlight.setRedYellowGreenState("intersection", NS_GREEN_STATE)
            calculated_values = True


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
