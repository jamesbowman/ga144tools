import numpy as np
import time
import Image

class S89(object):
    def __init__(self):
        pass

    @classmethod
    def fromfloat(cls, x):
        v = cls()
        v.c = (512 * x).astype(np.int32)
        return v

class vec3():
    def __init__(self, x, y, z):
        (self.x, self.y, self.z) = (x, y, z)
    def __mul__(self, other):
        return vec3(self.x * other, self.y * other, self.z * other)
    def __add__(self, other):
        return vec3(self.x + other.x, self.y + other.y, self.z + other.z)
    def __sub__(self, other):
        return vec3(self.x - other.x, self.y - other.y, self.z - other.z)
    def dot(self, other):
        return (self.x * other.x) + (self.y * other.y) + (self.z * other.z)
    def __abs__(self):
        return self.dot(self)
    def norm(self):
        mag = np.sqrt(abs(self))
        return self * (1.0 / np.where(mag == 0, 1, mag))
    def components(self):
        return (self.x, self.y, self.z)
rgb = vec3

(w, h) = (128, 128)         # Screen size
L = vec3(5, 5., -10)        # Point light position
E = vec3(0., 0, 0)     # Eye position
FARAWAY = 1.0e39            # an implausibly huge distance
gen = 0

def raytrace(D, scene, bounce = 0):
    # (0,0,0) is the ray origin, D is the normalized ray direction
    # scene is a list of Sphere objects (see below)
    # bounce is the number of the bounce, starting at zero for camera rays

    distances = [s.intersect(D) for s in scene]
    nearest = reduce(np.minimum, distances)
    color = rgb(0, 0, 0)
    for (s, d) in zip(scene, distances):
        cc = s.light(D, d, scene, bounce) * (nearest != FARAWAY) * (d == nearest)
        color += cc
        _rgb = [Image.fromarray((255 * np.clip(c, 0, 1).reshape((h, w))).astype(np.uint8), "L") for c in cc.components()]
        global gen
        Image.merge("RGB", _rgb).save("p%02d.png" % gen)
        gen += 1
    return color

class Sphere:
    def __init__(self, center, r, diffuse, mirror = 0.5):
        self.c = center
        self.r = r
        self.diffuse = diffuse
        self.mirror = mirror

    def intersect(self, D):
        b = 2 * D.dot(self.c * -1)
        c = abs(self.c) - (self.r * self.r)
        disc = (b ** 2) - (4 * c)
        sq = np.sqrt(np.maximum(0, disc))
        h0 = (-b - sq) / 2
        h1 = (-b + sq) / 2
        h = np.where((h0 > 0) & (h0 < h1), h0, h1)

        pred = (disc > 0) & (h > 0)
        return np.where(pred, h, FARAWAY)

    def diffusecolor(self, M):
        return self.diffuse

    def light(self, D, d, scene, bounce):
        M = (D * d)                         # intersection point
        N = (M - self.c) * (1. / self.r)        # normal
        toL = (L - M).norm()                    # direction to light
        toO = (E - M).norm()                    # direction to ray origin
        nudged = M + N * .0001                  # M nudged to avoid itself

        # Lambert shading (diffuse)
        lv = np.maximum(N.dot(toL), 0)
        color = self.diffusecolor(M) * lv

        # Blinn-Phong shading (specular)
        phong = N.dot((toL + toO).norm())
        color += rgb(1.25, .75, .5) * np.power(np.clip(phong, 0, 1), 16)
        return color

class CheckeredSphere(Sphere):
    def diffusecolor(self, M):
        checker = ((M.x * 2).astype(int) % 2) == ((M.z * 2).astype(int) % 2)
        return self.diffuse * checker

scene = [
    Sphere(vec3(0, 0, 2), 1.3, rgb(0, 0, 1)),
    # Sphere(vec3(-.2, .0, .5), .2, rgb(1, 0, 0)),
    # Sphere(vec3(1, 1, 2), .6, rgb(1, 0, 0)),
    ]

r = float(w) / h
# Screen coordinates: x0, y0, x1, y1.
S = (-1., 1., 1., -1.)
x = np.tile(np.linspace(S[0], S[2], w), h)
y = np.repeat(np.linspace(S[1], S[3], h), w)

x8 = S89.fromfloat(x)
y8 = S89.fromfloat(y)
print y8.c

t0 = time.time()
Q = vec3(x, y, 1)
color = raytrace(Q.norm(), scene)
print "Took", time.time() - t0

if 0:
    dm = np.array([[0,.5],[.75,.25]]) + .125
    dither = np.tile(dm, (w / 2, h / 2)).flatten()
else:
    dm = np.array([ [0,8,2,10], [12,4,14,6], [3,11,1,9], [15,7,13,5] ])/16. + (1./32)
    dither = np.tile(dm, (w / 4, h / 4)).flatten()

def unquant(c):
    # return 255 * np.clip(c, 0, 1)
    gt = c > dither
    return 255 * gt

rgb = [Image.fromarray((unquant(c).reshape((h, w))).astype(np.uint8), "L") for c in color.components()]
Image.merge("RGB", rgb).save("fig.png")
