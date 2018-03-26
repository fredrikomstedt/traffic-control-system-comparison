import os, sys
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Please declare environment variable 'SUMO_HOME'")
import traci

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
