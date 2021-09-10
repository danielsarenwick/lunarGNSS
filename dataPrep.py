# after the end of the analysis, run this script to clean the raw data
# and save the useful data to "results/results.csv"

import pandas as pd
from numpy import array, save, load, arange
from main import iterationProblem
from tqdm import tqdm
from pymoo.factory import get_decomposition

# Sets the weights for the relative impact of each objective
# This is largely up to intuition, and I have assumed that
# the delta v cost is the least important in deciding the
# constellation performance
weights = array([0.3, 0.3, 0.1, 0.3])
decomp = get_decomposition("pbi", theta=0.5, eps=0)
# ignore the first few iterations
gens = arange(5, 1864)
# create a master pandas dataframe to store the final data
results = pd.DataFrame(columns=[
    'a', 'e', 'i', 'aop', 's', 'p', 'f', 'GDoP', 'HDoP', 'dV', 'T', 'Decomp'
])
# iterates through each generation of results to retrieve each constellation
# design considered during the analysis
for x in gens:
    # loads the appropriate iteration
    run, = load(
        "generations/evolution_%d.npy" % (x + 1), allow_pickle=True).flatten()
    ress = run.result()
    # normalises the results of each objective between 0 and 1
    # this is so that the decomposition can consider each objective
    # without being altered by the differences in magnitude
    resNorm = ress.F / ress.F.max(axis=0)
    # separates the variables and objectives into two pandas dataframes
    X_new = pd.DataFrame(ress.X, columns=['a', 'e', 'i', 'aop', 's', 'p', 'f'])
    F_new = pd.DataFrame(ress.F, columns=['GDoP', 'HDoP', 'dV', 'T'])
    # calculates a decomposition values for each constellation design
    # to determine the relative performance of each according to the
    # given weights above
    F_new['Decomp'] = decomp.do(resNorm, weights)
    # concatentates the two pandas dataframes into a single dataframe
    results_new = pd.concat([X_new, F_new], axis=1)
    # appends the results from this iteration to the master dataframe
    results = results.append(results_new, ignore_index=True)
# removes any constellation design within the desired ranges
results = results[results['GDoP'].between(0, 10)]
results = results[results['HDoP'].between(0, 10)]
results = results[results['dV'].between(0, 0.1)]
results = results[results['T'].between(0, 60)]
# removes any duplicates from the data
results = results.drop_duplicates(subset=results.columns.difference(
    ['Decomp']))
# saves the master pandas dataframe to a csv file
results.to_csv('results/results.csv', index_label=False, index=False)
