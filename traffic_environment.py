from pybrain.rl.environments.environment import Environment
from scipy import zeros

class TrafficEnvironment(Environment):

    # the number of action values the environment accepts
    indim = 2

    # the number of sensor values the environment produces
    outdim = 350

    delay_ns = 0
    delay_we = 0
    phase_time = 0
    west_east = 1
    set_west_east = True

    def getSensors(self):
        """ the currently visible state of the world (the    observation may be stochastic - repeated calls returning different values)
            :rtype: by default, this is assumed to be a numpy array of doubles
        """
        obs = zeros(4)
        obs[0] = float(self.delay_ns)
        obs[1] = float(self.delay_we)
        obs[2] = float(self.phase_time)
        obs[3] = float(self.west_east)
        return obs

    def setSensorValues(self, d_ns, d_we, p_t, w_e):
        #Discretisize the continuous values
        #NS
        if d_ns < 200:
            self.delay_ns = 0
        elif d_ns < 400:
            self.delay_ns = 200
        elif d_ns < 600:
            self.delay_ns = 400
        elif d_ns < 800:
            self.delay_ns = 600
        else:
            self.delay_ns = 800

        #WE
        if d_we < 200:
            self.delay_we = 0
        elif d_we < 400:
            self.delay_we = 200
        elif d_we < 600:
            self.delay_we = 400
        elif d_we < 800:
            self.delay_we = 600
        else:
            self.delay_we = 800

        #Time
        if p_t < 10:
            self.phase_time = 0
        elif p_t < 20:
            self.phase_time = 10
        elif p_t < 30:
            self.phase_time = 20
        elif p_t < 40:
            self.phase_time = 30
        elif p_t < 50:
            self.phase_time = 40
        elif p_t < 60:
            self.phase_time = 50
        else:
            self.phase_time = 60

        if w_e:
            self.west_east = 1
        else:
            self.west_east = 0


    def performAction(self, action):
        """ perform an action on the world that changes it's internal state (maybe stochastically).
            :key action: an action that should be executed in the Environment.
            :type action: by default, this is assumed to be a numpy array of doubles
        """
        if action[0] == 0:
            self.set_west_east = False
        else:
            self.set_west_east = True

    def reset(self):
        """ Most environments will implement this optional method that allows for reinitialization.
        """
