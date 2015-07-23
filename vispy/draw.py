from vispy import gloo, app
import threading, math
from math import pi
import numpy as np
from Fish import Fish

#WORLD = []
#canvasWidth = 1024
#canvasHeight = 768
#unit = 9

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

# fish stuff and stuff #

class WORLD():
    def __init__(self, canvasWidth, canvasHeight, unit):
        self.WORLD = []
        self.canvasWidth = canvasWidth
        self.canvasHeight = canvasHeight
        self.unit = unit
        self.fishes = []
    def setAndGo(self):
        self.init_world()
        self.addFish()
    #def startFish(self, fish):
    #    threads = 
    def addFish(self, x, y, angle):
        fishy_fish = Fish(self, x, y, angle)
        fishy_fish.start()
        self.fishes.append(fishy_fish)
    def dotproduct(v1, v2):
        return sum((a*b) for a, b in zip(v1, v2))
    def length(v):
        return math.sqrt(dotproduct(v, v))
    def angle_from_origin(x, y):
        v1 = [1,0]
        v2 = [x,y]
        ang = math.acos(dotproduct(v1, v2) / (length(v1) * length(v2)))
        if v2[1] < 0:
            return (pi*2) - ang
        else:
            return ang
    def get_distance(a_x, a_y, b_x, b_y):
        return math.pow(((a_x-b_x)*(a_x-b_x) + (a_y-b_y)*(a_y-b_y)),.5)
    def get_close_fishes(self, fish):
        p1_x = int(fish.x_position)
        p1_y = int(fish.y_position)
        p3_x = math.cos(fish.angle)+p1_x
        p3_y = math.sin(fish.angle)+p1_y
        potentials = []
        # bounding box test -> initial get
        for x in range(p1_x-(self.unit*fish.zone_attraction), p1_x+(self.unit*fish.zone_attraction)):
            if x < 0 or x > self.canvasWidth:
                continue
            for y in range(p1_y-(self.unit*fish.zone_attraction), p1_y+(self.unit*fish.zone_attraction)):
                if y < 0 or y > self.canvasHeight:
                    continue
                #print str(x) + " " + str(y)
                if self.WORLD[x][y] != 0 and not (x == p1_x and y == p1_y):
                    #print "OH MY GOSH"
                    potentials.append(self.WORLD[x][y])
        # circle test
        for p in potentials:
            p2_x = p[0]
            p2_y = p[1]
            distance = self.get_distance(p2_x, p2_y, p1_x, p1_y)
            if not distance <= (self.unit*fish.zone_attraction):
                potentials.remove(p)
            # perception test
            else:
                d12 = self.get_distance(p1_x, p1_y, p2_x, p2_y)
                d13 = self.get_distance(p1_x, p1_y, p3_x, p3_y)
                d23 = self.get_distance(p2_x, p2_y, p3_x, p3_y)
                angle = math.acos((d12*d12 + d13*d13 - d23*d23)/(2 * d12 * d13))
                # field of perception is in both directions, so we make sure angle smaller than half the field of perception
                if angle > math.radians(fish.field_perception/2):
                    potentials.remove(p)
                else:
                    print angle
        return potentials
    def init_world(self):
        self.WORLD = [[0 for x in range(self.canvasHeight)] for x in range(self.canvasWidth)]

if __name__ == '__main__':
    init_world()
    c = Canvas()
    app.run()







