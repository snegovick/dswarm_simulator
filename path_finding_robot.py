import localization_2d
import particle_filter as pf
import collision_detection as cd

import grid_map_overlay as gmo
import potential_field_overlay as pfo

import curve_following_robot as cfr

import random
import math
import copy

from forkmap import map
from path_finding.path_finding import find_path_wave_heuristic8, copy_map
from path_finding.smoothing_algorithms import smooth_path_with_field, smooth_path

ppmm = localization_2d.pixel_per_mm
w = localization_2d.polygon_width
h = localization_2d.polygon_height

class pf_robot(cfr.cf_robot):
    def __init__(self, x, y, r, name, color, theta, sense_noise, radio_address):
        super(pf_robot,self).__init__(x, y, r, name, color, theta, sense_noise, radio_address)
        self.path = []
        self.orig_path = []
        self.current_pt = 0

        self.grid_overlay = None
        self.draw_trajectory = False
        
        self.path_is_built = False
        self.map_is_clean = True

    def draw_path(self, cr):
        if len(self.path)>1:
            self.path=self.path[:1]
        elif (len(self.path)<1 and (not self.map_is_clean)):
            self.grid_overlay.reset_drawing_map()
            self.map_is_clean = True
            self.path_is_built = False
            self.robot_path = []

        if ((self.path_is_built == False) and self.draw_trajectory and len(self.path)==1):
            self.path_is_built = True
            self.map_is_clean = False
            # x_cell = int((self.path[0][0])/self.grid_overlay.pixels_per_cell)
            # y_cell = int((self.path[0][1])/self.grid_overlay.pixels_per_cell)

            x_cell = int((self.x+w/2)/self.grid_overlay.pixels_per_cell)
            y_cell = int((self.y+h/2)/self.grid_overlay.pixels_per_cell)

            start = (x_cell, y_cell)

            x_cell = int((self.path[0][0])/self.grid_overlay.pixels_per_cell)
            y_cell = int((self.path[0][1])/self.grid_overlay.pixels_per_cell)

            finish = (x_cell, y_cell)
            print "start, finish:", start, finish

            t_map = copy_map(self.grid_overlay.map)
            path = find_path_wave_heuristic8(t_map, self.obstacle_field_map, start, finish) # smoothing disabled
            unaltered_path = path[:]
            # path = smooth_path(path)
            path = smooth_path_with_field(path, self.obstacle_field_map, self.grid_overlay.pixels_per_cell)
            print "path:", path
            path.reverse()

            self.robot_path = []
            for p in path:
                t_x = p[0]*self.grid_overlay.pixels_per_cell
                t_y = p[1]*self.grid_overlay.pixels_per_cell
                self.robot_path.append((t_x+self.grid_overlay.pixels_per_cell/ppmm/2.0, t_y+self.grid_overlay.pixels_per_cell/ppmm/2.0))

            for p in unaltered_path:
                self.grid_overlay.drawing_map[int(p[1])][int(p[0])] = 1

        self.draw_dist(cr)
        self.draw_curve(cr)
        # prev_p = None
        # for p in self.robot_path:
        #     cr.arc(p[0], p[1], 5/ppmm, 0.0, 2*math.pi)
        #     if prev_p:
        #         cr.move_to(prev_p[0],prev_p[1])
        #         cr.line_to(p[0], p[1])

        #     cr.stroke()
        #     prev_p = p

    def draw(self, cr):
        super(pf_robot,self).draw(cr)

    def synchronize(self):
        super(pf_robot, self).synchronize()

    def click_handler(self, event):
        print "Hay, im selected ! My name is:", self.name
        if event.button == 3:
            self.path.append([event.x, event.y])
            

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
    grid_overlay = gmo.GridMapOverlay(50, 5, w, h, True)
    grid_overlay.build_static_map(localization_2d.objects2d[0])

    pfield_overlay = pfo.PotentialFieldOverlay(50, 5, w, h, grid_overlay.drawing_map, True, 0.75)


    names = ["first"]#, "second"]
    colors = [(0,0,255), (255, 0, 0)]

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

        if can_add == True:
            radio_addr = nctr+1
            r = pf_robot(posx-localization_2d.width/2,posy-localization_2d.height/2,radius, names[nctr], colors[nctr], 0.0, 0.1, radio_addr)
            r.polygon = localization_2d.objects2d[0]
            r.obstacle_field_map = pfield_overlay.drawing_map
            r.grid_overlay = grid_overlay
            r.draw_trajectory = False
            localization_2d.objects2d[1].append(r)
            nctr += 1

    localization_2d.objects2d[1][0].draw_trajectory = True

    screen = localization_2d.Screen
    screen.overlay_list = [pfield_overlay, grid_overlay]

    localization_2d.run(screen)
