from planner_widgets import *
import random

class DrawingBox(PlannerWidget):
    def __init__(self, n_participators):
        super(DrawingBox, self).__init__()
        self.clickable = True

        self.participators = n_participators
        self.boxes = {}
        self.scale = 0
        self.leftmost_val = 0
        self.vertical_lines = 10
        self.total_length = 100

        self.start_drag = [0,0]
        self.move = False

        self.plan = None
        self.task_lengths = None

    def setPlan(self, plan):
        self.plan = plan
        self.colors = [(random.random(), random.random(), random.random()) for t in self.plan.split_form]
    
    def draw(self, ctx, area):
        self.area = area

        if self.hidden:
            return

        a = area

        ctx.set_source_rgb(1.0, 1.0, 1.0)
        ctx.rectangle(a.x, a.y, a.w, a.h)
        ctx.fill()

        ctx.set_line_width(2)
        ctx.set_source_rgb(0, 0, 0)
        ctx.move_to(a.x, a.y)
        ctx.line_to(a.x+a.w, a.y)

        ctx.move_to(a.x, a.y+a.h)
        ctx.line_to(a.x+a.w, a.y+a.h)
        ctx.stroke()

        # draw horizontal lines
        ctx.set_source_rgb(0.6, 0.6, 0.6)
        ctx.set_line_width(1)

        participator_h = a.h/float(self.participators)
        current_y = a.y

        for i in range(self.participators):
            current_y+=participator_h
            ctx.move_to(a.x, current_y)
            ctx.line_to(a.x+a.w, current_y)

        ctx.stroke()


        # draw vertical lines
        s = 10**self.scale
        px_per_cell = a.w/self.vertical_lines
        ppu = px_per_cell/s
        current_x = a.x
        val = self.leftmost_val

        for i in range(self.vertical_lines):
            next_val = (int(val/s)+(i+1))*s
            remainder = next_val - val
            px = remainder*px_per_cell
            ctx.move_to(px, a.y)
            ctx.line_to(px, a.y+a.h)
        
        ctx.stroke()

        dict_form = self.plan.dictFormExecutors()

        current_color = 0
        current_y = a.y
        # print dict_form
        border = 2
        # print "ppu:", ppu

        print self.leftmost_val*ppu
        for k, v in dict_form.iteritems():
            current_x = 0
            for t in v:
                width = 1*ppu
                c = self.colors[current_color]
                current_color+=1
                current_color%=len(self.colors)

                if current_x+width < self.leftmost_val*ppu:
                    print "pass"
                    current_x += width
                    continue
                
                ctx.set_source_rgb(c[0], c[1], c[2])
                startx = current_x - self.leftmost_val*ppu
                actual_width = width
                if startx<0:
                    actual_width = width+(startx)
                    print "diff:", width+startx
                    startx = 0
                ctx.rectangle(int(a.x+startx), int(a.y+current_y), int(actual_width), int(participator_h))
                # print current_x+border, current_y+border, 20-border, current_y+participator_h-border
                current_x += width
                ctx.fill()
            current_y += participator_h
