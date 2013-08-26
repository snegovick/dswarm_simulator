neighbours = [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

def print_map(m):
    for l in m:
        out = ""
        for e in l:
            out+="%0.1f\t" % e
        print out
    print ""

def copy_map(m):
    t_m = []
    for l in m:
        t_m.append(l[:])
    return t_m

def show_path(m, path):
    t_m = copy_map(m)
    for i, p in enumerate(path):
        t_m[p[1]][p[0]] = len(path) - i
    return t_m

def translate_coords_to_cells(x, y, w, h, x_cells, y_cells):
    x_w = w/x_cells
    y_w = h/y_cells

    x_cell = int(x/x_w)
    y_cell = int(y/y_w)

    return x_cell, y_cell

if __name__ == "__main__":
    w = 10
    h = 10
    x = 5.9
    y = 2
    x_cells = 10
    y_cells = 10

    print "translating", x,y

    print translate_coords_to_cells(x, y, w, h, x_cells, y_cells)
