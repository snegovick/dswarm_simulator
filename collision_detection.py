import math

class circle(object):
    def __init__(self, x, y, r):
        self.x = x
        self.y = y
        self.r = r

class aabb(object):
    def __init__(self, left, right, top, bottom):
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom

def circle_to_circle(c1, c2):
    if (c1.x-c2.x)**2+(c1.y-c2.y)**2<=(c1.r+c2.r)**2:
        return (True,)
    return (False,)

def circle_to_circle_plain(c1x, c1y, c1r, c2x, c2y, c2r):
    if (c1x-c2x)**2+(c1y-c2y)**2<=(c1r+c2r)**2:
        return (True,)
    return (False,)

def circle_to_aabb(c, a):
    # cases
    cases = [(c.x+c.r, c.y), (c.x-c.r, c.y), (c.x, c.y+c.r), (c.x, c.y-c.r)]
    for x, y in cases:
        if (x>=a.left or x<=a.right) and (y>=a.bottom or y<=a.top):
            return (True,)
    return (False,)

def circle_to_aabb_inverse(c, a):
    # cases
    cases = [(c.x+c.r, c.y), (c.x-c.r, c.y), (c.x, c.y+c.r), (c.x, c.y-c.r)]
    for x, y in cases:
        if (x<=a.left or x>=a.right) and (y<=a.bottom or y>=a.top):
            return (True,)
    return (False,)

def circle_to_aabb_inverse_plain(c, a):
    # cases
    cx = c[0]
    cy = c[1]
    cr = c[2]
    cases = [(cx+cr, cy), (cx-cr, cy), (cx, cy+cr), (cx, cy-cr)]
    for x, y in cases:
        if (x<=a.left or x>=a.right) or (y>=a.bottom or y<=a.top):
            return (True,)
    return (False,)        

epsilon = 0.001
def orientedline_to_inverse_aabb_dist(lx, ly, angle, linelen, a):
    distances = []
    while angle>2*math.pi:
        angle -= 2*math.pi

    while angle<0:
        angle+=2*math.pi

    q = int(angle/(math.pi/2.))
    #print "angle, q:", angle, q
    #print "top:", a.top, "bottom:", a.bottom, "left:", a.left, "right:", a.right, "lx:", lx, "ly:", ly

    check = []
    if abs(angle)<epsilon:
        check = [0,]
    elif abs(angle-math.pi/2.)<epsilon:
        check = [1,]
    elif abs(angle-math.pi)<epsilon:
        check = [2,]
    elif abs(angle-3*math.pi/2.)<epsilon:
        check = [3,]
    elif q == 0:
        check = [0, 1]
    elif q == 1:
        check = [1, 2]
    elif q == 2:
        check = [2, 3]
    elif q == 3:
        check = [3, 0]


    for c in check:
        if c == 0:
            dist = a.right - lx
            if ((abs(angle-math.pi/2.)) > epsilon) and ((abs(angle-3.*math.pi/2.)) > epsilon):
                dist /= math.cos(angle)
            distances.append(abs(dist))
        elif c == 3:
            dist = a.top - ly
            if (abs(angle) > epsilon) and ((abs(angle-math.pi)) > epsilon):
                dist /= math.sin(angle)
            distances.append(abs(dist))
        elif c == 2:
            dist = lx - a.left
            if ((abs(angle-math.pi/2.)) > epsilon) and ((abs(angle-3.*math.pi/2.)) > epsilon):
                dist /= math.cos(angle)
            distances.append(abs(dist))
        elif c == 1:
            dist = ly - a.bottom
            if (abs(angle) > epsilon) and ((abs(angle-math.pi)) > epsilon):
                dist /= math.sin(angle)
            distances.append(abs(dist))

    #print distances
    d = min(distances)
    
    if d <= linelen:
        return d

    return linelen

def ray_dist_to_circle_plain(cx, cy, r, rx, ry, alpha, rlen_max):
    x0 = cx-rx
    y0 = cy-ry
    
    d2 = r**2-(y0*math.cos(alpha)-x0*math.sin(alpha))**2
    if d2<0:
        return (False, rlen_max)
    t = y0*math.sin(alpha)+x0*math.cos(alpha)
    d = math.sqrt(d2)
    s = [t+d, t-d]
    ms = min(s)
    if ms<rlen_max and ms>=0:
        return (True, ms)
    return (False, rlen_max)

