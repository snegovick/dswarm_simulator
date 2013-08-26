import localization_2d as l2d
import math

from path_finding.map_utils import print_map, copy_map
from path_finding.potential_field import build_potential_field_map

class PotentialFieldOverlay(l2d.Overlay):
    def __init__(self, x_cells, y_cells, w, h, obstacle_map, save_aspect_ratio=False, regression_coeff = 0.8, start_value = 1.0, threshold = 0.2):
        self.w = w
        self.h = h

        self.regression_coeff = regression_coeff
        self.start_value = start_value
        self.threshold = threshold

        self.x_cells = x_cells
        self.pixels_per_cell = w/self.x_cells
        if save_aspect_ratio:
            self.y_cells = h/self.pixels_per_cell
        else:
            self.y_cells = y_cells

        self.map = obstacle_map

        self.drawing_map = build_potential_field_map(self.map, regression_coeff, start_value, threshold)
        print_map(self.drawing_map)

    def reset_drawing_map(self):
        self.drawing_map = copy_map(self.map)

    def set_drawing_map(self, ext_map, r, s, t):
        self.drawing_map = build_potential_field_map(ext_map, r, s, t)
        return self.drawing_map

    def draw(self, cr, w, h):
        x_w = self.w/self.x_cells
        y_h = self.h/self.y_cells

        color = 0.0
        cr.set_line_width(0.1)

        for y in range(self.y_cells):
            for x in range(self.x_cells):
                val = (1.0-self.drawing_map[y][x])*0.95
                cr.set_source_rgba(val, val, val, 0.3)
                cr.rectangle(x*x_w+1, y*y_h+1, x_w-1, y_h-1)
                cr.fill()
