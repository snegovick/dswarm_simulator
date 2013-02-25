import math

def a_coeff(p, axis):
    #a = 1.5*(p[1][axis] - p[2][axis])+0.5*(p[3][axis]-p[0][axis])
    a = (-p[0][axis]+3*p[1][axis]-3*p[2][axis]+p[3][axis])/2.0
    return a

def b_coeff(p, axis):
    #b = -(2.5*p[1][axis] + 2*p[2][axis])-(0.5*p[3][axis]+p[0][axis])
    b = (2*p[0][axis]-5*p[1][axis]+4*p[2][axis]-p[3][axis])/2.0
    return b

def c_coeff(p, axis):
    # c = (p[2][axis]-p[0][axis])/2.0
    c = (-p[0][axis]+p[2][axis])/2.0
    return c

def d_coeff(p, axis):
    # return p[1][axis]
    return p[1][axis]


def interpolate_4pt(points, start_angle, end_angle):
    a = (a_coeff(points, 0), a_coeff(points, 1))
    b = (b_coeff(points, 0), b_coeff(points, 1))
    c = (c_coeff(points, 0), c_coeff(points, 1))
    d = (d_coeff(points, 0), d_coeff(points, 1))
    return (lambda t, axis: (((a[axis]*t+b[axis])*t+c[axis])*t+d[axis]), 
            lambda t, axis: (3.0*a[axis]*t*t+2.0*b[axis]*t+c[axis]), (a, b, c, d))
    
    
if __name__=="__main__":    
    import Image, ImageDraw
    import sys
    sys.path.append("../emath")
    import emath
    
    scale = 50
    size = 2000
    offsety = 200
    offsetx = 400
    pt = (30*scale-offsetx, 20*scale-offsety)

    points = [(34.0, 21.0), (33.41471967399936, 20.65689705441718), (32.83803702998342, 20.261398758636084), (32.232883196591345, 19.86294517447802), (31.579010525252198, 19.48298870353226), (30.887667250620147, 19.186173774761993), (30.132264648735838, 18.94582617606274), (29.515372979934906, 18.62975286799863), (28.988207825356778, 18.212347607765757), (28.528147649549737, 17.700527009882283), (28.14069722325448, 17.064846910533674), (27.778024560134764, 16.34779514601751), (27.428705034492292, 15.7403928515697), (27.085690793784263, 15.112705885312405), (26.702997345581604, 14.512675193371987), (26.226230823353532, 13.998328136632143), (25.653194133024556, 13.575324055199712), (24.93068958488625, 13.298155500092376), (24.060198781332673, 13.162182869839926), (23.07981411355464, 13.113270418895363), (22.034798376442794, 13.059304336185505), (21.210654485888092, 12.896376937507991), (20.65784321318701, 12.530536344910999), (20.18923431919627, 11.986045245657666), (19.815536627988532, 11.312904080829778), (19.517539162441505, 10.678376662093392), (19.3446668602152, 9.961492755437522), (19.36687251371859, 9.22820858615211), (19.59714424060841, 8.55582075285236), (19.98160131682331, 7.968650706758493), (20.071653606639444, 7.065703430778836), (20.066460881046545, 6.122971525155615), (19.99816074309545, 5.460578730489387), (19.762267430516545, 4.833088102662134), (19.0, 4.0)]
    p2 = [(p[0]*scale-offsetx, p[1]*scale-offsety) for p in points]
    print p2
    
    im = Image.new('RGBA', (size, size), (255, 255, 255, 255))
    draw = ImageDraw.Draw(im)
    
    draw.ellipse([pt[0]-5, pt[1]-5, pt[0]+5, pt[1]+5], fill=(0,0,255))

    for i, p in enumerate(p2[1:-2]):
        ti = i + 1
        points = []
        draw.ellipse((p[0]-5, p[1]-5, p[0]+5, p[1]+5), fill=(255, 0, 0))
        points.append(p2[ti-1])
        points.append(p2[ti])
        points.append(p2[ti+1])
        points.append(p2[ti+2])

        polynome, dp, coeffs = interpolate_4pt(points, 0, 0)

        prev_pt = None
        nsteps = 100

        mdist = 1000
        mtt = 0
        mpt = (0,0)

        for t in range(0, nsteps+1, 1):
            tt = t/float(nsteps)

            draw.line([p[0], p[1], p[0]+dp(tt, 0), p[1]+dp(tt, 1)], fill=(0, 255, 0))
            #print math.sqrt(dp(tt, 0)**2+dp(tt, 1)**2)


            px = polynome(tt, 0)
            py = polynome(tt, 1)

            dist = math.sqrt((px-pt[0])**2+(py-pt[1])**2)
            if dist<mdist:
                mdist = dist
                mtt = tt
                mpt = (px, py)

            #print tt, ":", px, py

            if prev_pt!=None:
                draw.line([prev_pt[0], prev_pt[1], px, py], fill=(0,0,0))
            prev_pt = (px, py)

        draw.line([pt[0], pt[1], mpt[0], mpt[1]], fill=(255,255,0))

    im.save("out.png", "PNG")
