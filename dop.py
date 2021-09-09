import orekit
from java.util import Arrays
from numpy import zeros

def calcDop(moon, propagators, points, t):

    #latitude = zeros((len(t), points))
    #longitude = zeros((len(t), points))
    GDoP = zeros((len(t), points))
    HDoP = zeros((len(t), points))

    aFinal = zeros(len(propagators))
    eFinal = zeros(len(propagators))
    iFinal = zeros(len(propagators))

    endParams = zeros((len(propagators), 3))

    y = 0

    for tt in t:
        for x in range(points):
            try:
                DoP = moon.stations[x].compute(tt, Arrays.asList(propagators))
                #latitude[y, x] = DoP.getLocation().getLatitude()
                #longitude[y, x] = DoP.getLocation().getLongitude()
                GDoP[y, x] = DoP.getGdop()
                HDoP[y, x] = DoP.getHdop()
            except Exception:
                pass
    
        y += 1
    for x in range(len(propagators)):
        try:
            finalState = propagators[x].propagate(t[-1])
            endParams[x, 0] = finalState.getA()
            endParams[x, 1] = finalState.getE()
            endParams[x, 2] = finalState.getI()
        except Exception:
            endParams[x, :] = 0
        
    return GDoP, HDoP, endParams