import os, sys
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Please declare environment variable 'SUMO_HOME'")
import traci

from math import sqrt

class WaitingTimeListener(traci.StepListener):
    def step(self, t=0):
        addWaitingTimes("west_left")
        addWaitingTimes("north_up")
        addWaitingTimes("east_right")
        addWaitingTimes("south_down")

vehicles_checked = {}

def addWaitingTimes(edge):
    #Get the vehicles from the last step on the lane
    vehicles = traci.edge.getLastStepVehicleIDs(edge)
    for vehicle in vehicles:
        if not vehicle in vehicles_checked:
            vehicles_checked[vehicle] = traci.vehicle.getAccumulatedWaitingTime(vehicle)

def getAverageWaitingTime():
    time_sum = 0
    vehicle_amount = 0
    for vehicle in vehicles_checked:
        vehicle_amount += 1
        time_sum += vehicles_checked[vehicle]
    return float(time_sum)/vehicle_amount

def getAverageSquaredWaitingTime():
    time_sum = 0
    vehicle_amount = 0
    for vehicle in vehicles_checked:
        vehicle_amount += 1
        time = vehicles_checked[vehicle]
        time_sum += time**2
    return float(time_sum)/vehicle_amount

def getNumberOfVehiclesOnEdge(edge):
    vehicles = traci.edge.getLastStepVehicleIDs(edge)
    return len(vehicles)

def getTimeNeededToEnterIntersectionOnEdge(edge):
    #Get the vehicles from a road
    vehicles = traci.edge.getLastStepVehicleIDs(edge)
    if len(vehicles) == 0:
        return 0
    vehiclesOnLanes = {}

    #Get the amount of vehicles on each lane
    for vehicle in vehicles:
        lane = traci.vehicle.getLaneIndex(vehicle)
        if not lane in vehiclesOnLanes:
            vehiclesOnLanes[lane] = 0
        vehiclesOnLanes[lane] += 1

    #Find lane with most vehicles
    max_number_of_vehicles_on_lane = 0
    max_lane = ""
    for lane in vehiclesOnLanes:
        if vehiclesOnLanes[lane] > max_number_of_vehicles_on_lane:
            max_number_of_vehicles_on_lane = vehiclesOnLanes[lane]
            max_lane = lane

    #Intersection position
    intersection_position = traci.junction.getPosition("intersection")

    #Find largest distance from max lane
    max_distance = 0
    max_distance_vehicle = ""
    for vehicle in vehicles:
        if traci.vehicle.getLaneIndex(vehicle) is max_lane:
            position = traci.vehicle.getPosition(vehicle)
            distance = sqrt((intersection_position[0] - position[0])**2 +
                            (intersection_position[1] - position[1])**2)
            if distance > max_distance:
                max_distance = distance
                max_distance_vehicle = vehicle

    #Calculate time
    #Assume 0.5 seconds for each vehicle to get started
    vehicle_startup_time = 0.5
    time = vehicle_startup_time*max_number_of_vehicles_on_lane

    #PQ-formula to find time needed from acceleration and speed to get
    #to the middle of the intersection.
    acceleration = traci.vehicle.getAccel(max_distance_vehicle)/2 #Assume linear increase
    velocity = traci.vehicle.getSpeed(max_distance_vehicle)
    time += -velocity/acceleration + sqrt((velocity/acceleration)**2 +
                                            2*max_distance/acceleration)
    return time

def getDensityAndTimeOnEdge(edge):
    return getNumberOfVehiclesOnEdge(edge), getTimeNeededToEnterIntersectionOnEdge(edge)
