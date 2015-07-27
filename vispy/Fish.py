import threading, math
from math import pi
from random import randint

class Fish():
    def __init__(self, world, x, y, angle):
        self.x_position=x
        self.y_position=y
        self.angle=angle
        self.zone_repulsion=1
        self.zone_orientation=7
        self.zone_attraction=15
        self.field_perception=200
        self.turning_rate=150
        self.speed=27
        self.time_step=0.1
        self.is_running=False
        self.world=world
        self.identifier="fish" + str(randint(0,1000000))
        #self.start()
    def _run(self):
        self.is_running=False
        self.start()
        self.move()
    def start(self):
        if not self.is_running:
            self._timer = threading.Timer(self.time_step, self._run)
            self._timer.start()
            self.is_running = True
    def stop(self):
        if hasattr(self, '_timer'):
            self._timer.cancel()
        self.is_running = False
    def increase_angle(self):
        self.angle += self.turning_rate*self.time_step
        if self.angle > 360:
            self.angle -= 360
    def decrease_angle(self):
        self.angle -= self.turning_rate*self.time_step
        if self.angle < 0:
            self.angle += 360
    def get_distance(self, a_x, a_y, b_x, b_y):
        return math.pow(((a_x-b_x)*(a_x-b_x) + (a_y-b_y)*(a_y-b_y)),.5)
    def evaluate_and_turn(self):
        zones = self.zone_check()
        goal_angle = self.angle
        if len(zones['repulse']):
            goal_angle = self.repulse(zones['repulse'])
        elif len(zones['orient']):
            if len(zones['attract']):
                goal_angle = 0.5 * (self.orient(zones['orient']) + self.attract(zones['attract']))
            else:
                goal_angle = self.orient(zones['orient'])
        elif len(zones['attract']):
            goal_angle = self.attract(zones['attract'])
        if goal_angle != self.angle:
            if abs(goal_angle - self.angle) <= self.turning_rate*self.time_step or (360 - abs(goal_angle - self.angle)) <= self.turning_rate*self.time_step:
                self.angle = goal_angle
            elif goal_angle > self.angle:
                if goal_angle - self.angle > 180:
                    self.decrease_angle()
                else:
                    self.increase_angle()
            elif goal_angle < self.angle:
                if goal_angle - self.angle > 180:
                    self.increase_angle()
                else:
                    self.decrease_angle()
        if self.angle >= 360:
            self.angle -= 360
    def move_forward(self):
        move_vector = self.speed*self.time_step
        eval_angle = math.radians(self.angle)
        if eval_angle == 0:
            self.x_position += move_vector
        elif eval_angle > 0 and eval_angle < pi/2:
            self.x_position += math.cos(eval_angle)*move_vector
            self.y_position += math.sin(eval_angle)*move_vector
        elif eval_angle == pi/2:
            self.y_position += move_vector
        elif eval_angle > pi/2 and eval_angle < pi:
            eval_angle = pi - eval_angle
            self.x_position -= math.cos(eval_angle)*move_vector
            self.y_position += math.sin(eval_angle)*move_vector
        elif eval_angle == pi:
            self.x_position -= move_vector
        elif eval_angle > pi and eval_angle < 3*pi/2:
            eval_angle -= pi
            self.x_position -= math.cos(eval_angle)*move_vector
            self.y_position -= math.sin(eval_angle)*move_vector
        elif eval_angle == 3*pi/2:
            self.y_position -= move_vector
        elif eval_angle > 3*pi/2:
            eval_angle = 2*pi - eval_angle
            self.x_position += math.cos(eval_angle)*move_vector
            self.y_position -= math.sin(eval_angle)*move_vector
        # handle edge of map
        if self.x_position < 0:
            self.x_position += self.world.canvasWidth
        elif self.x_position >= self.world.canvasWidth:
            self.x_position -= self.world.canvasWidth
        if self.y_position < 0:
            self.y_position += self.world.canvasHeight
        elif self.y_position >= self.world.canvasHeight:
            self.y_position -= self.world.canvasHeight
    def move(self):
        #threading.Timer(self.time_step, move, args=self).start()
        self.evaluate_and_turn()
        self.move_forward()
        self.world.WORLD[int(self.x_position)][int(self.y_position)] = 0
        self.world.WORLD[int(self.x_position)][int(self.y_position)] = [self.x_position, self.y_position, self.angle, self.identifier]
    def repulse(self, fishes):
        sum_x, sum_y = self.unit_vector_sum(fishes)
        sum_x *= -1
        sum_y *= -1
        return self.world.angle_from_origin(sum_x, sum_y)
    def attract(self, fishes):
        sum_x, sum_y = self.unit_vector_sum(fishes)
        return self.world.angle_from_origin(sum_x, sum_y)
    def orient(self, fishes):
        angles = []
        for fish in fishes:
            angles.append(float(fish.angle))
        return sum(angles) / len(angles)
    def unit_vector_sum(self, fishes):
        sum_x = 0
        sum_y = 0
        for fish in fishes:
            diff_x = self.x_position - fish.x_position
            diff_y = self.y_position - fish.y_position
            norm = self.get_distance(diff_x, diff_y, 0, 0)
            try:
                sum_x += diff_x/norm
            except ZeroDivisionError:
                sum_x = 0
            try:
                sum_y += diff_y/norm
            except ZeroDivisionError:
                sum_y = 0
        return sum_x, sum_y
    def zone_check(self):
        potentials = self.world.get_close_fishes(self)
        zones = {}
        zones['repulse'] = []
        zones['orient'] = []
        zones['attract'] = []
        for p in potentials:
            distance = self.get_distance(self.x_position, self.y_position, p.x_position, p.y_position)
            if distance <= self.world.unit*self.zone_repulsion:
                zones['repulse'].append(p)
            elif distance <= self.world.unit*self.zone_orientation:
                zones['orient'].append(p)
            elif distance <= self.world.unit*self.zone_attraction:
                zones['attract'].append(p)
        return zones

# def monitor(fish, fish2, fish3):
#     fish_x = 0
#     fish_y = 0
#     while True:
#         if fish_x != fish.x_position or fish_y != fish.y_position:
#             fish_x = fish.x_position
#             fish_y = fish.y_position
#             print fish_x, fish_y, fish.angle
#             print fish2.x_position, fish2.y_position, fish2.angle
#             print fish3.x_position, fish3.y_position, fish3.angle
#             print ""