import math
from map_utils import *


def find_path_wave_lambda(params, heuristic, variant = 4):
    visited = [params["start_point"]]
    w = len(params["m_map"][0])
    h = len(params["m_map"])
    field_map = params["field_map"]
    start_point = params["start_point"]
    end_point = params["end_point"]
    m_map = params["m_map"]

    m_t_map = copy_map(params["m_map"])

    c = math.sqrt(2.0)
    neighbours = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    t_coeff = [1, 1, 1, 1]
    if variant == 8:
        neighbours += [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        t_coeff += [c, c, c, c]

    front = [start_point]
    next_front = []

    step = 1
    m_t_map[start_point[1]][start_point[0]] = step

    while True:
        step += 1
        for p in front:
            for n, t_c in zip(neighbours, t_coeff):
                nx = p[0]+n[0]
                ny = p[1]+n[1]

                if (nx>=w) or (nx<0) or (ny>=h) or (ny<0):
                    continue
                
                if (m_map[ny][nx] != 0):
                    continue
                
                if ((nx, ny) in visited):
                    continue
                
                # print n, t_c

                m_t_map[ny][nx] = heuristic({"step": step, "x": nx, "y": ny, "t_c": t_c, "params": params})
                visited.append((nx, ny))
                next_front.append((nx, ny))

        if end_point in next_front:
            break

        if next_front == []:
            return None

        front = next_front[:]
        next_front = []

    # print "back_prop"
    # print print_map(m_t_map)


    p = end_point
    next_point = p
    min_value = (step+1)*c
    path = [p]
    while True:
        if p == start_point:
            break

        for n in neighbours:
            nx = p[0]+n[0]
            ny = p[1]+n[1]
            # print "checking:", nx, ny, "min_value:", min_value
            if (nx>=w) or (nx<0) or (ny>=h) or (ny<0):
                # print "out of boundaries"
                continue
            
            if (m_map[ny][nx] < 0):
                # print "is obstacle"
                continue

            # print "value:", m_t_map[ny][nx]

            if ((min_value == None) and (m_t_map[ny][nx] != 0) and ((nx, ny) not in path)):
                min_value = m_t_map[ny][nx]
                next_point = (nx, ny)
                
            
            if ((m_t_map[ny][nx] < min_value) and (m_t_map[ny][nx] != 0) and ((nx, ny) not in path)):
                # print "considered:", m_t_map[ny][nx], "(", nx, ",", ny, ")", "coords:", n[0], ",", n[1]
                next_point = (nx, ny)
                min_value = m_t_map[ny][nx]
        min_value = None
        p = next_point
        next_point = None
        # print "took:", p
        if p!=None:
            path.append(p)
            # print path
        else:
            print "Didnt find the point"
            path = None
            break
    return path

def find_path_wave(m_map, start_point, end_point):
    params = {"m_map": m_map, "start_point": start_point, "end_point": end_point}
    return find_path_wave_lambda(params, lambda p: p["step"]*p["t_c"], 4)

def find_path_wave8(m_map, start_point, end_point):
    params = {"m_map": m_map, "start_point": start_point, "end_point": end_point}
    return find_path_wave_lambda(params, lambda p: p["step"]*p["t_c"])

def find_path_wave_heuristic8(m_map, field_map, start_point, end_point, field_value_coeff=6.0, distance_coeff=0.01, step_coeff=1.0):
    params = {"m_map": m_map, "start_point": start_point, "end_point": end_point, "field_map": field_map, "field_value_coeff": field_value_coeff, "distance_coeff": distance_coeff, "step_coeff": step_coeff}

    def heuristic(p):
        x = p["x"]
        y = p["y"]
        ep = p["params"]["end_point"]
        return (p["step"]*p["t_c"]*p["params"]["step_coeff"]+
        p["params"]["field_value_coeff"]*p["params"]["field_map"][y][x]+
        p["params"]["distance_coeff"]*math.sqrt((ep[0]-x)**2+(ep[1]-y)**2))
    return find_path_wave_lambda(params, heuristic)


def throw_away_points(y):
    n_y = [y[0]]
    for i in range(1, len(y)):
        if math.sqrt((n_y[-1][0]-y[i][0])**2 + (n_y[-1][1]-y[i][1])**2)>1.:
            n_y.append(y[i])
    n_y.append(y[-1])
    return n_y    

if __name__=="__main__":
    m = [[0,-1, 0, 0, 0, 0],
         [0,-1, 0, 0, 0, 0],
         [0,-1, 0, 0, 0, 0],
         [0,-1, 0,-1, 0, 0],
         [0, 0, 0,-1, 0, 0],
         [0,-1, 0, 0, 0, 0],
         [0,-1, 0,-1, 0, 0]]

    start = (0,0)
    end = (5,6)
    path = find_path_wave8(m, start, end)
    print path
    print_map(show_path(m, path))

    print "original map:"
    print_map(m)
    from potential_field import build_potential_field_map
    pf = build_potential_field_map(m)

    print "potential map:"
    print_map(pf)

    path = find_path_wave_heuristic8(m, pf, start, end)
    
    print "path:"
    print_map(show_path(m, path))

    print "path_smoother test:"
    path = [(0, 0),
            (0, 1),
            (0, 2),
            (1, 2),
            (2, 2),
            (3, 2),
            (4, 2),
            (4, 3),
            (4, 4)]

    path = [(0,0), (0,1), (1,1)]

    path = [(20, 18), (20, 17), (20, 16), (20, 15), (20, 14), (20, 13), (20, 12), (20, 11), (20, 10), (20, 9), (21, 9), (22, 9), (23, 9), (24, 9), (25, 9), (26, 9), (27, 9), (28, 9), (29, 9)]
    print "before:"
    for p in path:
        print p


    orig_path = path[:]

    from smoothing_algorithms import smooth_path

    path = smooth_path(path)
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
