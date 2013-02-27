import localization_2d
import particle_filter as pf
import collision_detection as cd
from path_finding.catmull_rom import interpolate_4pt
from path_finding.path_utils import find_closest_point, cr_spline_closest_point, point_to_point_dist

import random
import math
import copy

from forkmap import map

ppmm = localization_2d.pixel_per_mm
w = localization_2d.polygon_width
h = localization_2d.polygon_height


class cf_robot(localization_2d.robot):
    def __init__(self, x, y, r, name, color, theta, sense_noise, radio_address):
        super(cf_robot,self).__init__(x, y, r, name, color, theta, sense_noise, radio_address)
        self.path = []
        self.current_pt = None
        self.robot_path = []
        self.omega_min = 0.8
        self.prev_error = None

    def draw_dist(self, cr):
        if self.current_pt != None:
            cr.move_to(self.x+w/2, self.y+h/2)
            cr.line_to(self.current_pt[0], self.current_pt[1])
            cr.arc(self.current_pt[0], self.current_pt[1], 5/ppmm, 0.0, 2*math.pi)
            cr.stroke()


    def draw_curve(self, cr):
        if len(self.robot_path)>4:

            prev_p = self.robot_path[0]

            pts = self.robot_path
            for i, p in enumerate(self.robot_path[0:-1]):
                ti = i

                points = []
                if ti == 0:
                    points.append(pts[ti])
                else:
                    points.append(pts[ti-1])
                points.append(pts[ti])
                points.append(pts[ti+1])
                if ti>=len(self.robot_path)-2:
                    points.append(pts[ti+1])
                else:
                    points.append(pts[ti+2])


                polynome, dp, coeffs = interpolate_4pt(points, 0, 0)


                steps = 100
                for tt in range(steps+1):
                    t = tt/float(steps)
                    px = polynome(t, 0)
                    py = polynome(t, 1)
                    
                    cr.move_to(prev_p[0],prev_p[1])
                    cr.line_to(px, py)
                    cr.stroke()
                    prev_p = (px, py)


    def draw_path(self, cr):
        self.robot_path = self.path
        self.draw_dist(cr)

        for p in self.robot_path:
            cr.arc(p[0], p[1], 5/ppmm, 0.0, 2*math.pi)
            cr.stroke()

        self.draw_curve(cr)

    def draw(self, cr):
        self.draw_path(cr)
        super(cf_robot,self).draw(cr)

    def pt_dist(self, t_x, t_y):
        return math.sqrt((self.x-t_x)**2 + (self.y-t_y)**2)

    def synchronize(self):
        if self.robot_path!=[] and len(self.robot_path)>4:
            path = [(self.x+0.1+w/2, self.y+0.1+h/2)]
            path+=self.robot_path
            pt, dp, d = find_closest_point(path, (self.x+30*math.cos(self.theta)+w/2, self.y+30*math.sin(self.theta)+h/2))
            pt = (pt[0], pt[1])
            self.current_pt = pt #self.robot_path[idx]
            # print "pt:", pt, "dp:", dp
            
            theta = self.theta if self.theta>0 else 2*math.pi+self.theta
            alpha = math.atan2(dp[1], dp[0])
            alpha = alpha if alpha>0 else 2*math.pi+alpha

            gamma = theta-alpha
            zeta = gamma

            # if zeta>2*math.pi:
            #     while zeta>2*math.pi:
            #         zeta-=2*math.pi
            # elif zeta<-2*math.pi:
            #     while zeta<-2*math.pi:
            #         zeta+=2*math.pi

            if zeta>math.pi:
                zeta = 2*math.pi-zeta
            elif zeta<=-math.pi:
                zeta = 2*math.pi+zeta

#            if abs(zeta)-math.pi<0.1:
                

            if abs(zeta)>math.pi/3.:
                sign = gamma/abs(gamma)
                self.wheels_omega = (-sign*self.omega_min/2.0, sign*self.omega_min/2.0)
            else:
                v1 = [math.cos(self.theta), math.sin(self.theta)]
                v2 = [self.x+w/2-pt[0], self.y+h/2-pt[1]]
                v2len = math.sqrt(v2[0]**2+v2[1]**2)
                v2[0] = v2[0]/v2len
                v2[1] = v2[1]/v2len

                # print "v1:", v1, "v2:", v2

                d_sign = v1[0]*v2[1]-v1[1]*v2[0]
                # print "d_sign:", d_sign
                d_sign = 1 if d_sign>0 else -1

                e = d

                if self.prev_error==None:
                    self.prev_error = e
                    de = 0
                else:
                    de = e - self.prev_error
                    self.prev_error = e

                delta = 0.02*d*d_sign# - 0.5*de
                delta = 3*delta
                self.wheels_omega = (self.omega_min-delta, self.omega_min+delta)
                # print "delta:", delta, "de:", de
            # print "gamma:", gamma, "zeta:", zeta

        else:
            self.current_pt = None
            self.wheels_omega = (0,0)
            self.prev_error = None
                      
            

if __name__=="__main__":
    localization_2d.objects2d.append([localization_2d.polygon(localization_2d.polygon_width, localization_2d.polygon_height), 
                                      localization_2d.circular_obstacle(100, 100, 50), 
                                      localization_2d.circular_obstacle(-200, -50, 30),
                                      localization_2d.circular_obstacle(150, -100, 50),])
    localization_2d.objects2d.append([])
    # obstacles here
    radius = 20.


    #names = ["first", "second", "third"]
    #colors = [(0.1, 0, 0), (0, 0.1, 0), (0, 0, 0.1)]
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
            r = cf_robot(posx-localization_2d.width/2,posy-localization_2d.height/2,radius, names[nctr], colors[nctr], 0.0, 0.1)
            r.polygon = localization_2d.objects2d[0]
            localization_2d.objects2d[1].append(r)
            nctr += 1

    localization_2d.run(localization_2d.Screen)
