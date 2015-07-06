import threading

class Fish():
    def __init__(self, WORLD, x, y, angle):
        self.x_position=x
        self.y_position=y
        self.angle=angle
        self.zone_repulsion=1
        self.zone_orientation=7
        self.zone_attraction=15
        self.field_perception=200
        self.turning_rate=50
        self.speed=3
        self.time_step=0.1
        self.is_running=False
        self.WORLD=WORLD.WORLD
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
    def evaluate_and_turn(self):
        zones = zone_check()
        goal_angle = self.angle
        if len(zones['repulse']):
            goal_angle = repulse(zones['repulse'])
        elif len(zones['orient']):
            if len(zones['attract']):
                goal_angle = 0.5 * (orient(zones['orient']) + attract(zones['attract']))
            else:
                goal_angle = orient(zones['orient'])
        elif len(zones['attract']):
            attract(zones['attract'])
        if goal_angle != self.angle:
            if abs(goal_angle - self.angle) <= self.turning_rate*self.time_step or (360 - abs(goal_angle - self.angle)) <= self.turning_rate*self.time_step:
                self.angle = goal_angle
            elif goal_angle > self.angle:
                if goal_angle - self.angle > 180:
                    decrease_angle()
                else:
                    increase_angle()
            elif goal_angle < self.angle:
                if goal_angle - self.angle > 180:
                    increase_angle()
                else:
                    decrease_angle()
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
    def move(self):
        global WORLD
        #threading.Timer(self.time_step, move, args=self).start()
        WORLD[int(self.x_position)][int(self.y_position)] = 0
        evaluate_and_turn()
        move_forward()
        WORLD[int(self.x_position)][int(self.y_position)] = [self.x_position, self.y_position, self.angle]
    def repulse(fishes):
        sum_x, sum_y = unit_vector_sum(fishes)
        sum_x *= -1
        sum_y *= -1
        return angle_from_origin(sum_x, sum_y)
    def attract(fishes):
        sum_x, sum_y = unit_vector_sum(fishes)
        return angle_from_origin(sum_x, sum_y)
    def orient(fishes):
        angles = []
        for fish in fishes:
            angles.append(float(fish[2]))
        return sum(angles) / len(angles)
    def unit_vector_sum(self, fishes):
        sum_x = 0
        sum_y = 0
        for fish in fishes:
            diff_x = self.x_position - fish[0]
            dif_y = self.y_position - fish[1]
            norm = get_distance(diff_x, diff_y, 0, 0)
            sum_x += diff_x/norm
            sum_y += diff_y/norm
        return sum_x, sum_y
    def zone_check(self):
        potentials = get_close_fishes(self)
        zones = {}
        zones['repulse'] = []
        zones['orient'] = []
        zones['attract'] = []
        for p in potentials:
            distance = get_distance(self.x_position, self.y_position, p[0], p[1])
            if distance <= unit*self.zone_repulsion:
                zones['repulse'].append(p)
            elif distance <= unit*self.zone_orientation:
                zones['orient'].append(p)
            elif distance <= unit*self.zone_attraction:
                zones['attract'].append(p)
        return zones