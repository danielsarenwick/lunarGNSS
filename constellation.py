from math import radians, pi

import orekit
from org.orekit.orbits import KeplerianOrbit, PositionAngle


# defines a class to define the initial orbital position of each
# satellite within a constellation
class constellation:
    def __init__(self, config, moon, initialDate):
        # Imports constellation configurations in the format:
        # a, i, aop, t, p, f

        # Loads Walker constellation parameters

        self.s = int(config[4])
        self.p = int(config[5])
        self.f = int((self.p - 1) * config[6])
        self.t = int(self.s * self.p)

        # Creates the initial state of each satellite in the constellation
        # in keplerian parameters
        # a, e, i, aop, raan,ta

        self.initialOrbit = [0] * self.t

        for x in range(self.p):
            raan = 2 * pi * (x / self.p)
            for y in range(self.s):
                ta = 2 * pi * (y / self.s)
                i = y + (x * self.s)
                self.initialOrbit[i] = KeplerianOrbit(
                    float(config[0] * 1000),
                    float(config[1]),
                    float(radians(config[2])),
                    float(radians(config[3])),
                    float(raan),
                    float(ta + 2 * pi * ((self.f * x) / self.t)),
                    PositionAngle.TRUE, moon.inertialFrame, initialDate,
                    moon.mu)
