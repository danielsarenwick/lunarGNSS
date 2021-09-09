from pymoo.algorithms.ctaea import CTAEA
from pymoo.model.problem import Problem
from pymoo.factory import get_termination, get_reference_directions, get_sampling, get_mutation, get_crossover
from pymoo.operators.mixed_variable_operator import MixedVariableCrossover, MixedVariableMutation, MixedVariableSampling
from pymoo.util.termination.f_tol import MultiObjectiveSpaceToleranceTermination
from numpy import array, save, load

import random
import copy
import numpy as np
import pandas as pd

import analysis
import time
from tqdm import tqdm

from multiprocessing import Pool, get_context
from itertools import product

import orekit
from orekit.pyhelpers import setup_orekit_curdir

# initialises Orekit
vm = orekit.initVM()
setup_orekit_curdir()


# define a class to handle the optimisation within Pymoo
class iterationProblem(Problem):
    def __init__(self):
        # defines the bounds for each of the variables under consideration
        # a, e, i, aop, s, p, f
        lowerBounds = np.array([5000.0, 0.0, 0.0, 0.0, 3, 3, 0])
        upperBounds = np.array([50000.0, 0.5, 90.0, 360.0, 10, 10, 1])

        super().__init__(
            n_var=7,  # a, e, i, aop, s, p, f
            n_obj=4,  # gdop, hdop, deltav, t
            n_constr=4,
            xl=lowerBounds,
            xu=upperBounds)

    def _evaluate(self, x, out, *args, **kwargs):
        # initialises the simulation for the current set of configurations
        results = poolHandler(x)
        # split data from results into seperate variables
        gdop = [y[0] for y in results]  # gdop
        hdop = [y[1] for y in results]  # hdop
        deltav = [y[2] for y in results]  # delta v
        t = [y[3] for y in results]  # number of satellite in constellation
        # define constraints for the results of each variable
        # if the design falls outside the constraint, the then design
        # is discarded
        g1 = (x[:, 4] * x[:, 5]) - 60.0  # t <= 60.0
        g2 = [(y[0] - 10.0) for y in results]  # gdop <= 10.0
        g3 = [(y[1] - 10.0) for y in results]  # hdop <= 10.0
        g4 = [(y[2] - 1.0) for y in results]  # dv <= 1.0
        # returns the results of the current iteration back to CTAEA
        out["F"] = np.column_stack([gdop, hdop, deltav, t])
        out["G"] = np.column_stack([g1, g2, g3, g4])


# setup up and runs the simulation for the given constellation configuration
def analyses(config):
    # defines the quality parameters for the simulation
    # sets the time in seconds between each step in the orbital propagator
    stepSize = 900.0
    # sets the number of points from which to construct the surface of the Moon
    points = 500
    # performs the simulaiton for the given constellation design
    results = analysis.constellationAnalysis(config, stepSize, points)
    # returns the performance metrics to the optimiser
    return results


# function to handle the multiprocessing of the simulation by using a pool
def poolHandler(configs):
    # set to the number of cores (threads) in your CPU
    # BE CAREFUL WITH RAM USAGE!!!
    # each process uses approximately 2.5 GB of RAM at maximum load
    cpus = 24
    # creates the multiprocessing pool with the given number of CPUs
    # 'forkserver' and maxtaskperchild = 1 are used to minimise RAM usage
    p = get_context("forkserver").Pool(cpus, maxtasksperchild=1)

    # configList = pd.DataFrame(
    #   data=configs, columns=["a", "e", "i", "aop", "s", "p", "f"])

    # configList.to_csv('configList.csv', index_label=False, index=False)
    # maps the current list of configuations onto the multiprocessing pool
    # tqdm is used to display the current progress through the current
    # iteration
    results = list(
        tqdm(
            p.imap(
                analyses, configs, chunksize=1), total=len(configs)))

    p.close()
    p.join()

    return results


if __name__ == '__main__':
    # determines whether to load a save or not.
    # if you want to start a fresh analysis, set x to 0
    # if you want to a previous analysis set x to 1
    x = 1

    if x == 0:
        # creates a fresh optimisation with the given variables,
        # objectives, and constraints
        problem = iterationProblem()
        # defines the number of constellations to be generated for each
        # iteration
        iterationSize = 200
        # defines the directions within the objective space through which
        # the CTAEA algorithm will search
        ref_dirs = get_reference_directions("energy", 4, iterationSize)
        # defines the type used for each of the seven input variables
        mask = ["real", "real", "real", "real", "int", "int", "real"]
        # defines the random sampling used for the selection of configurations
        sampling = MixedVariableSampling(mask, {
            "real": get_sampling("real_random"),
            "int": get_sampling("int_random")
        })
        # defines the crossover model used
        crossover = MixedVariableCrossover(
            mask, {
                "real": get_crossover(
                    "real_sbx", prob=0.75, eta=5.0),
                "int": get_crossover(
                    "int_sbx", prob=0.75, eta=5.0)
            })
        # defines the mutation model used
        mutation = MixedVariableMutation(
            mask, {
                "real": get_mutation(
                    "real_pm", eta=10.0),
                "int": get_mutation(
                    "int_pm", eta=10.0)
            })
        # creates a object containing the CTAEA algorithm with the
        # given directions, sampling, crossover, and mutation defined
        # above
        algorithm = CTAEA(
            ref_dirs=ref_dirs,
            sampling=sampling,
            crossover=crossover,
            mutation=mutation,
            eliminate_duplicates=True)
        # sets the tolerance at which the algorithm will terminate
        # the current value fo 1e-3 sets the to continue indefinately
        termination = MultiObjectiveSpaceToleranceTermination(
            tol=1e-3, n_last=30, nth_gen=5)

        run = copy.deepcopy(algorithm)
        run.setup(problem, termination=termination, seed=1)
        # runs the optimisation process until the termination is met
        while run.has_next():
            run.next()
            # saves the data for each iteration into a new folder
            # this allows one to restart from any generation, or
            # load each generation for analysis at the end
            save("generations/evolution_%d" % run.n_gen, run)
            print("\n\n", run.n_gen)
            # when you want to finish the current simulation simply
            # close the cmd prompt running the script
    else:
        # if you want to load from a previous run
        # enter the number of the generation you wish to start from
        run, = load(
            "generations/evolution_1864.npy", allow_pickle=True).flatten()

        while run.has_next():
            run.next()

            save("generations/evolution_%d" % run.n_gen, run)
            print("\n\n", run.n_gen)
