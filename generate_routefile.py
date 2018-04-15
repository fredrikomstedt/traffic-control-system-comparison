# Generates a routefile for a SUMO simulation with a random
# amount of vehicles traversing the network in a random fashion.

# Code modified from runner.py found in the traci_tls tutorial from the SUMO software.
# Written by Fredrik Omstedt and Erik Björck.

import random
#random.seed(1337) #Make tests reproducible

def generate_vehicle(road):
    vehType = random.randint(0, 3)
    vehRoute = random.randint(0, 2) + road
    vehColorRed = random.randint(0, 1)
    vehColorGreen = random.randint(0, 1)
    vehColorBlue = random.randint(0, 1)
    if vehColorRed == 0 and vehColorGreen == 0 and vehColorBlue == 0:
        vehColorRed = 1
    return vehType, vehRoute, vehColorRed, vehColorGreen, vehColorBlue

def generate_routefile(d, variable):
    N = 7800 #Number of time steps

    if variable:
        print("Variable demand.")

    #Demand per second from any direction
    demand = d

    #Generate the route file
    with open("intersection.rou.xml", "w") as routes:
        print(
            """
            <routes>
                <vType id="0" accel="2" decel="4.5" sigma="0.5" length="5" minGap="2.5" maxSpeed="14" guiShape="passenger"/>
                <vType id="1" accel="2" decel="4.5" sigma="0.5" length="3" minGap="2.5" maxSpeed="14" guiShape="passenger"/>
                <vType id="2" accel="2" decel="4.5" sigma="0.5" length="4" minGap="2.5" maxSpeed="14" guiShape="passenger"/>
                <vType id="3" accel="2" decel="4.5" sigma="0.5" length="10" minGap="3" maxSpeed="14" guiShape="bus"/>

                <route id="0" edges="west_right north_up" />
                <route id="1" edges="west_right east_right" />
                <route id="2" edges="west_right south_down" />

                <route id="3" edges="north_down east_right" />
                <route id="4" edges="north_down south_down" />
                <route id="5" edges="north_down west_left" />

                <route id="6" edges="east_left south_down" />
                <route id="7" edges="east_left west_left" />
                <route id="8" edges="east_left north_up" />

                <route id="9" edges="south_up west_left" />
                <route id="10" edges="south_up north_up" />
                <route id="11" edges="south_up east_right" />

            """
        , file=routes)
        vehNr = 0
        for i in range(N):
            if variable:
                if i >= 600:
                    x = i - 600
                    demand = 0.05 + 0.00008333333*x - 1.157407e-8*(x**2)

            #West
            if random.uniform(0, 1) < demand:
                vehType, vehRoute, vehCR, vehCG, vehCB = generate_vehicle(0)
                print('    <vehicle id="veh_%i" type="%i" route="%i" color="%f,%f,%f" depart="%i" />' % (vehNr, vehType, vehRoute, vehCR, vehCG, vehCB, i), file=routes)
                vehNr += 1

            #North
            if random.uniform(0, 1) < demand:
                vehType, vehRoute, vehCR, vehCG, vehCB = generate_vehicle(3)
                print('    <vehicle id="veh_%i" type="%i" route="%i" color="%f,%f,%f" depart="%i" />' % (vehNr, vehType, vehRoute, vehCR, vehCG, vehCB, i), file=routes)
                vehNr += 1

            #East
            if random.uniform(0, 1) < demand:
                vehType, vehRoute, vehCR, vehCG, vehCB = generate_vehicle(6)
                print('    <vehicle id="veh_%i" type="%i" route="%i" color="%f,%f,%f" depart="%i" />' % (vehNr, vehType, vehRoute, vehCR, vehCG, vehCB, i), file=routes)
                vehNr += 1

            #South
            if random.uniform(0, 1) < demand:
                vehType, vehRoute, vehCR, vehCG, vehCB = generate_vehicle(9)
                print('    <vehicle id="veh_%i" type="%i" route="%i" color="%f,%f,%f" depart="%i" />' % (vehNr, vehType, vehRoute, vehCR, vehCG, vehCB, i), file=routes)
                vehNr += 1

        print("</routes>", file=routes)



if __name__ == "__main__":
    generate_routefile(1./10, False)
