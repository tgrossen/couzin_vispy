import threading, math
from math import pi
import numpy as np
from random import randint
from copy import deepcopy
from Fish import Fish

class World():
    def __init__(self, canvasWidth, canvasHeight, unit):
        self.WORLD = []
        self.canvasWidth = canvasWidth
        self.canvasHeight = canvasHeight
        self.unit = unit
        self.fishes = []
    
    def addFish(self, x, y, angle, log=False, speed=1, identifier=None):
        fishy_fish = Fish(self, x, y, angle, log=log, speed=speed)
        self.fishes.append(fishy_fish)
    
    def dotproduct(self, v1, v2):
        return sum((a*b) for a, b in zip(v1, v2))
    
    def length(self, v):
        return math.sqrt(self.dotproduct(v, v))
    
    def angle_from_origin(self, x, y):
        v1 = [1,0]
        v2 = [x,y]
        try:
            ang = math.acos(self.dotproduct(v1, v2) / (self.length(v1) * self.length(v2)))
        except ZeroDivisionError:
            ang = 0
        if v2[1] < 0:
            return (pi*2) - ang
        else:
            return ang
    
    def get_distance(self, a_x, a_y, b_x, b_y):
        return math.pow(((a_x-b_x)*(a_x-b_x) + (a_y-b_y)*(a_y-b_y)),.5)
    
    def get_close_fishes(self, fish):
        p1_x = int(fish.x_position)
        p1_y = int(fish.y_position)
        p3_x = math.cos(fish.angle)+p1_x
        p3_y = math.sin(fish.angle)+p1_y
        x_min = p1_x-(self.unit*fish.zone_attraction)
        x_max = p1_x+(self.unit*fish.zone_attraction)
        y_min = p1_y-(self.unit*fish.zone_attraction)
        y_max = p1_y+(self.unit*fish.zone_attraction)

        fish.potentials = []
        fish.potentials = filter(lambda other_fish: other_fish.identifier != fish.identifier and
            int(other_fish.x_position) in range(x_min, x_max) and
            int(other_fish.y_position) in range(y_min, y_max), self.fishes)
        remove = []
        for other_fish in fish.potentials:
            p2_x = other_fish.x_position
            p2_y = other_fish.y_position
            distance = self.get_distance(p2_x, p2_y, fish.x_position, fish.y_position)
            if not distance <= (self.unit*fish.zone_attraction):
                if fish.log:
                    print str(fish.identifier) + ": remove: " + str(other_fish.identifier)
                remove.append(other_fish.identifier)
            # perception test
            elif fish.field_perception == 360:
                continue
            else:
                d12 = self.get_distance(p1_x, p1_y, p2_x, p2_y)
                d13 = self.get_distance(p1_x, p1_y, p3_x, p3_y)
                d23 = self.get_distance(p2_x, p2_y, p3_x, p3_y)
                try:
                    num = (d12*d12 + d13*d13 - d23*d23)/(2 * d12 * d13)
                    if num > 1.0:
                        angle = 0
                    elif num < -1.0:
                        angle = pi
                    else:
                        angle = math.acos(num)
                except ZeroDivisionError:
                    angle = 0
                if angle > math.radians(fish.field_perception/2):
                    remove.append(other_fish.identifier)
        fish.potentials = filter(lambda f: f.identifier not in remove, fish.potentials)
        return fish.potentials
    
    def init_world(self):
        self.WORLD = [[0 for x in range(self.canvasHeight)] for x in range(self.canvasWidth)]

