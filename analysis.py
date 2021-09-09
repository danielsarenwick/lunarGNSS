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


def constellationAnalysis(config, stepSize, points):

    vm = orekit.getVMEnv()

    vm.attachCurrentThread()

    start = process_time()

    duration = 86400.0 * 14

    initialDate = AbsoluteDate(2021, 1, 1, 23, 30, 0.000,
                               TimeScalesFactory.getUTC())

    Moon = moon()
    constellations = constellation(config, Moon, initialDate)

    mass = 250.0

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

    minElevation = radians(10)
    alt = 0.0

    Moon.defineGroundstations(points, minElevation, alt)

    t = [
        initialDate.shiftedBy(float(dt))
        for dt in arange(0, duration, stepSize)
    ]

    GDoP, HDoP, endParams = calcDop(Moon, propagators, points, t)

    GDoP = [item for sublist in GDoP for item in sublist]
    HDoP = [item for sublist in HDoP for item in sublist]

    for x in range(len(GDoP)):
        if isnan(GDoP[x]):
            GDoP[x] = 1000.0
            HDoP[x] = 1000.0

    meanGDoP = float(nanmean(GDoP))
    meanHDoP = float(nanmean(HDoP))

    stdGDoP = float(nanstd(GDoP))
    stdHDoP = float(nanstd(HDoP))

    threeSigGDoP = meanGDoP + (3 * stdGDoP)
    threeSigHDoP = meanHDoP + (3 * stdHDoP)

    flatEndParams = [item for sublist in endParams for item in sublist]

    if any(x == 0 for x in flatEndParams):

        results = [float(1e6), float(1e6), float(1e6), float(1e6)]

    else:
        dv = [0] * len(propagators)

        for x in range(len(propagators)):
            dv[x] = calcDv(startParams[x], endParams[x], Moon)

        meanDv = float(nanmean(dv))

        end = process_time()
        time = end - start

        results = [threeSigGDoP, threeSigHDoP, meanDv, constellations.t]

    return results
