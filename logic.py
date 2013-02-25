import localization_2d
import particle_filter as pf
import collision_detection as cd

import random
import math
import copy

from forkmap import map

ST_GO_STRAIGHT = 1
ST_TURN_LEFT = 2
ST_TURN_RIGHT = 3
ST_CLOSE_APPROACH = 4

TURN_SPEED = 0.9
FORWARD_SPEED = 0.9

ppmm = localization_2d.pixel_per_mm
w = localization_2d.polygon_width
h = localization_2d.polygon_height


class loc_robot(localization_2d.robot):
    def __init__(self, x, y, r, name, color, theta, sense_noise):
        super(loc_robot,self).__init__(x, y, r, name, color, theta, sense_noise)
        self.ctr = 0

        self.dir_start = 0
        self.dir_change_t = 100
        self.rotate_t = 1

        self.state = ST_GO_STRAIGHT
        self.probabilities = None
        
        self.new_angle = 0.0

        self.close_threshold = 20.

        self.n_particles = 500
        self.random_particles = self.n_particles/10

        self.pf = pf.particle_filter()

        # uniform
        #robot_position_start = (self.r*2-w/2, self.r*2-h/2)
        #robot_position_end = (w/2-self.r*2, h/2-self.r*2)

        # centered around robot position
        robot_position_start = (self.x-self.r, self.y-self.r)
        robot_position_end = (self.x+self.r, self.y+self.r)

        self.particles = pf.init_particles_oriented(robot_position_start, robot_position_end, theta, self.n_particles)

        self.draw_particles =True
        self.sense_noise = 100.

        self.resampling_t = 0
        self.start = 0

        self.step = 0

    def draw(self, cr):
        super(loc_robot,self).draw(cr)
        if not self.draw_particles:
            return None

        cr.set_source_rgb (self.color[0], self.color[1], self.color[2])
        l = 5.
        cr.identity_matrix()

        if self.probabilities!=None:
            max_prob_idx = self.probabilities.index(max(self.probabilities))
            px, py, pt = self.particles[max_prob_idx]
            # print "probability:", self.probabilities[max_prob_idx], "mp particle coords:", self.particles[max_prob_idx]
            cr.arc(px/ppmm+w/2,py/ppmm+h/2,10,0.0,2*math.pi)
            cr.move_to(px/ppmm+w/ppmm/2,py/ppmm+h/ppmm/2)
            cr.line_to(px/ppmm+l*math.cos(pt)+w/ppmm/2,py/ppmm+l*math.sin(pt)+h/ppmm/2)
            cr.stroke()


        for p in self.particles:#[:-self.n_particles/100]:#[:1000]:
            px = p[0]
            py = p[1]
            ptheta = p[2]
            cr.arc(px/ppmm+w/2,py/ppmm+h/2,2,0.0,2*math.pi)
            cr.move_to(px/ppmm+w/ppmm/2,py/ppmm+h/ppmm/2)
            cr.line_to(px/ppmm+l*math.cos(ptheta)+w/ppmm/2,py/ppmm+l*math.sin(ptheta)+h/ppmm/2)
            cr.stroke()

    def move_particles(self):
        drive_noise = self.wheel_noise
        omega = self.wheels_omega
        polygon = self.polygon
        base = self.base
        robot_radius = self.r
        radius = self.wheel_radius
        def update_position(particle):
            x0, y0, t0 = particle
            deltaulr = [om*radius+random.gauss(0.0, drive_noise) for om in omega]
            deltau = (deltaulr[0]+deltaulr[1])/2.0
            dtheta = (deltaulr[0] - deltaulr[1])/base
            theta = t0+dtheta

            while theta>math.pi*2.0:
                theta-=math.pi*2.0

            x = x0
            y = y0
            x = x + deltau*math.cos(theta)
            y = y + deltau*math.sin(theta)

            if ((cd.circle_to_aabb_inverse_plain((x, y, robot_radius),
                                                 polygon[0])[0] == True)) :
                return (x0, y0, theta)

            for o in polygon[1:]:
                if (cd.circle_to_circle_plain(x, y, robot_radius, o.x, o.y, o.r)[0] == True):
                    return (x0, y0, theta)
            return (x, y, theta)
        self.particles = pf.move_particles(self.particles, update_position)
        


    def resample(self, start, end):
        r = self.r
        data = self.data
        range_max = self.range_max
        polygon = self.polygon
        def sample_rangefinders(p):
            self.data = data
            theta = p[2]
            x = p[0]
            y = p[1]
            ranges = [0.0]*8

            for i, b in enumerate(self.beams):
                angle = theta+b*math.pi/180.
                all_ranges = []
                all_ranges.append(int(cd.orientedline_to_inverse_aabb_dist(x+r*math.cos(angle), y+r*math.sin(angle), angle, range_max, polygon[0])))
                for o in polygon[1:]:
                    all_ranges.append(int(cd.ray_dist_to_circle_plain(o.x, o.y, o.r, x+r*math.cos(angle), y+r*math.sin(angle), angle, range_max)[1]))

                ranges[i] = min(all_ranges)

            return ranges

        measurements = self.ranges
        sense_noise = self.sense_noise
        def measurement_prob(ranges):
            prob = 1.0
            for i,r in enumerate(ranges):
                prob*=localization_2d.gaussian(float(r), sense_noise, float(measurements[i]))
            return prob
            
        #self.particles = pf.resample(self.particles, sample_rangefinders, measurement_prob)
        self.particles, self.probabilities = self.pf.resample_add_random_points(self.particles, sample_rangefinders, measurement_prob, self.random_particles, (self.r*2-w/2, self.r*2-h/2), (w/2-self.r*2, h/2-self.r*2))
        #print len(self.particles)
        

    def synchronize(self):
        # rambling
        # print self.state
        #print self.x, self.y
        #print "step:", self.step
        self.step += 1
        if (self.ctr - self.resampling_t >= 10):
            #print "resampling"
            self.resampling_t = self.ctr
            self.resample(0, self.n_particles)

        for r in self.ranges:
            if r<self.close_threshold:
                self.state = ST_CLOSE_APPROACH
        wheels = None

        self.ctr += 1
        if self.ctr-self.dir_start>self.dir_change_t:
            self.dir_start = self.ctr
            self.rotate_t = random.randrange(1,20)
            self.state = random.randrange(2,4)
        
        if self.state == ST_GO_STRAIGHT:
            wheels = [FORWARD_SPEED, FORWARD_SPEED]
        elif self.state == ST_TURN_LEFT:
            if self.ctr - self.dir_start > self.rotate_t:
                self.state = ST_GO_STRAIGHT
            wheels = [FORWARD_SPEED, FORWARD_SPEED+1.]
        elif self.state == ST_TURN_RIGHT:
            wheels = [FORWARD_SPEED+1., FORWARD_SPEED]
            if self.ctr - self.dir_start > self.rotate_t:
                self.state = ST_GO_STRAIGHT
        elif self.state == ST_CLOSE_APPROACH:
            # front case
            if self.ranges[4] < self.close_threshold*2:
                wheels = [FORWARD_SPEED, FORWARD_SPEED]
            elif self.ranges[0] < self.close_threshold:
                wheels = [-TURN_SPEED, TURN_SPEED]
            elif (self.ranges[1] < self.close_threshold) or (self.ranges[2] < self.close_threshold):
                wheels = [-TURN_SPEED, TURN_SPEED]
            elif (self.ranges[7] < self.close_threshold) or (self.ranges[6] < self.close_threshold):
                wheels = [TURN_SPEED, -TURN_SPEED]

        if wheels!=None:
            self.wheels_omega = wheels
        self.move_particles()
            
localization_2d.objects2d.append([localization_2d.polygon(localization_2d.polygon_width, localization_2d.polygon_height), localization_2d.circular_obstacle(100, 100, 50), localization_2d.circular_obstacle(-200, -50, 30)])
localization_2d.objects2d.append([])
# obstacles here
radius = 20.


#names = ["first", "second", "third"]
#colors = [(0.1, 0, 0), (0, 0.1, 0), (0, 0, 0.1)]
names = ["first", "second"]
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
        r = loc_robot(posx-localization_2d.width/2,posy-localization_2d.height/2,radius, names[nctr], colors[nctr], 0.0, 0.1)
        r.polygon = localization_2d.objects2d[0]
        localization_2d.objects2d[1].append(r)
        nctr += 1

localization_2d.run(localization_2d.Screen)
