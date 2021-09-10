import orekit
from orekit import JArray_double
from org.orekit.propagation import SpacecraftState
from org.orekit.propagation.numerical import NumericalPropagator
from org.hipparchus.ode.nonstiff import (
    ClassicalRungeKuttaIntegrator,
    DormandPrince853Integrator, )
from org.orekit.forces.gravity import (
    ThirdBodyAttraction,
    HolmesFeatherstoneAttractionModel,
    Relativity, )
from org.orekit.forces.gravity.potential import GravityFieldFactory
from org.orekit.forces.radiation import (
    SolarRadiationPressure,
    IsotropicRadiationSingleCoefficient, )
from org.orekit.bodies import CelestialBodyFactory
from org.orekit.orbits import OrbitType


# defines a class to create an Orekit propagator object
# for a satellite given an initial orbit
class satellite:
    def __init__(self, initialOrbit, moon, mass, stepSize):
        integrator = ClassicalRungeKuttaIntegrator(stepSize)

        self.propagator = NumericalPropagator(integrator)
        self.propagator.setOrbitType(OrbitType.CARTESIAN)

        self.initialState = SpacecraftState(initialOrbit, mass)
        self.propagator.setInitialState(self.initialState)

        gravityProvider = GravityFieldFactory.getNormalizedProvider(10, 10)

        self.propagator.addForceModel(
            HolmesFeatherstoneAttractionModel(moon.bodyFrame, gravityProvider))

        self.propagator.addForceModel(
            ThirdBodyAttraction(CelestialBodyFactory.getEarth()))

        self.propagator.addForceModel(
            ThirdBodyAttraction(CelestialBodyFactory.getSun()))

        self.propagator.addForceModel(Relativity(moon.mu))

        self.propagator.addForceModel(
            SolarRadiationPressure(
                CelestialBodyFactory.getSun(),
                moon.eqRadius,
                IsotropicRadiationSingleCoefficient(3.92, 1.8), ))


# Assumes a satellite similar to that of Starlink at 2.8 x 1.4 m
