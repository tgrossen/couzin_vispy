#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

from vispy import gloo
from vispy import app
import numpy as np
import random, argparse
from World import World
from Fish import Fish

VERT_SHADER = """
attribute vec2 a_position;
uniform float u_size;
void main() {
    gl_Position = vec4(a_position, 0.0, 1.0);
    gl_PointSize = u_size;
}
"""

FRAG_SHADER = """
void main() {
    gl_FragColor = vec4(1.0, 0.0, 1.0, 1.0);
}
"""

n = 6

desc=''' Example:
    python fish_world_program.py --fishes 2
    '''

class Canvas(app.Canvas):
    def __init__(self, world):
        app.Canvas.__init__(self, keys='interactive', size=(1024, 768))
        self.world = world
        ps = self.pixel_scale

        self.program = gloo.Program(VERT_SHADER, FRAG_SHADER)
        data = np.random.uniform(0, 0, size=(n, 2))
        self.a_position = data.astype(np.float32)
        self.program['a_position'] = self.a_position #center position array of the fish pixels
        self.program['u_size'] = 3 #size of the fish pixels
        
        self.timer = app.Timer('auto', connect=self.on_timer, start=True)

        self.show()

    def on_key_press(self, event):
        if event.text == ' ':
            if self.timer.running:
                self.timer.stop()
                for fish in self.world.fishes:
                    fish.stop()
            else:
                self.timer.start()
                for fish in self.world.fishes:
                    fish.start()

    def on_resize(self, event):
        width, height = event.size
        gloo.set_viewport(0, 0, width, height)

    def on_draw(self, event):
        gloo.clear('white')
        self.program.draw('points')
    
    def on_timer(self, event):
        x = 0
        for fish in self.world.fishes:
            # print self.a_position[x]
            self.a_position[x][0] = (fish.x_position - (self.world.canvasWidth/2.0)) / (self.world.canvasWidth/2.0)   #the X-Position
            self.a_position[x][1] = (fish.y_position - (self.world.canvasHeight/2.0)) / (self.world.canvasHeight/2.0) #the Y-Position
            x += 1
        self.program['a_position'] = self.a_position
        self.update()

def readCommandLine():
    parser = argparse.ArgumentParser(description=desc, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--fishes', required=False, default=50, help='Number of fishes to use.')
    parser.add_argument('--speed', required=False, default=1, help='Amount by which to multiply speed, turning angle, etc.')
    parser.add_argument('--log', required=False, default=False, help='Boolean value for logging or no logging')
    return parser.parse_args()

if __name__ == '__main__':
    try:
        args = readCommandLine()
    except:
        print desc
        raise
    n = int(args.fishes)
    speed = int(args.speed)
    if args.log == False:
        log = False
    else:
        log = True
    world = World(1024, 768, 3)
    world.init_world()
    c = Canvas(world)
    if n < 50:
        world.add_test_fishes(n, log, speed)
    else:
        world.add_fish_swarm(n, log, speed)
    if sys.flags.interactive != 1:
        app.run()