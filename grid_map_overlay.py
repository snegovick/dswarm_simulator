import localization_2d as l2d
import math

from path_finding.map_utils import print_map, copy_map

class GridMapOverlay(l2d.Overlay):
    def __init__(self, x_cells, y_cells, w, h, save_aspect_ratio=False):
        self.w = w
        self.h = h

        self.x_cells = x_cells
        self.pixels_per_cell = w/self.x_cells
        if save_aspect_ratio:
            self.y_cells = h/self.pixels_per_cell
        else:
            self.y_cells = y_cells

        self.map = []
        for y in range(self.y_cells):
            self.map.append([])
            for x in range(self.x_cells):
                self.map[-1].append(0)

        self.drawing_map = copy_map(self.map)

    def reset_drawing_map(self):
        self.drawing_map = copy_map(self.map)

    def build_static_map(self, polygon):
        x_w = self.w/self.x_cells
        y_h = self.h/self.y_cells
        sigma = 20

        for o in polygon[1:]:
            for y, l in enumerate(self.map):
                for x, e in enumerate(l):
                    ex = x*x_w+x_w/2.-self.w/2.
                    ey = y*y_h+y_h/2.-self.h/2.
                    if (math.sqrt((o.x-ex)**2+(o.y-ey)**2)<=o.r+sigma):
                        print o.x, o.y, o.r, ex, ey
                        self.map[y][x] = -1

        # add borders
        for x, e in enumerate(self.map[0]):
            self.map[0][x] = -1
            self.map[-1][x] = -1

        for y, e in enumerate(self.map):
            self.map[y][0] = -1
            self.map[y][-1] = -1


        self.drawing_map = copy_map(self.map)
        # print print_map(self.map)

    def draw(self, cr, w, h):
        x_w = self.w/self.x_cells
        y_h = self.h/self.y_cells

        color = 0.05
        cr.set_line_width(0.1)

        for y in range(self.y_cells):
            for x in range(self.x_cells):
                if self.drawing_map[y][x]!=0:
                    cr.set_source_rgba(0, 0, 0, 0.2)
                elif self.drawing_map[y][x] == 1:
                    cr.set_source_rgba(112./255, 128./255,144./255,0.2)
                else:
                    cr.set_source_rgba(0.8, 0.8, 0.8, 0.1)
                cr.rectangle(x*x_w+1, y*y_h+1, x_w-1, y_h-1)
                cr.fill()
