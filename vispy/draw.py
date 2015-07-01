from vispy import gloo, app
import threading, math
import numpy as np

WORLD = []
canvasWidth = 1024
canvasHeight = 768
unit = 9

VERT_SHADER = """
attribute vec2  a_position;
attribute vec3  a_color;
attribute float a_size;

varying vec4 v_fg_color;
varying vec4 v_bg_color;
varying float v_radius;
varying float v_linewidth;
varying float v_antialias;

void main (void) {
    v_radius = a_size;
    v_linewidth = 1.0;
    v_antialias = 1.0;
    v_fg_color  = vec4(0.0,0.0,0.0,0.5);
    v_bg_color  = vec4(a_color,    1.0);

    gl_Position = vec4(a_position, 0.0, 1.0);
    gl_PointSize = 2.0*(v_radius + v_linewidth + 1.5*v_antialias);
}
"""

FRAG_SHADER = """
#version 120

varying vec4 v_fg_color;
varying vec4 v_bg_color;
varying float v_radius;
varying float v_linewidth;
varying float v_antialias;
void main()
{
    float size = 2.0*(v_radius + v_linewidth + 1.5*v_antialias);
    float t = v_linewidth/2.0-v_antialias;
    float r = length((gl_PointCoord.xy - vec2(0.5,0.5))*size);
    float d = abs(r - v_radius) - t;
    if( d < 0.0 )
        gl_FragColor = v_fg_color;
    else
    {
        float alpha = d/v_antialias;
        alpha = exp(-alpha*alpha);
        if (r > v_radius)
            gl_FragColor = vec4(v_fg_color.rgb, alpha*v_fg_color.a);
        else
            gl_FragColor = mix(v_bg_color, v_fg_color, alpha);
    }
}
"""


class Canvas(app.Canvas):

    def __init__(self):
        app.Canvas.__init__(self, keys='interactive')
        ps = self.pixel_scale

        # Create vertices
        n = 100
        v_position = 0.25 * np.random.randn(n, 2).astype(np.float32)
        v_color = np.random.uniform(0, 1, (n, 3)).astype(np.float32)
        v_size = np.random.uniform(2*ps, 12*ps, (n, 1)).astype(np.float32)

        self.program = gloo.Program(VERT_SHADER, FRAG_SHADER)
        # Set uniform and attribute
        self.program['a_color'] = gloo.VertexBuffer(v_color)
        self.program['a_position'] = gloo.VertexBuffer(v_position)
        self.program['a_size'] = gloo.VertexBuffer(v_size)
        gloo.set_state(clear_color='white', blend=True,
                       blend_func=('src_alpha', 'one_minus_src_alpha'))

        self.show()

    def on_resize(self, event):
        gloo.set_viewport(0, 0, *event.physical_size)

    def on_draw(self, event):
        gloo.clear(color=True, depth=True)
        self.program.draw('points')

def dotproduct(v1, v2):
    return sum((a*b) for a, b in zip(v1, v2))
def length(v):
    return math.sqrt(dotproduct(v, v))
def angle_from_origin(x, y):
    v1 = [1,0]
    v2 = [x,y]
    ang = math.acos(dotproduct(v1, v2) / (length(v1) * length(v2)))
    if v2[1] < 0:
        return (math.pi*2) - ang
    else:
        return ang

def get_distance(a_x, a_y, b_x, b_y):
    return math.pow(((a_x-b_x)*(a_x-b_x) + (a_y-b_y)*(a_y-b_y)),.5)

def get_close_fishes(fish):
    p1_x = fish.x_position
    p1_y = fish.y_position
    p3_x = math.cos(fish.angle)+p1_x
    p3_y = math.sin(fish.angle)+p1_y
    potentials = []
    # bounding box test -> initial get
    for x in range(p1_x-(unit*fish.zone_attraction), p1_x+(unit*fish.zone_attraction)):
        if x < 0 or x > canvasWidth:
            continue
        for y in range(p1_y-(unit*fish.zone_attraction), p1_y+(unit*fish.zone_attraction)):
            if y < 0 or y > canvasHeight:
                continue
            #print str(x) + " " + str(y)
            if WORLD[x][y] != 0 and not (x == p1_x and y == p1_y):
                #print "OH MY GOSH"
                potentials.append(WORLD[x][y])
    # circle test
    for p in potentials:
        p2_x = p[0]
        p2_y = p[1]
        distance = get_distance(p2_x, p2_y, p1_x, p1_y)
        if not distance <= (unit*fish.zone_attraction):
            potentials.remove(p)
        # perception test
        else:
            d12 = get_distance(p1_x, p1_y, p2_x, p2_y)
            d13 = get_distance(p1_x, p1_y, p3_x, p3_y)
            d23 = get_distance(p2_x, p2_y, p3_x, p3_y)
            angle = math.acos((d12*d12 + d13*d13 - d23*d23)/(2 * d12 * d13))
            # field of perception is in both directions, so we make sure angle smaller than half the field of perception
            if angle > math.radians(fish.field_perception/2):
                potentials.remove(p)
            else:
                print angle
    return potentials

class Fish():
    def __init__(self, x, y, angle):
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
    def go():
        zones = zone_check()
        goal_angle = self.angle
        if len(zones['repulse']):
            goal_angle = repulse(zones['repulse'])
        else if len(zones['orient']):
            if len(zones['attract']):
                goal_angle = 0.5 * (orient(zones['orient']) + attract(zones['attract']))
            else:
                goal_angle = orient(zones['orient'])
        else if len(zones['attract']):
            attract(zones['attract'])
        if goal_angle != self.angle:
            if abs(goal_angle - self.angle) or (360 - abs(goal_angle - self.angle)) <= self.turning_rate*self.time_step:
                self.angle = goal_angle
            else if goal_angle > self.angle:
                if goal_angle - self.angle > 180



    def speed_up():
        self.speed += self.max_speed*self.time_step
        if self.speed > 5:
            self.speed = 5
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
            angles.append(float(fish[2])
        return sum(angles) / len(angles)
    def unit_vector_sum(fishes):
        sum_x = 0
        sum_y = 0
        for fish in fishes:
            diff_x = self.x_position - fish[0]
            dif_y = self.y_position - fish[1]
            norm = get_distance(diff_x, diff_y, 0, 0)
            sum_x += diff_x/norm
            sum_y += diff_y/norm
        return sum_x, sum_y
    def zone_check():
        potentials = get_close_fishes(self)
        # repulsion test
        zones = {}
        zones['repulse'] = []
        zones['orient'] = []
        zones['attract'] = []
        for p in potentials:
            distance = get_distance(self.x_position, self.y_position, p[0], p[1])
            if distance <= unit*self.zone_repulsion:
                zones['repulse'].append(p)
            else if distance <= unit*self.zone_orientation:
                zones['orient'].append(p)
            else if distance <= unit*self.zone_attraction:
                zones['attract'].append(p)
        return zones

if __name__ == '__main__':
    WORLD = [[0 for x in range(canvasHeight)] for x in range(canvasWidth)]
    c = Canvas()
    app.run()







