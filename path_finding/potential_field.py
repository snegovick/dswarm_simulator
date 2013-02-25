import math
from map_utils import *

def build_potential_field_map(m_map, regression_coeff = 0.6, start_value = 1.0, threshold = 0.2):
    w = len(m_map[0])
    h = len(m_map)
    m_t_map = copy_map(m_map)

    # find all the obstacles and put these into initial front
    front = []

    neighbours = [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    for y, r in enumerate(m_map):
        for x, e in enumerate(r):
            if e == -1:
                m_t_map[y][x] = start_value
                front.append((x, y))

    visited = front[:]
    # propagate the field values
    value = start_value
    c = math.sqrt(2)

    while len(front)!=0:
        value = value*regression_coeff
        new_front = []
        if value<=threshold*start_value:
            break
        for p in front:
            for n in neighbours:
                nx = p[0]+n[0]
                ny = p[1]+n[1]
        
                if (nx>=w) or (nx<0) or (ny>=h) or (ny<0):
                    continue
                
                if (m_map[ny][nx] != 0):
                    continue

                if n[0]==0 or n[0] == 0:
                    t_c = 1.0/c
                else:
                    t_c = 1.0
                
                checked = (nx, ny) in visited
                if (checked and (m_t_map[ny][nx] >= value*t_c)):
                    continue

                m_t_map[ny][nx] = value*value*t_c
                if not checked:
                    visited.append((nx, ny))
                    new_front.append((nx, ny))

        front = new_front

    return m_t_map

if __name__=="__main__":
    m = [[0,-1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0,-1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0,-1, 0,-1,-1, 0, 0, 0, 0, 0, 0],
         [0,-1, 0,-1, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0,-1, 0, 0, 0, 0, 0, 0, 0]]

    nm = build_potential_field_map(m)
    print_map(nm)

