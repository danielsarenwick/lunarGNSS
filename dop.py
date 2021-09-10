import orekit
from java.util import Arrays
from numpy import zeros


# defines a function to propagate the constellation and calculate
# the dilution of precision over each time step
def calcDop(moon, propagators, points, t):
    # initialises two empty numpy arrays to hold generated dop values
    GDoP = zeros((len(t), points))
    HDoP = zeros((len(t), points))
    # similarly generates four empty numpy arrays to hold the final
    # state of each satellite
    aFinal = zeros(len(propagators))
    eFinal = zeros(len(propagators))
    iFinal = zeros(len(propagators))
    endParams = zeros((len(propagators), 3))

    y = 0

    # iterates though each time step in the propagation
    for tt in t:
        # iterates through each point on the surface of the moon
        for x in range(points):
            try:
                # propagates the constellation too the current time step, tt
                # then calculates the dilution of precision at the current
                # point on the surface, x
                DoP = moon.stations[x].compute(tt, Arrays.asList(propagators))
                GDoP[y, x] = DoP.getGdop()
                HDoP[y, x] = DoP.getHdop()
            except Exception:
                pass
        y += 1

    # after the propagation has finished, the final state of each satellite is
    # retrieved and stored
    for x in range(len(propagators)):
        try:
            finalState = propagators[x].propagate(t[-1])
            endParams[x, 0] = finalState.getA()
            endParams[x, 1] = finalState.getE()
            endParams[x, 2] = finalState.getI()
        except Exception:
            endParams[x, :] = 0

    return GDoP, HDoP, endParams
