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
