from numpy import sqrt, square, cos


# calculates the delta v required to return the satellite
# back to its original orbit - station keeping
def calcDv(startParams, endParams, moon):
    # final orbit of the satellite after propagation
    a1 = endParams[0]
    e1 = endParams[1]
    i1 = endParams[2]
    # initial orbit of the satellite before propagation
    a2 = startParams[0]
    e2 = startParams[1]
    i2 = startParams[2]
    # computes the delta v required for a two-manoeuvre
    # Hohmann transfer and out of plane burn
    rp1 = a1 * (1 - e1)
    vp1 = sqrt(moon.mu * ((2 / rp1) - (1 / a1)))

    ra2 = a2 * (1 + e2)
    at = 0.5 * (rp1 + ra2)

    tv1 = sqrt(moon.mu * ((2 / rp1) - (1 / at)))
    dv1 = abs(tv1 - vp1)

    tv2 = sqrt(moon.mu * ((2 / ra2) - (1 / at)))
    va2 = sqrt(moon.mu * ((2 / ra2) - (1 / a2)))

    di = abs(i2 - i1)

    dv2 = abs(sqrt(square(tv2) + square(va2) - (2 * tv2 * va2 * cos(di))))

    dv = abs(dv1 + dv2)

    return (dv / 1000)
