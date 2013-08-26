#!/usr/bin/env python
import random
import math
import sys

from planner_widgets import *
from drawing_box import *

width = 800
height = 400

import pygtk
pygtk.require('2.0')
import gtk, gobject, cairo

def point_in_rect((l, r, u, d), (x, y)):
    if x>l and x<r and y>d and y<u:
        return True
    return False

class Screen(gtk.DrawingArea):
    
    # Draw in response to an expose-event
    __gsignals__ = { "expose-event": "override" }
    step = 0
    widget = None
    widgets = []

    def periodic(self):
        self.queue_draw()
        return True
    
    def button_press_event(self, widget, event):
        for w in self.widgets:
            if w.clickable and (not w.hidden) and point_in_rect((w.area.x, w.area.x+w.area.w, w.area.y+w.area.h, w.area.y), (event.x, event.y)):
                w.button_press_event(Event(event.x-w.area.x, event.y-w.area.y, event.button))

    def button_release_event(self, widget, event):
        for w in self.widgets:
            if w.clickable and (not w.hidden) and point_in_rect((w.area.x, w.area.x+w.area.w, w.area.y+w.area.h, w.area.y), (event.x, event.y)):
                w.button_release_event(Event(event.x-w.area.x, event.y-w.area.y, event.button))

    def motion_notify(self, widget, event):
        for w in self.widgets:
            if w.clickable and (not w.hidden):
                w.motion_notify(Event(event.x-w.area.x, event.y-w.area.y, None))



    # Handle the expose-event by drawing
    def do_expose_event(self, event):
        # Create the cairo context
        cr_gdk = self.window.cairo_create()

        surface = cr_gdk.get_target()

        cr_surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        cr = cairo.Context(cr_surf)

        self.db.leftmost_val = self.tl.start
        self.tl.scale = self.db.scale
        self.tl.total_length = self.db.total_length
        self.widget.draw(cr, Area(0, 0, width, height))
        
        # Restrict Cairo to the exposed area; avoid extra work
        cr.rectangle(event.area.x, event.area.y, event.area.width, event.area.height)
        cr.clip()

        cr_surf.flush()

        self.step += 1
        cr_gdk.set_source_surface(cr_surf)
        cr_gdk.paint()

    def add_widget(self, widget):
        self.widgets.append(widget)

        
# GTK mumbo-jumbo to show the widget in a window and quit when it's closed
def run(Widget):
    window = gtk.Window()
    window.resize(width, height)
    window.connect("delete-event", gtk.main_quit)
    widget = Widget()
    widget.connect("button_press_event", widget.button_press_event)
    widget.set_events(gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.BUTTON_RELEASE_MASK | gtk.gdk.MOTION_NOTIFY | gtk.gdk.POINTER_MOTION_MASK | gtk.gdk.POINTER_MOTION_HINT_MASK)
    widget.connect("button_release_event", widget.button_release_event)
    widget.connect("motion_notify_event", widget.motion_notify)

    vp = VerticalPack()
    widget.db = DrawingBox(20)
    vp.pack_end(widget.db)
    widget.tl = TimeLineWidget()
    vp.pack_end(widget.tl)
    widget.widget = vp

    widget.tl.vlines = widget.db.vertical_lines

    widget.add_widget(vp)
    widget.add_widget(widget.db)
    widget.add_widget(widget.tl)
    
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

