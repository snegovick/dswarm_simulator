import catmull_rom
import math

def point_to_point_dist(pt1, pt2):
    return math.sqrt((pt1[0]-pt2[0])**2+(pt1[1]-pt2[1])**2)

def find_closest_point(path, pt):
    points = []
    points.append(path[0])
    points.append(path[0])
    points.append(path[1])
    points.append(path[2])

    polynome, dp, coeffs = catmull_rom.interpolate_4pt(points, 0, 0)
    px = polynome(0, 0)
    py = polynome(0, 1)

    mdist = math.sqrt((px-pt[0])**2+(py-pt[1])**2)
    mt = 0
    mdp = (dp(0, 0), dp(0, 1))
    mpt = (px, py)

    for i, p in enumerate(path):
        points = []
        if i == 0:
            points.append(path[i])
            points.append(path[i])
            points.append(path[i+1])
            points.append(path[i+2])
        elif i == len(path)-1:
            points.append(path[i-2])
            points.append(path[i-1])
            points.append(path[i])
            points.append(path[i])

        elif i==len(path)-2:
            points.append(path[i-1])
            points.append(path[i])
            points.append(path[i+1])
            points.append(path[i+1])

        else:
            points.append(path[i-1])
            points.append(path[i])
            points.append(path[i+1])
            points.append(path[i+2])

            polynome, dp, coeffs = catmull_rom.interpolate_4pt(points, 0, 0)
            steps = 5
            
            px = polynome(0, 0)
            py = polynome(0, 1)

            for tt in range(steps):
                t = tt/float(steps)
                px = polynome(t, 0)
                py = polynome(t, 1)
                dist = math.sqrt((px-pt[0])**2+(py-pt[1])**2)
                if dist<mdist:
                    mdist = dist
                    mt = t
                    mdp = (dp(t, 0), dp(t, 1))
                    mpt = (px, py)

    return (mpt, mdp, mdist)

def cr_spline_closest_point(points, pt):
    polynome, dp, coeffs = catmull_rom.interpolate_4pt(points, 0, 0)
    steps = 5

    px = polynome(0, 0)
    py = polynome(0, 1)

    mdist = math.sqrt((px-pt[0])**2+(py-pt[1])**2)
    mt = 0
    mdp = (dp(0, 0), dp(0, 1))
    mpt = (px, py)
    for tt in range(steps):
        t = tt/float(steps)
        px = polynome(t, 0)
        py = polynome(t, 1)
        dist = math.sqrt((px-pt[0])**2+(py-pt[1])**2)
        if dist<mdist:
            mdist = dist
            mt = t
            mdp = (dp(t, 0), dp(t, 1))
            mpt = (px, py)

    return (mpt, mdp)
