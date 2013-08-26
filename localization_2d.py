#!/usr/bin/env python
import random
import math
import collision_detection as cd
from extra import ceiling_camera, radio
import sys

write_pngs = False
if len(sys.argv)>=2:
    if sys.argv[1] == "w":
        write_pngs = True

bpp = 4

polygon_width = 1000
polygon_height = 500
pixel_per_mm = 1.

obstacle_color = (0,0,0)
obstacle_compare_color = (0,0,0)
no_obstacle_compare_color = (255, 255, 255)

width = int(polygon_width/pixel_per_mm)
height = int(polygon_height/pixel_per_mm)

import pygtk
pygtk.require('2.0')
import gtk, gobject, cairo

objects2d = []

class obj2d(object):
    def __init__(self):
        self.x = None
        self.y = None
        self.theta = None

    def check_if_point_belongs(self, x, y):
        return False

    def click_handler(self, event):
        pass

    def draw(self, cairo):
        pass

class polygon (obj2d, cd.aabb):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.lw = 10
        self.selected = False

        self.top = -self.height/2. + self.lw
        self.bottom = self.height/2. - self.lw
        self.left = self.lw-self.width/2.
        self.right = self.width - self.lw - self.width/2.

    def draw(self, cairo):
        cairo.set_source_rgb(1.0,1.0,1.0)
        cairo.rectangle(0,0,self.width/pixel_per_mm,self.height/pixel_per_mm)
        cairo.fill()

        cairo.set_line_width(self.lw)
        cairo.set_source_rgb(obstacle_color[0], obstacle_color[1], obstacle_color[2])
        cairo.move_to(0,self.lw/2)
        cairo.line_to(self.width/pixel_per_mm,self.lw/2)

        cairo.move_to(self.width/pixel_per_mm-self.lw/2,0)
        cairo.line_to(self.width/pixel_per_mm-self.lw/2,self.height/pixel_per_mm)

        cairo.move_to(self.width/pixel_per_mm,self.height/pixel_per_mm-self.lw/2)
        cairo.line_to(0,self.height/pixel_per_mm-self.lw/2)

        cairo.move_to(self.lw/2,self.height/pixel_per_mm)
        cairo.line_to(self.lw/2,0)

        cairo.stroke()
        cairo.set_line_width(2.0)

class square_obstacle (obj2d):
    def __init__(self, width, height, x, y, angle):
        self.width = width
        self.height = height
        self.angle = angle
        self.x = x
        self.y = y
        self.lw = 10
        self.selected = False

    def check_if_point_belongs(self, x, y):
        pass

    def draw(self, cr):
        cr.translate(self.x/pixel_per_mm+w/2., self.y/pixel_per_mm+h/2.)
        cr.rotate(self.angle)
        cairo.set_line_width(self.lw)
        cairo.set_source_rgb(obstacle_color[0], obstacle_color[1], obstacle_color[2])
        # cr.arc(w*self.x+w/2, h*self.y+h/2, self.r, 0.0, 2*math.pi)
        cr.move_to(0,0)
        cr.line_to(width/pixel_per_mm, 0)
        cr.move_to(width/pixel_per_mm,0)
        cr.line_to(width/pixel_per_mm, height/pixel_per_mm)
        cr.move_to(width/pixel_per_mm, height/pixel_per_mm)
        cr.line_to(0, height/pixel_per_mm)
        cr.move_to(0, height/pixel_per_mm)
        cr.line_to(0,0)
        cr.stroke()
        cr.identity_matrix()

class circular_obstacle (obj2d):
    def __init__(self, x, y, r):
        self.x = x
        self.y = y
        self.r = r
        self.lw = 10
        self.selected = False

    def check_if_point_belongs(self, x, y):
        if (math.sqrt((x-self.x)**2+(y-self.y)**2)<self.r):
            return True
        return False

    def draw(self, cr):
        cr.identity_matrix()
        cr.translate(self.x/pixel_per_mm+width/2., self.y/pixel_per_mm+height/2.)
        cr.set_line_width(self.lw)
        cr.set_source_rgb(obstacle_color[0], obstacle_color[1], obstacle_color[2])
        cr.arc(0, 0, self.r, 0.0, 2*math.pi)
        cr.stroke()
        cr.identity_matrix()
        cr.set_line_width(2.0)


def gaussian(mu, sigma, x):
    return math.exp(- ((mu - x) ** 2) / (sigma ** 2) / 2.0) / math.sqrt(2.0 * math.pi * (sigma ** 2))

class proto_robot(obj2d, cd.circle):
    def __init__(self, x, y, theta):
        self.x = x
        self.y = y
        self.selected = False

        self.theta = theta
        self.ranges = [0.0 for i in range(8)]
        self.r = 10.
        
        self.wheel_radius = 1.
        self.base = 85.
        self.wheels_omega = [0.0, 0.0]
        
        self.dtheta = 0.0
        self.dx = 0.0
        self.dy = 0.0
        self.sense_noise = 10.
        self.beams = [0.0, 15.0, 90-15, 90+15, 180, 180+90-15, 180+90+15, 360-15]
        self.range_max = 100.
        self.wheel_noise = 0.1

    def check_if_point_belongs(self, x, y):
        if (math.sqrt((x-self.x)**2+(y-self.y)**2)<self.r):
            return True
        return False

    def synchronize(self):
        pass

    def __repr__(self):
        return "x: "+str(self.x)+", y: "+str(self.y)+", theta: "+str(self.theta)

    def measurement_prob(self, measurements):
        prob = 1.0
        for i,r in enumerate(self.ranges):
            prob*=gaussian(r, self.sense_noise, measurements[i])
        return prob

    def sample_rangefinders(self, data):
        self.data = data
        w = width
        h = height

        if (False):#cd.circle_to_aabb_inverse_plain((self.x, self.y, self.r+self.range_max), self.polygon)[0] == True):
            #print "Far"
            self.ranges = [self.range_max]*8
        else:
            #print "Near"
            for i, b in enumerate(self.beams):
                all_ranges = []
                angle = self.theta+b*math.pi/180.
                all_ranges.append(int(cd.orientedline_to_inverse_aabb_dist(self.x+self.r*math.cos(angle), self.y+self.r*math.sin(angle), angle, self.range_max, self.polygon[0])))
                for o in self.polygon[1:]:
                    all_ranges.append(int(cd.ray_dist_to_circle_plain(o.x, o.y, o.r, self.x+self.r*math.cos(angle), self.y+self.r*math.sin(angle), angle, self.range_max)[1]))
                self.ranges[i] = min(all_ranges)
        
        # print "ranges:", self.ranges, "position:", self.x, self.y
        self.synchronize()
        #print "====="


class robot (proto_robot):
    def __init__(self, x, y, r, name, color, theta, sense_noise, radio_address):
        super(robot,self).__init__(x, y, theta)
        self.r = r
        self.range_max = 100.
        self.name = name
        self.sense_noise = sense_noise

        self.color = color
        
        self.ranges = [0.0 for i in range(8)]

        self.draw_beams = True
        self.data = None
        self.transciever = radio.transciever(radio_address)

    def click_handler(self, event):
        pass

    def update_position(self, polygon):
        ox = self.x
        oy = self.y
        ot = self.theta
        owheels = self.wheels_omega[:]

        #old_robot = robot(self.x, self.y, self.r, self.name, self.color, self.theta, self.sense_noise, None)
        deltaulr = [om*self.wheel_radius+random.gauss(0.0, self.wheel_noise) for om in  self.wheels_omega]
        deltau = (deltaulr[0]+deltaulr[1])/2.0
        self.dtheta = (deltaulr[0] - deltaulr[1])/self.base
        self.theta = self.theta+self.dtheta

        while self.theta>math.pi*2.0:
            self.theta-=math.pi*2.0

        x = self.x
        y = self.y
        #print x, self.x, y, self.y, self.dtheta
        self.x = self.x + deltau*math.cos(self.theta)
        self.y = self.y + deltau*math.sin(self.theta)
        # new_robot = robot(self.x, self.y, self.r, self.name, self.color, self.theta, self.sense_noise)
        
        if (cd.circle_to_aabb_inverse(self, polygon)[0] == True):
            self.x = ox
            self.y = oy
            self.theta = ot
            self.wheels_omega = owheels
        return self

    def draw(self, cr):
        #self.update_position()
        w = width
        h = height

        cr.translate(self.x/pixel_per_mm+w/2., self.y/pixel_per_mm+h/2.)
        cr.rotate(self.theta)
        cr.set_source_rgb (self.color[0], self.color[1], self.color[2])
        # cr.arc(w*self.x+w/2, h*self.y+h/2, self.r, 0.0, 2*math.pi)
        cr.arc(0, 0, self.r/pixel_per_mm, 0.0, 2*math.pi)
        cr.move_to(0,0)
        cr.line_to(self.r/pixel_per_mm,0)
        cr.stroke()

        cr.set_source_rgb (1., 0, 0)
        dist = [(0.0, 0.0, 0.0) for i in range(8)]

        for i, b in enumerate(self.beams):
            angle = self.theta+b*math.pi/180.

        if self.draw_beams:
            for b, l in zip(self.beams, self.ranges):
                cr.rotate(b*math.pi/180.0)
                cr.set_source_rgba (0, 0, 0, 0.5)
                cr.move_to(self.r/pixel_per_mm+3, 0)
                cr.line_to(self.r/pixel_per_mm+l+3, 0)
                cr.stroke()
                cr.rotate(-b*math.pi/180.0)

class Overlay:
    def draw(self, context, width, height):
        pass

# Create a GTK+ widget on which we will draw using Cairo
class Screen(gtk.DrawingArea):

    # Draw in response to an expose-event
    __gsignals__ = { "expose-event": "override" }
    step = 0

    overlay_list = []
    radio = radio.radio()
    cam = ceiling_camera.camera_service(0)
    radio.add_transciever(cam.transciever)

    active_object = None

    def expose_overlays(self, c, w, h):
        for o in self.overlay_list:
            o.draw(c, w, h)

    def periodic(self):
        self.queue_draw()
        return True

    def radio_init(self):
        layer = objects2d[1]
        for r in layer:
            self.radio.add_transciever(r.transciever)
            self.cam.track_object(r.name, r)
    
    def button_press_event(self, widget, event):
        if event.button == 1:
            layer0 = objects2d[0]
            layer1 = objects2d[1]
            for obj in layer0+layer1:
                if obj.check_if_point_belongs(event.x - width/2., event.y-height/2.):
                    if self.active_object != None:
                        self.active_object.selected = False
                    self.active_object = obj
                    self.active_object.selected = True
                    obj.click_handler(event)
                    return
        elif event.button == 3:
            if self.active_object!=None:
                self.active_object.click_handler(event)
            else:
                print "Select object"

    # Handle the expose-event by drawing
    def do_expose_event(self, event):
        self.radio.process()
        self.cam.process()
        # Create the cairo context
        cr_gdk = self.window.cairo_create()

        surface = cr_gdk.get_target()

        cr_surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        cr = cairo.Context(cr_surf)
        
        # Restrict Cairo to the exposed area; avoid extra work
        cr.rectangle(event.area.x, event.area.y, event.area.width, event.area.height)
        cr.clip()

        #self.expose_overlays(cr, width, height)

        # polygon and obstacles
        layer = objects2d[0]
        for obj in layer:
            obj.draw(cr)

        cr_surf.flush()

        data = cr_surf.get_data()

        layer = objects2d[1]
        for r in layer:
            r.sample_rangefinders(data)

        for obj in layer:
            obj.update_position(objects2d[0][0])
            obj.draw(cr)
            cr.identity_matrix()

    
        # for r in layer:
        #     r.update_position()

        self.expose_overlays(cr, width, height)

        if write_pngs:
            cr_surf.write_to_png("/tmp/"+str(self.step).zfill(6)+".png")
        self.step += 1
        cr_gdk.set_source_surface(cr_surf)
        cr_gdk.paint()

        
# GTK mumbo-jumbo to show the widget in a window and quit when it's closed
def run(Widget):
    window = gtk.Window()
    window.resize(width, height)
    window.connect("delete-event", gtk.main_quit)
    widget = Widget()
    widget.radio_init()
    widget.connect("button_press_event", widget.button_press_event)
    widget.set_events(gtk.gdk.BUTTON_PRESS_MASK)
    # print dir(widget)
    # widget.m_window = window
    gobject.timeout_add(10, widget.periodic)
    widget.x = 0.
    widget.y = 0.
    widget.show()
    window.add(widget)
    window.present()
    gtk.main()

if __name__ == "__main__":
    run(Screen)
