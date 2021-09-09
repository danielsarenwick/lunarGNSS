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

vm = orekit.initVM()
setup_orekit_curdir()

class iterationProblem(Problem):
    def __init__(self):
        lowerBounds = np.array([5000.0, 0.0, 0.0, 0.0, 3, 3, 0])
        upperBounds = np.array([50000.0, 0.5, 90.0, 360.0, 10, 10, 1])

        super().__init__(
            n_var=7, # a, e, i, aop, s, p, f
            n_obj=4, # gdop, hdop, deltav, t
            n_constr=4,
            xl=lowerBounds,
            xu=upperBounds
        )

    def _evaluate(self, x, out, *args, **kwargs):
            results = poolHandler(x)

            gdop = [y[0] for y in results]  # gdop
            hdop = [y[1] for y in results]  # hdop
            deltav = [y[2] for y in results]  # delta v
            t = [y[3] for y in results]

            g1 = (x[:,4] * x[:,5]) - 60.0
            g2 = [(y[0]-10.0) for y in results]
            g3 = [(y[1]-10.0) for y in results]
            g4 = [(y[2]-1.0) for y in results]

            out["F"] = np.column_stack([gdop, hdop, deltav, t])
            out["G"] = np.column_stack([g1, g2, g3, g4])

def analyses(config):
    stepSize = 900.0
    points = 500

    results = analysis.constellationAnalysis(config, stepSize, points)

    return results

def poolHandler(configs):
    p = get_context("forkserver").Pool(24, maxtasksperchild=1)

    configList = pd.DataFrame(data=configs, columns=[
        "a",
        "e",
        "i",
        "aop",
        "s",
        "p",
        "f"
    ])

    #configList.to_csv('configList.csv', index_label=False, index=False)

    results = list(tqdm(p.imap(analyses, configs, chunksize=1), total=len(configs)))

    p.close()
    p.join()

    return results

if __name__ == '__main__':
    x = 1

    if x == 0:
        problem = iterationProblem()

        ref_dirs = get_reference_directions("energy", 4, 200)

        mask = ["real", "real", "real", "real", "int", "int", "real"]

        sampling = MixedVariableSampling(mask, {
            "real": get_sampling("real_random"),
            "int": get_sampling("int_random")
        })

        crossover = MixedVariableCrossover(mask, {
            "real": get_crossover("real_sbx", prob=0.75, eta=5.0),
            "int": get_crossover("int_sbx", prob=0.75, eta=5.0)
        })

        mutation = MixedVariableMutation(mask, {
            "real": get_mutation("real_pm", eta=10.0),
            "int": get_mutation("int_pm", eta=10.0)
        })

        algorithm = CTAEA(
            ref_dirs=ref_dirs,
            sampling=sampling,
            crossover=crossover,
            mutation=mutation,
            eliminate_duplicates=True
        )

        termination = MultiObjectiveSpaceToleranceTermination(
            tol=1e-3,
            n_last=30,
            nth_gen=5
        )

        run = copy.deepcopy(algorithm)
        run.setup(problem, termination=termination, seed=1)

        while run.has_next():
            run.next()

            save("generations/evolution_%d"%run.n_gen, run)
            print("\n\n", run.n_gen)
    else:
        run, = load("generations/evolution_1771.npy", allow_pickle=True).flatten()

        while run.has_next():
            run.next()

            save("generations/evolution_%d"%run.n_gen, run)
            print("\n\n", run.n_gen)
