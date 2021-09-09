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


def analyses(config):
    stepSize = 900.0
    points = 500

    res = analysis.constellationAnalysis(config, stepSize, points)
    return res

def poolHandler(config):
    p = get_context("forkserver").Pool(24, maxtasksperchild=1)
    res = list(tqdm(p.imap(analyses, config, chunksize=1), total=len(config)))

    p.close()
    p.join()

    return res

if __name__ == '__main__':
    file = pd.read_csv('constellations.csv')
    print(file)
    print()

    configs = file.to_numpy()

    results = analyses(configs[0])

    res = pd.DataFrame(data=results, columns=[
        "3sig GDoP",
        "3sig HDoP",
        "dV (km/s)",
        "T"
    ])

    print()
    print(res)