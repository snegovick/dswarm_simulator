import localization_2d
import particle_filter as pf
import collision_detection as cd

from extra import radio

from overlays import grid_map_overlay as gmo
from overlays import potential_field_overlay as pfo

import path_finding_robot as pfr

import random
import math
import copy
import struct

from forkmap import map
from path_finding.path_finding import find_path_wave_heuristic8
from path_finding.map_utils import copy_map, translate_coords_to_cells, neighbours
from path_finding.smoothing_algorithms import smooth_path_with_field, smooth_path
from path_finding.potential_field import build_potential_field_map

ppmm = localization_2d.pixel_per_mm
w = localization_2d.polygon_width
h = localization_2d.polygon_height

x_cells = 50
y_cells = 5

class doa_robot(pfr.pf_robot):
    def __init__(self, x, y, r, name, color, theta, sense_noise, radio_address):
        super(doa_robot,self).__init__(x, y, r, name, color, theta, sense_noise, radio_address)
        self.path = []
        self.orig_path = []
        self.current_pt = 0

        self.grid_overlay = None
        self.draw_trajectory = False
        
        self.path_is_built = False
        self.map_is_clean = True

        self.counter = 0

        self.position_rq_timeout = random.randint(5, 10)
        self.last_position_rq = 0
        self.other_robots = {}

        self.dynamic_map_rebuild_timeout = 15
        self.last_map_rebuild = 0
        self.field_propagate_steps = 10

        self.dynamic_obstacle_map = None

    def draw_path(self, cr):
        super(doa_robot,self).draw_path(cr)

    def draw(self, cr):
        super(doa_robot,self).draw(cr)

    def synchronize(self):
        self.counter+=1

        if (self.counter-self.last_map_rebuild)>self.dynamic_map_rebuild_timeout:
            self.last_map_rebuild = self.counter
            self.dynamic_obstacle_map = copy_map(self.static_obstacle_map)
            for rx, ry in self.other_robots.values():
                x, y = translate_coords_to_cells(rx+w/2., ry+h/2., w, h, x_cells, y_cells)
                self.dynamic_obstacle_map[y][x] = -1                
                for tx, ty in neighbours:
                    nx = x+tx
                    ny = y+ty
                    if (nx < x_cells) and (nx >= 0) and (ny >= 0) and (ny < y_cells):
                        self.dynamic_obstacle_map[ny][nx] = -1
            if self.selected:
                self.obstacle_field_map = self.pfield_overlay.set_drawing_map(self.dynamic_obstacle_map, self.regression_coeff, self.start_value, self.threshold)
            if (len(self.path)==1) and (not self.turnaround_maneuver):
                self.rebuild_path(self.dynamic_obstacle_map)
                self.grid_overlay.reset_drawing_map()
                for p in self.unaltered_path:
                    self.grid_overlay.drawing_map[int(p[1])][int(p[0])] = 1


        if (self.counter-self.last_position_rq)>self.position_rq_timeout:
            self.last_position_rq = self.counter
            print "im (", self.name, ") transmitting message"
            m = radio.message(self.name, 0)
            self.transciever.transmit(m)

        if self.transciever.is_message_available():
            m = self.transciever.receive()
            print "i (",self.name, ") have message:", m
            id, x, y = struct.unpack("Bff", m.data)
            if id != self.transciever.address:
                self.other_robots[id] = [x, y]
        super(doa_robot, self).synchronize()


    def click_handler(self, event):
        print "Hay, im selected ! My name is:", self.name
        if event.button == 1:
            if self.dynamic_obstacle_map == None:
                self.dynamic_obstacle_map = copy_map(self.static_obstacle_map)
            self.pfield_overlay.set_drawing_map(self.dynamic_obstacle_map)
        if event.button == 3:
            print "adding point to path"
            self.path = []
            self.path.append([event.x, event.y])
            self.path_is_built = False
            self.map_is_clean = True
            self.grid_overlay.reset_drawing_map()
            print self.path


if __name__=="__main__":
    localization_2d.objects2d.append([localization_2d.polygon(localization_2d.polygon_width, localization_2d.polygon_height)])

    points = [(-2*w/6, -0.5*h/5), (-w/6, -1.5*h/5), (0, -0.5*h/5), (w/6, -1.5*h/5), (2*w/6, -0.5*h/5),
              (-2*w/6, 1.5*h/5), (-w/6, 0.5*h/5), (0, 1.5*h/5), (w/6, 0.5*h/5), (2*w/6, 1.5*h/5)]
    
    for p in points:
        print p[0], p[1]
        localization_2d.objects2d[0].append(localization_2d.circular_obstacle(p[0], p[1], 30))

    # exit()
    localization_2d.objects2d.append([])
    # obstacles here
    radius = 20.


    # add grid overlay and create grid map of obstacles
    grid_overlay = gmo.GridMapOverlay(x_cells, y_cells, w, h, True)
    y_cells = grid_overlay.y_cells
    grid_overlay.build_static_map(localization_2d.objects2d[0])

    pfield_overlay = pfo.PotentialFieldOverlay(x_cells, y_cells, w, h, grid_overlay.drawing_map, True)


    names = ["first", "second"]
    colors = [(0,0,255), (255, 0, 0)]

    regression_coeff = pfield_overlay.regression_coeff
    start_value = pfield_overlay.start_value
    threshold = pfield_overlay.threshold

    static_obstacle_map = grid_overlay.drawing_map
    

    #add robots
    nctr = 0
    while nctr<len(names):
        posx = random.randrange(radius*2., localization_2d.polygon_width-radius*2.)
        posy = random.randrange(radius*2., localization_2d.polygon_height-radius*2.)
        print posx, posy
        can_add = True
        for r in localization_2d.objects2d[1]:
            if math.sqrt((posx-r.x)**2+(posy-r.y)**2)<radius:
                can_add = False
                break

        if not can_add:
            continue

        for o in localization_2d.objects2d[0][1:]:
            dist = math.sqrt((posx-w/2.-o.x)**2+(posy-h/2.-o.y)**2)
            print "dist:", dist, "min_dist:", (radius+o.r)
            if dist<(radius+o.r):
                can_add = False
                break

        if can_add == True:
            radio_addr = nctr+1
            r = doa_robot(posx-localization_2d.width/2,posy-localization_2d.height/2,radius, names[nctr], colors[nctr], 0.0, 0.1, radio_addr)
            r.polygon = localization_2d.objects2d[0]
            r.static_obstacle_map = static_obstacle_map
            r.obstacle_field_map = build_potential_field_map(static_obstacle_map, regression_coeff, start_value, threshold)
            r.regression_coeff = regression_coeff
            r.start_value =  start_value
            r.threshold = threshold
            r.pfield_overlay = pfield_overlay
            r.grid_overlay = grid_overlay
            r.draw_trajectory = True
            localization_2d.objects2d[1].append(r)
            nctr += 1

    screen = localization_2d.Screen
    screen.overlay_list = [pfield_overlay, grid_overlay]
    localization_2d.run(screen)
