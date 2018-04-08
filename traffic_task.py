from scipy import clip, asarray

from pybrain.rl.environments.task import Task
from numpy import *

class TrafficTask(Task):
    reward = 0

    def __init__(self, environment):
        """ All tasks are coupled to an environment. """
        self.env = environment
        self.last_reward = 0

    def performAction(self, action):
        """ A filtered mapping towards performAction of the underlying environment. """
        self.env.performAction(action)

    def getObservation(self):
        """ A filtered mapping to getSample of the underlying environment. """
        sensors = self.env.getSensors()
        return sensors

    def getReward(self):
        """ Compute and return the current reward (i.e. corresponding to the last action performed) """
        current_reward = self.last_reward
        self.last_reward = self.reward
        return current_reward

    def setReward(self, r):
        self.reward = r

    @property
    def indim(self):
        return self.env.indim

    @property
    def outdim(self):
        return self.env.outdim
