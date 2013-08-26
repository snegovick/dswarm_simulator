import sys
import math

class Area:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

class Event:
    def __init__(self, x, y, button):
        self.x = x
        self.y = y
        self.button = button

class PlannerWidget(object):
    def __init__(self):
        self.area = Area(None, None, None, None)
        self.area_rq = Area(None, None, None, None)
        self.hidden = False
        self.clickable = False

    def draw(self, ctx, area):
        pass

    def button_press_event(self, event):
        pass

    def button_release_event(self, event):
        pass

    def motion_notify(self, event):
        pass

class VerticalPack(PlannerWidget):
    def __init__(self):
        super(VerticalPack, self).__init__()
        self.subwidgets = []
        self.clickable = False

    def draw(self, ctx, area):
        self.area = area

        if self.hidden:
            return

        unknown_h = []
        known_h = []
        consumed_h = 0

        for w in self.subwidgets:
            if w.area_rq.h == None:
                unknown_h.append(w)
            else:
                known_h.append(w)
                consumed_h+=w.area_rq.h

        free_h = area.h-consumed_h
        h_per_widget = int(free_h/len(unknown_h))

        current_x = area.x
        current_y = area.y

        for w in self.subwidgets:
            
            if w in known_h:
                h = w.area_rq.h
            else:
                h = h_per_widget
            w.draw(ctx, Area(current_x, current_y, area.w, h))
            current_y += h

    def pack_end(self, widget):
        self.subwidgets.append(widget)

class TimeLineWidget(PlannerWidget):
    def __init__(self):
        super(TimeLineWidget, self).__init__()
        self.area_rq = Area(None, None, None, 50)
        self.clickable = True
        self.start = 0
        self.scale = 0
        self.total_length = 0
        self.vlines = 0

        self.move = False
        self.start_drag = [0,0]

    def button_press_event(self, event):
        self.move = True
        self.start_drag = [event.x, event.y]

    def motion_notify(self, event):
        if not self.move:
            return

        a = self.area
        end_drag = [event.x, event.y]
        dist = math.sqrt((end_drag[0]-self.start_drag[0])**2+(end_drag[1]-self.start_drag[1])**2)
        print "dist:", dist
        if dist>1:
            s = 10**self.scale
            displayed_length = s*self.vlines
            tlen = self.total_length
            if self.total_length < displayed_length:
                tlen = displayed_length
            px_per_unit = float(a.w)/tlen

            if end_drag[0]>self.start_drag[0]:
                if not self.start+displayed_length>self.total_length:
                    self.start+= dist/px_per_unit
            else:
                self.start-= dist/px_per_unit

        print "self.start:", self.start
        if self.start<0:
            self.start = 0

            

        self.start_drag = [event.x, event.y]


    def button_release_event(self, event):
        self.move = False
    
    def draw(self, ctx, area):
        self.area = area

        if self.hidden:
            return

        a = area

        ctx.set_line_width(1)
        ctx.set_source_rgb(0.8, 0.8, 0.8)
        ctx.rectangle(a.x, a.y, a.x+a.w, a.y+a.h)
        ctx.fill()

        ctx.set_line_width(2)
        ctx.set_source_rgb(0, 0, 0)
        ctx.move_to(a.x, a.y)
        ctx.line_to(a.x+a.w, a.y)

        ctx.move_to(a.x, a.y+a.h)
        ctx.line_to(a.x+a.w, a.y+a.h)
        ctx.stroke()

        # draw position
        s = 10**self.scale
        cell_sz = self.area.w/self.vlines
        px_per_unit = cell_sz/s
        displayed_length = s*self.vlines
        tlen = self.total_length
        if self.total_length < displayed_length:
            tlen = displayed_length
        total_scale = tlen/float(a.w)

        start = self.start/total_scale
        end = start+displayed_length/total_scale
        ctx.move_to(a.x+start, a.y)
        ctx.line_to(a.x+start, a.y+a.h)
        ctx.move_to(a.x+end, a.y)
        ctx.line_to(a.x+end, a.y+a.h)
        ctx.stroke()


class NumberedBox(PlannerWidget):
    def __init__(self):
        super(NumberedBox, self).__init__()
        pass
    
    def draw(self, ctx, area):
        pass
