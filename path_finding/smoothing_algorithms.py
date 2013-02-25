import math
from map_utils import *

def calc_field_grad(m, pt):
    w = len(m[0])
    h = len(m)
    
    if pt[0]>=w or pt[0]<0:
        return None

    if pt[1]>=h or pt[1]<0:
        return None

    px_s = pt[0]-1
    px_e = pt[0]+1
    
    if px_s>=w or px_s<0:
        px_s = pt[0]

    if px_e>=w or px_e<0:
        px_e = pt[0]

    dx = m[pt[1]][px_e] - m[pt[1]][px_s]

    py_s = pt[1]-1
    py_e = pt[1]+1
    
    if py_s>=w or py_s<0:
        py_s = pt[1]

    if py_e>=w or py_e<0:
        py_e = pt[1]

    dy = m[py_e][pt[0]] - m[py_s][pt[0]]
    return (dx, dy)

def smooth_path(path):
    y = [(float(p[0]), float(p[1])) for p in path]
    x = [(float(p[0]), float(p[1])) for p in path]

    alpha = 0.01
    beta = 0.2
    tolerance = 0.1
    change = tolerance
    count = 0
    while change>=tolerance:
        count += 1
        change = 0.0
        n_y = [y[0]]
        for i in range(1, len(y)-1):
            t = (y[i][0], y[i][1])
            t_x = y[i][0] + alpha*(2.0*(x[i][0]-y[i][0]))
            t_y = y[i][1] + alpha*(2.0*(x[i][1]-y[i][1]))

            dx1 = (y[i][0]-y[i-1][0])
            dx2 = (y[i+1][0]-y[i][0])

            dy1 = (y[i][1]-y[i-1][1])
            dy2 = (y[i+1][1]-y[i][1])

            vect_1_len = math.sqrt(dx1**2+dy1**2)
            vect_2_len = math.sqrt(dx2**2+dy2**2)

            # print "vector 1 length:", vect_1_len, "(", "dx1:", dx1, "dy1:", dy1, ")", "vector 2 length:", vect_2_len, "(", "dx2:", dx2, "dy2:", dy2, ")"

            total_len = vect_1_len*vect_2_len
            if total_len == 0:
                dx1 = 0
                dy1 = 0
                total_len = 1

            #t2_x = t_x - beta*(1.0-(dx1*dx2)/(total_len))
            #t2_y = t_y - beta*(1.0-(dy1*dy2)/(total_len))

            #delta_x = beta*(1.0-(y[i+1][0]*y[i-1][0])/total_len)
            #delta_y = beta*(1.0-(y[i+1][1]*y[i-1][1])/total_len)

            delta_x = beta*((y[i-1][0] + y[i+1][0] - 2.*y[i][0])/total_len)
            delta_y = beta*((y[i-1][1] + y[i+1][1] - 2.*y[i][1])/total_len)

            t2_x = t_x + delta_x
            t2_y = t_y + delta_y

            # print "delta x:", delta_x, "delta y:", delta_y

            n_y.append((t2_x, t2_y))
            # print "t_x:", t_x, "t_y:", t_y, "t2_x:", t2_x, "t2_y:", t2_y, "new y:", n_y[-1], "old y:", t

            change += abs(t[0] - n_y[-1][0])+abs(t[1] - n_y[-1][1])
        print "change:", change
        n_y.append(y[-1])
        y = n_y
        # break

    print "smoother took", count, "cycles"
    
    return y

def smooth_path_with_field(path, field_map, units_per_cell):
    y = [(float(p[0]), float(p[1])) for p in path]
    x = [(float(p[0]), float(p[1])) for p in path]

    m = field_map
    upc = units_per_cell

    alpha = 0.01
    beta = 0.2
    gamma = 0.25
    tolerance = 0.1

    step_coeff = 0.8

    change = tolerance
    count = 0
    while change>=tolerance:
        count += 1
        change = 0.0
        n_y = [y[0]]
        for i in range(1, len(y)-1):
            t = (y[i][0], y[i][1])
            t_x = y[i][0] + alpha*(2.0*(x[i][0]-y[i][0]))
            t_y = y[i][1] + alpha*(2.0*(x[i][1]-y[i][1]))

            dx1 = (y[i][0]-y[i-1][0])
            dx2 = (y[i+1][0]-y[i][0])

            dy1 = (y[i][1]-y[i-1][1])
            dy2 = (y[i+1][1]-y[i][1])

            vect_1_len = math.sqrt(dx1**2+dy1**2)
            vect_2_len = math.sqrt(dx2**2+dy2**2)

            # print "vector 1 length:", vect_1_len, "(", "dx1:", dx1, "dy1:", dy1, ")", "vector 2 length:", vect_2_len, "(", "dx2:", dx2, "dy2:", dy2, ")"

            total_len = vect_1_len*vect_2_len
            if total_len == 0:
                dx1 = 0
                dy1 = 0
                total_len = 1

            #t2_x = t_x - beta*(1.0-(dx1*dx2)/(total_len))
            #t2_y = t_y - beta*(1.0-(dy1*dy2)/(total_len))

            #delta_x = beta*(1.0-(y[i+1][0]*y[i-1][0])/total_len)
            #delta_y = beta*(1.0-(y[i+1][1]*y[i-1][1])/total_len)

            delta_x = beta*((y[i-1][0] + y[i+1][0] - 2.*y[i][0])/total_len)
            delta_y = beta*((y[i-1][1] + y[i+1][1] - 2.*y[i][1])/total_len)

            t_x = t_x + delta_x
            t_y = t_y + delta_y

            print "i:", i, type(y), type(m)
            pt_x = int(y[i][0])
            pt_y = int(y[i][1])
            print y[i][0], y[i][1], "->", pt_x, pt_y, "upc:", upc
            dx, dy = calc_field_grad(m, (pt_x, pt_y))

            print "dx, dy:", (dx, dy)

            sy = (1 if dy>0 else -1)
            sx = (1 if dx>0 else -1)
            print "m at", pt_x, pt_y,":",m[pt_y][pt_x]
            dx = gamma*sx*m[pt_y][pt_x]
            dy = gamma*sy*m[pt_y][pt_x]
            print "dx, dy:", (dx, dy)

            t_x = t_x - dx
            t_y = t_y - dy

            # print "delta x:", delta_x, "delta y:", delta_y

            n_y.append((t_x, t_y))
            # print "t_x:", t_x, "t_y:", t_y, "t2_x:", t2_x, "t2_y:", t2_y, "new y:", n_y[-1], "old y:", t

            change += abs(t[0] - n_y[-1][0])+abs(t[1] - n_y[-1][1])
        print "change:", change
        n_y.append(y[-1])
        y = n_y
        # break
        alpha = alpha*step_coeff
        beta = beta*step_coeff
        gamma = gamma*step_coeff

    print "smoother took", count, "cycles"
    
    return y

if __name__=="__main__":
    m = [[   0, 0.1, 0.2, 0.3],
         [ 0.1, 0.2, 0.3, 0.4],
         [ 0.2, 0.3, 0.4, 0.5],
         [ 0.3, 0.4, 0.5, 0.6]]

    path = [(0, 3), (1,3), (2, 3), (2, 2), (2, 1), (2, 0), (3, 0)]

    print "field gradient:", calc_field_grad(m, (1, 1))

    
    
    orig_path = path[:]

    path = smooth_path_with_field(path, m, 1)
    print "after:"
    for p in path:
        print p

    import Image, ImageDraw

    scale = 50
    size = 2000
    offset = 10

    im = Image.new('RGBA', (size, size), (255, 255, 255, 255))
    draw = ImageDraw.Draw(im)

    pt_size = size/100
    
    for p in path:
        draw.ellipse((p[0]*scale+offset-pt_size/2, p[1]*scale+offset-pt_size/2, p[0]*scale+offset+pt_size/2, p[1]*scale+offset+pt_size/2), fill=(255, 0, 0, 100))

    for p in orig_path:
        draw.ellipse((p[0]*scale+offset-pt_size/2, p[1]*scale+offset-pt_size/2, p[0]*scale+offset+pt_size/2, p[1]*scale+offset+pt_size/2), fill=(0, 0, 0, 100))


    im.save("out.png", "PNG")
