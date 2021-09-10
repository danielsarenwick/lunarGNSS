# Standard python libraries
from numpy import zeros, arange, nanmean, nanstd, array, savetxt, isnan
from math import radians
from time import process_time

from propagator import satellite
from constellation import constellation
from moon import moon
from dop import calcDop
from dv import calcDv

import orekit

from org.orekit.time import AbsoluteDate, TimeScalesFactory


# defines a function which handles the simulation of each constellation design
def constellationAnalysis(config, stepSize, points):
    vm = orekit.getVMEnv()
    vm.attachCurrentThread()
    # defines the duration of the current simulation
    # currently runs for 14 days
    duration = 86400.0 * 14
    # sets the initial data for propagation
    initialDate = AbsoluteDate(2021, 1, 1, 23, 30, 0.000,
                               TimeScalesFactory.getUTC())
    # creates the moon object. See moon.py
    Moon = moon()
    constellations = constellation(config, Moon, initialDate)
    # defines the mass of an individual satellite
    mass = 250.0
    # creates propagation objects for each satellite and sets each to the
    # appropriate initial orbit
    propagators = [0] * constellations.t
    startParams = zeros((constellations.t, 3))
    for x in range(constellations.t):
        satellites = satellite(constellations.initialOrbit[x], Moon, mass,
                               stepSize)
        propagators[x] = satellites.propagator
        initialState = satellites.initialState
        startParams[x, 0] = initialState.getA()
        startParams[x, 1] = initialState.getE()
        startParams[x, 2] = initialState.getI()
    # defines the minimum elevation and altitude at which dilution of precision
    # will be calculated from the Lunar surface
    minElevation = radians(10)
    alt = 0.0
    # defines DoP computer groundstations at each point on the Lunar surface
    Moon.defineGroundstations(points, minElevation, alt)
    # creates an array of time steps for which to iterate through during
    # propagation
    t = [
        initialDate.shiftedBy(float(dt))
        for dt in arange(0, duration, stepSize)
    ]
    # performs the main orbital propagation and DoP calculation.
    # see DoP.py
    GDoP, HDoP, endParams = calcDop(Moon, propagators, points, t)
    # flattens the GDoP and HDoP arrays
    GDoP = [item for sublist in GDoP for item in sublist]
    HDoP = [item for sublist in HDoP for item in sublist]
    # Orekit returns values of NaN when a GNSS signal cannot be found
    # in order to include this in the 3sigma calculation, NaNs are replaced
    # with values of 1000.0. This allows the optimisation algorithm to
    # identify these designs and remove them
    for x in range(len(GDoP)):
        if isnan(GDoP[x]):
            GDoP[x] = float(1e6)
            HDoP[x] = float(1e6)
    # calculates the mean of GDop and HDoP
    meanGDoP = float(nanmean(GDoP))
    meanHDoP = float(nanmean(HDoP))
    # calculates the standard deviation of GDoP and HDoP
    stdGDoP = float(nanstd(GDoP))
    stdHDoP = float(nanstd(HDoP))
    # calculates the 3 sigma values of each
    threeSigGDoP = meanGDoP + (3 * stdGDoP)
    threeSigHDoP = meanHDoP + (3 * stdHDoP)
    # flattens the array of final orbital parameters
    flatEndParams = [item for sublist in endParams for item in sublist]
    if any(x == 0 for x in flatEndParams):

        results = [float(1e6), float(1e6), float(1e6), float(1e6)]

    else:
        # calculates the required deltaV to return  each satellite to its
        # original orbit
        dv = [0] * len(propagators)

        for x in range(len(propagators)):
            dv[x] = calcDv(startParams[x], endParams[x], Moon)

        meanDv = float(nanmean(dv))

        results = [threeSigGDoP, threeSigHDoP, meanDv, constellations.t]

    return results
