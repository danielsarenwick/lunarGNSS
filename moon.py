from numpy import arcsin
from math import pi
from scipy.constants import golden

import orekit
from org.orekit.bodies import OneAxisEllipsoid, CelestialBodyFactory, GeodeticPoint
from org.orekit.utils import Constants
from org.orekit.gnss import DOPComputer


# defines a class to handle neccessary definition for the Moon
class moon:
    def __init__(self):
        # creates a model of the Moon as a one axis ellipsoid
        # using Orekit to use for the gravitational model
        body = CelestialBodyFactory.getMoon()
        self.eqRadius = Constants.MOON_EQUATORIAL_RADIUS
        flat = 0.0012

        self.inertialFrame = body.getInertiallyOrientedFrame()
        self.bodyFrame = body.getBodyOrientedFrame()
        self.mu = body.getGM()
        self.oneAxisEllipsoid = OneAxisEllipsoid(self.eqRadius, flat,
                                                 self.bodyFrame)

    # function to create an array of latitudes and longitudes to
    # define the surface of the Moon with a given number of points
    # It uses a fibonacci sphere method to ensure that they are
    # more or less evenly spaced
    def defineGroundstations(self, points, minElevation, alt):
        self.stations = [0] * points
        self.point = [0] * points
        self.pos = [0] * points
        self.frame = [0] * points

        y = 0
        ga = (2 - golden) * (2 * pi)

        for x in range(points):
            lat = float(arcsin(-1 + (2 * x) / (points + 1)))
            long = float(x * ga)
            while long > pi:
                long -= 2 * pi
            # defines an Orekit DOPComputer at each point to
            # facilitate the calculate of dop later
            self.stations[y] = DOPComputer.create(
                self.oneAxisEllipsoid, GeodeticPoint(lat, long, alt))

            self.stations[y].withMinElevation(minElevation)

            self.pos[y] = self.oneAxisEllipsoid.transform(
                GeodeticPoint(lat, long, alt))

            y += 1
