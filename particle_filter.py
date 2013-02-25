import random
import math

def init_particles(start, end, n_particles):

    particles = []

    xs, ys = start
    xe, ye = end
    for p in range(n_particles):
            #print p
        posx = random.randrange(xs, xe)
        posy = random.randrange(ys, ye)
        angle = random.randrange(0, 360)*math.pi/180.
        particles.append((posx, posy, angle))
    return particles

def init_particles_oriented(start, end, orientation, n_particles):

    particles = []

    xs, ys = start
    xe, ye = end
    for p in range(n_particles):
            #print p
        posx = random.randrange(xs, xe)
        posy = random.randrange(ys, ye)
        angle = random.gauss(orientation*180.0/math.pi, 30)*math.pi/180.
        particles.append((posx, posy, angle))
    return particles

def move_particles(particles, update_position):
    def move_particle(p):
        return update_position(p)
            
    particles = map(move_particle, particles)
    return particles

def resample(particles, sample_rangefinders, measurement_prob):
    ranges = map(sample_rangefinders, particles)
    w_vect = map(measurement_prob, ranges)
        
    # resampling wheel
    p3 = []
    N = len(particles)
    index = int(random.randrange(0, N))
    beta = 0.0
    mw = max(w_vect)
    print mw
    for i in range(N):
        beta += random.random()*2.0*mw
        while beta>w_vect[index]:
            beta -= w_vect[index]
            index = (index+1)%N
        p3.append(particles[index])
    return p3

class particle_filter:
    def __init__(self):
        self.average = 0.0
        self.filter_values = [0.0]*20
        self.filter_position = 0
        self.filter_started = False
        self.random_particles_threshold = 10**(-23)
        self.steps_since_last_randomization = 0
        self.random_steps = len(self.filter_values)

    def resample_add_random_points(self, particles, sample_rangefinders, measurement_prob, number_of_random_points, start, end):

        if not self.filter_started:
            if self.filter_position == len(self.filter_values):
                self.filter_started = True

        if self.filter_position >= len(self.filter_values):
            self.filter_position = 0

        ranges = map(sample_rangefinders, particles)
        w_vect = map(measurement_prob, ranges)

        mw = max(w_vect)

        if self.filter_started:
            self.average -= self.filter_values[self.filter_position]

        self.average += mw/len(self.filter_values)
        self.filter_values[self.filter_position] = mw/len(self.filter_values)
        self.filter_position += 1
        diff = abs(self.average - mw)
        print "average:", self.average, "mw:", mw, "diff:", ("n/a" if not self.filter_started else diff)

        N = len(particles)    
        add_random_points = False
        self.steps_since_last_randomization += 1
        if (diff >= self.random_particles_threshold) and self.filter_started and (self.steps_since_last_randomization > self.random_steps):
            print "randomize"
            self.steps_since_last_randomization = 0
            add_random_points = True
            N = len(particles)-number_of_random_points


        # resampling wheel
        p3 = []
        index = int(random.randrange(0, N))
        beta = 0.0

        # print mw
        for i in range(N):
            beta += random.random()*2.0*mw
            while beta>w_vect[index]:
                beta -= w_vect[index]
                index = (index+1)%N
            p3.append(particles[index])

        if add_random_points:
            tparticles = init_particles(start, end, number_of_random_points)
            for tp in tparticles:
                p3.insert(random.randrange(len(p3)), tp)

        return p3, w_vect

if __name__ == "__main__":
    r = 10
    lw = 10
    width = 1000
    height = 500
    p = init_particles((lw+r, lw+r), (width-lw-r, height-lw-r), 100000)
    
