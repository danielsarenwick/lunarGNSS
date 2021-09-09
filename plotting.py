import plotly.graph_objects as go

from numpy import zeros

import orekit

from org.orekit.time import AbsoluteDate
from org.orekit.utils import PVCoordinates
from org.orekit.propagation import BoundedPropagator

def plotEphemerides(propagators, t, moon, points):

    fig = go.Figure()

    pos = zeros((len(propagators), len(t), 3))

    for x in range(len(propagators)):

        pos[x, :, 0] = [propagators[x].propagate(tt).getPVCoordinates(moon.bodyFrame).getPosition().getX() for tt in t]
        pos[x, :, 1] = [propagators[x].propagate(tt).getPVCoordinates(moon.bodyFrame).getPosition().getY() for tt in t]
        pos[x, :, 2] = [propagators[x].propagate(tt).getPVCoordinates(moon.bodyFrame).getPosition().getZ() for tt in t]

        fig.add_trace(go.Scatter3d(
            x=pos[x, :, 0],
            y=pos[x, :, 1],
            z=pos[x, :, 2]
            #mode='markers'
        ))

    #posGround = zeros((points, 3))
        
    #for x in range(points):   
    #    posGround[x, 0] = moon.pos[x].getX()
    #    posGround[x, 1] = moon.pos[x].getY()
    #    posGround[x, 2] = moon.pos[x].getZ()

    #fig.add_trace(go.Scatter3d(
    #    x = posGround[:, 0],
    #    y = posGround[:, 1],
    #    z = posGround[:, 2]
        #mode='marker'
    #))
    
    fig.write_html('orbitPlot.html')
