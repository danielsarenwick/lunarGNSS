from numpy import arcsin
from math import pi
from scipy.constants import golden

import orekit
from org.orekit.bodies import OneAxisEllipsoid, CelestialBodyFactory, GeodeticPoint
from org.orekit.utils import Constants
from org.orekit.gnss import DOPComputer

class moon:

    def __init__(self):

        body = CelestialBodyFactory.getMoon()
        self.eqRadius = Constants.MOON_EQUATORIAL_RADIUS
        flat = 0.0012

        self.inertialFrame = body.getInertiallyOrientedFrame()
        self.bodyFrame = body.getBodyOrientedFrame()
        self.mu = body.getGM()
        self.oneAxisEllipsoid = OneAxisEllipsoid(self.eqRadius, flat, self.bodyFrame) 

    def defineGroundstations(self, points, minElevation, alt):
        
        # Creates an array of points about a sphere using the fibonnaci sphere generator
   
        self.stations = [0]*points
        self.point = [0]*points
        self.pos = [0]*points
        self.frame = [0]*points

        y = 0
        ga = (2 - golden) * (2 * pi)
       
        for x in range (points):
            lat = float(arcsin(-1 + (2 * x) / (points + 1)))
            long = float(x * ga)
            while long > pi:
                long -= 2*pi
            self.stations[y] = DOPComputer.create(self.oneAxisEllipsoid, GeodeticPoint(lat, long, alt))
            self.stations[y].withMinElevation(minElevation)
            self.pos[y] = self.oneAxisEllipsoid.transform(GeodeticPoint(lat, long, alt))
            y += 1