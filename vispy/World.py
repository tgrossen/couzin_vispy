import threading, math
from math import pi
import numpy as np
from random import randint
from Fish import Fish

class World():
    def __init__(self, canvasWidth, canvasHeight, unit):
        self.WORLD = []
        self.canvasWidth = canvasWidth
        self.canvasHeight = canvasHeight
        self.unit = unit
        self.fishes = []
    def setAndGo(self):
        self.init_world()
        self.addFish()
    def add_fish_swarm(self, count):
        startX = 200
        startY = 200
        for x in range(0, count):
            self.addFish(startX + randint(-count,count), startY + randint(-count,count), randint(0, 360))
    def add_random_fishes(self, count):
        for x in range(0, count):
            self.addFish(randint(0, self.canvasWidth), randint(0, self.canvasHeight), randint(0, 360))
    def addFish(self, x, y, angle):
        fishy_fish = Fish(self, x, y, angle)
        #fishy_fish.start()
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
        # if len(self.fishes) == 1:
        #     return []
        p1_x = int(fish.x_position)
        p1_y = int(fish.y_position)
        p3_x = math.cos(fish.angle)+p1_x
        p3_y = math.sin(fish.angle)+p1_y
        x_min = p1_x-(self.unit*fish.zone_attraction)
        x_max = p1_x+(self.unit*fish.zone_attraction)
        y_min = p1_y-(self.unit*fish.zone_attraction)
        y_max = p1_y+(self.unit*fish.zone_attraction)

        potentials = []
        potentials = filter(lambda other_fish: other_fish.identifier != fish.identifier and
            int(other_fish.x_position) in range(x_min, x_max) and
            int(other_fish.y_position) in range(y_min, y_max), self.fishes)
        # bounding box test -> initial get
        # for x in range(p1_x-(self.unit*fish.zone_attraction), p1_x+(self.unit*fish.zone_attraction)):
        #     if x < 0 or x > self.canvasWidth:
        #         continue
        #     for y in range(p1_y-(self.unit*fish.zone_attraction), p1_y+(self.unit*fish.zone_attraction)):
        #         if y < 0 or y > self.canvasHeight:
        #             continue
        #         #print str(x) + " " + str(y)
        #         if x in range(0, self.canvasWidth) and y in range(0, self.canvasHeight):
        #             if self.WORLD[x][y] != 0 and self.WORLD[x][y][3] != fish.identifier:
        #                 print "OH MY GOSH"
        #                 print "x:{x} y:{y} p1_x:{p1_x} p1_y:{p1_y}".format(x=x, y=y, p1_x=p1_x, p1_y=p1_y)
        #                 potentials.append(self.WORLD[x][y])
        # circle test
        for other_fish in potentials:
            p2_x = other_fish.x_position
            p2_y = other_fish.y_position
            distance = self.get_distance(p2_x, p2_y, fish.x_position, fish.y_position)
            if not distance <= (self.unit*fish.zone_attraction):
                potentials.remove(other_fish)
            # perception test
            else:
                d12 = self.get_distance(p1_x, p1_y, p2_x, p2_y)
                d13 = self.get_distance(p1_x, p1_y, p3_x, p3_y)
                d23 = self.get_distance(p2_x, p2_y, p3_x, p3_y)
                try:
                    angle = math.acos((d12*d12 + d13*d13 - d23*d23)/(2 * d12 * d13))
                except ZeroDivisionError:
                    angle = 0
                # field of perception is in both directions, so we make sure angle smaller than half the field of perception
                if angle > math.radians(fish.field_perception/2):
                    potentials.remove(other_fish)
                #else:
                #    print angle
        return potentials
    def init_world(self):
        self.WORLD = [[0 for x in range(self.canvasHeight)] for x in range(self.canvasWidth)]