from planner_widgets import *

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
    
    def draw(self, ctx, area):
        self.area = area

        if self.hidden:
            return

        a = area

        ctx.set_source_rgb(1.0, 1.0, 1.0)
        ctx.rectangle(a.x, a.y, a.x+a.w, a.y+a.h)
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
        px_per_cell = a.w/self.vertical_lines
        current_x = a.x
        val = self.leftmost_val
        s = 10**self.scale
        for i in range(self.vertical_lines):
            next_val = int(val+(i+1)*s)/int(s)
            next_val *= s
            remainder = next_val - val
            px = remainder*px_per_cell
            ctx.move_to(px, a.y)
            ctx.line_to(px, a.y+a.h)
        
        ctx.stroke()
