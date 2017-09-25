import numpy as np
import Image
import math

def ch(cc):
    return rgb(*[int(cc[i:i+2], 16) / 255. for i in (0,2,4)])

class S89(object):
    def __init__(self, c = None):
        if c is not None:
            self.c = c.astype(np.int32)

    @classmethod
    def fromfloat(cls, x):
        v = cls()
        v.c = (512 * x).astype(np.int32)
        return v

    @classmethod
    def k(cls, f):
        v = cls()
        v.c = np.full(16384, int(512 * f), np.int32)
        return v

    def tofloat(self):
        return self.c / 512.

    def __mul__(self, other):
        if isinstance(other, S89):
            return S89((self.c * other.c) >> 9)
        else:
            return S89(self.c * other)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __add__(self, other):
        if isinstance(other, S89):
            return S89(self.c + other.c)
        else:
            return S89(self.c + 512 * other)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, S89):
            return S89(self.c - other.c)
        else:
            return S89(self.c - 512 * other)

    def __rsub__(self, other):
        return S89(512 * other - self.c)

    def __neg__(self):
        return S89(-self.c)

    def __repr__(self):
        return repr(self.c)

    def sqrt(self):
        return S89.fromfloat(np.sqrt(np.maximum(0, self.tofloat())))

    def reciprocal(self):
        return S89.fromfloat(1.0 / self.tofloat())
        
    def isqrt(self):
        return self.sqrt().reciprocal()

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
    def norm8(self):
        return self * abs(self).isqrt()
    def components(self):
        return (self.x, self.y, self.z)
    def tofloat(self):
        return vec3(self.x.tofloat(), self.y.tofloat(), self.z.tofloat())
    def __repr__(self):
        return "(%r, %r, %r)" % self.components()
rgb = vec3

(w, h) = (128, 128)         # Screen size
L = vec3(5, 5., -10)        # Point light position
FARAWAY = 0x1ffff           # an implausibly huge distance

def raytrace(D, scene):
    # (0,0,0) is the ray origin, D is the normalized ray direction
    # scene is a list of Sphere objects (see below)

    distances = [s.intersect(D) for s in scene]
    nearest = reduce(np.minimum, distances)
    color = rgb(0, 0, 0)
    for (s, d) in zip(scene, distances):
        cc = s.light(D, S89(d), scene) * (nearest != FARAWAY) * (d == nearest)
        color += cc
    return color

class Sphere:
    def __init__(self, center, r, diffuse):
        self.center = center * -1
        self.r = r
        self.c4 = 4 * (abs(center) - (r * r))
        self.diffuse = diffuse

    def intersect(self, D):
        # D = D.tofloat()
        b = D.dot(self.center) * 2
        disc = (b * b) - self.c4
        h = (-b - disc.sqrt()) * 0.5
        pred = disc.c > 0
        return np.where(pred, h.c, FARAWAY)

    def light(self, D, d, scene):
        M = (D * d)                             # intersection point
        toL = (L - M).norm8()                   # direction to light
        toO = (M * -1).norm8()                  # direction to ray origin
        N = (M + self.center) * (1. / self.r)   # normal
        lv = N.dot(toL)                         # Lambert shading (diffuse)
        color = self.diffuse * lv
        phong = N.dot((toL + toO).norm8())      # Blinn-Phong shading (specular)
        phong = phong * phong
        phong = phong * phong
        phong = phong * phong
        phong = phong * phong
        color += rgb(1, 1, 1) * phong
        return color

dm = np.array([ [0,8,2,10], [12,4,14,6], [3,11,1,9], [15,7,13,5] ])/16. + (1./32)
dither = np.tile(dm, (w / 4, h / 4)).flatten()

S = (-512, 504, 504, -512)
x = S89(np.tile(np.linspace(S[0], S[2], w), h))
y = S89(np.repeat(np.linspace(S[1], S[3], h), w))
Q = vec3(x, y, S89.k(3)).norm8().norm8()

for f in range(60):
    scene = [
        Sphere(vec3(0, 0, 2), 1.2, rgb(.66, .3, .3)),
        # Sphere(vec3(-1, -1, 1.6), .5, rgb(1, 0, 0)),
        # Sphere(vec3(1, 1, 1.6), .5, rgb(0, 1, 0)),
        ]
    scene = []
    r = 1.2
    for i,color in enumerate([ch("ff4500"), ch("008080"), ch("45ff00")]):
        th = 2 * math.pi * (f + 20 * i) / 60
        x = r * math.sin(th)
        z = r * math.cos(th)
        scene += [Sphere(vec3(x, .6 * z, 6 + z), r, color)]

    color = raytrace(Q, scene)

    def unquant(c):
        # return 255 * np.clip(c, 0, 1)
        return 255 * (c.tofloat() > dither)
    rgbim = [Image.fromarray((unquant(c).reshape((h, w))).astype(np.uint8), "L") for c in color.components()]
    Image.merge("RGB", rgbim).save("%04d.png" % f)
