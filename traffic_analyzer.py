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

density = {}
class DensityListener(traci.StepListener):
    def step(self, t=0):
        density["west"] = getNumberOfVehiclesOnEdge("west_right")
        density["north"] = getNumberOfVehiclesOnEdge("north_down")
        density["east"] = getNumberOfVehiclesOnEdge("east_left")
        density["south"] = getNumberOfVehiclesOnEdge("south_up")

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

def getVehiclesOnLanes(vehicles):
    vehiclesOnLanes = {}

    #Get the amount of vehicles on each lane
    for vehicle in vehicles:
        lane = traci.vehicle.getLaneIndex(vehicle)
        if not lane in vehiclesOnLanes:
            vehiclesOnLanes[lane] = []
        vehiclesOnLanes[lane].append(vehicle)
    return vehiclesOnLanes

def getTimeNeededToEnterIntersectionOnEdge(edge):
    #Get the vehicles from a road
    vehicles = traci.edge.getLastStepVehicleIDs(edge)
    if len(vehicles) == 0:
        return 0
    vehiclesOnLanes = getVehiclesOnLanes(vehicles)

    #Intersection position
    intersection_position = traci.junction.getPosition("intersection")

    #Get the max time
    max_time = 0
    for lane in vehiclesOnLanes:
        #Find largest distance from lane
        max_distance = 0
        max_distance_vehicle = ""
        for vehicle in vehiclesOnLanes[lane]:
            position = traci.vehicle.getPosition(vehicle)
            distance = sqrt((intersection_position[0] - position[0])**2 +
                            (intersection_position[1] - position[1])**2)
            if distance > max_distance:
                max_distance = distance
                max_distance_vehicle = vehicle

        #Calculate time
        #Assume 0.5 seconds for each vehicle to get started
        vehicle_startup_time = 0.5
        time = vehicle_startup_time*len(vehiclesOnLanes[lane])

        #A delay occurs if the vehicles travel left (as they have to
        #wait for cars from the opposite side of the intersection)
        #This is assumed to be .1 second per vehicle from the opposite
        #side
        if traci.vehicle.getLaneIndex(max_distance_vehicle) == 1:
            #determine edge:
            opposite_edge = ""
            if "west" in edge:
                opposite_edge = "east_left"
            elif "east" in edge:
                opposite_edge = "west_right"
            elif "north" in edge:
                opposite_edge = "south_up"
            else:
                opposite_edge = "north_down"

            #Get vehicles on lanes
            opposite_vehicles = traci.edge.getLastStepVehicleIDs(opposite_edge)
            opposite_vehiclesOnLanes = getVehiclesOnLanes(opposite_vehicles)

            #Get amount of vehicles on conflicting lane
            vehicle_amount_opposite_lane = 0
            for lane in opposite_vehiclesOnLanes:
                if traci.vehicle.getLaneIndex(opposite_vehiclesOnLanes[lane][0]) == 0:
                    vehicle_amount_opposite_lane = len(opposite_vehiclesOnLanes[lane])
                    break
            time += vehicle_amount_opposite_lane*0.1

        #PQ-formula to find time needed from acceleration and speed to get
        #to the middle of the intersection.
        acceleration = traci.vehicle.getAccel(max_distance_vehicle)/2 #Assume linear increase
        velocity = traci.vehicle.getSpeed(max_distance_vehicle)
        time += -velocity/acceleration + sqrt((velocity/acceleration)**2 +
                                                2*max_distance/acceleration)
        if time > max_time:
            max_time = time
    return max_time

def getDensityAndTimeOnEdge(edge):
    return getNumberOfVehiclesOnEdge(edge), getTimeNeededToEnterIntersectionOnEdge(edge)
