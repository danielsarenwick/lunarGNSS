import pandas as pd
from numpy import array, save, load, arange
from evolution import iterationProblem
from tqdm import tqdm
from pymoo.factory import get_decomposition

weights = array([0.3, 0.3, 0.1, 0.3])
decomp = get_decomposition("pbi", theta=0.5, eps=0)

gens = arange(5, 1864)
results = pd.DataFrame(columns=['a', 'e', 'i', 'aop', 's', 'p', 'f', 'GDoP', 'HDoP', 'dV', 'T', 'Decomp'])

for x in gens:
    run, = load("generations/evolution_%d.npy" %
                (x+1), allow_pickle=True).flatten()
    ress = run.result()

    resNorm = ress.F / ress.F.max(axis=0)

    X_new = pd.DataFrame(ress.X, columns=['a', 'e', 'i', 'aop', 's', 'p', 'f'])

    F_new = pd.DataFrame(ress.F, columns=['GDoP', 'HDoP', 'dV', 'T'])
    F_new['Decomp'] = decomp.do(resNorm, weights)

    results_new = pd.concat([X_new, F_new], axis=1)

    results = results.append(results_new, ignore_index=True)

results = results[results['GDoP'].between(0, 10)]
results = results[results['HDoP'].between(0, 10)]
results = results[results['dV'].between(0, 0.1)]
results = results[results['T'].between(0, 60)]

results = results.drop_duplicates(subset=results.columns.difference(['Decomp']))

results.to_csv('results.csv', index_label=False, index=False)
