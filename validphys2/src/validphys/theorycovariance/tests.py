#-*- coding: utf-8 -*-
"""
tests.py
Tools for testing theory covariance matrices and their properties.
"""
from __future__ import generator_stop

import logging

from collections import namedtuple
import numpy as np
import scipy.linalg as la
import matplotlib.pyplot as plt
import pandas as pd

from reportengine.checks import make_argcheck
from reportengine.figure import figure
from reportengine.table import table
from reportengine import collect

from validphys.checks import check_two_dataspecs

from validphys.theorycovariance.construction import _check_correct_theory_combination
from validphys.theorycovariance.construction import combine_by_type, process_starting_points
from validphys.theorycovariance.construction import theory_corrmat
from validphys.theorycovariance.construction import covmap, covs_pt_prescrip, theory_covmat_custom
from validphys.theorycovariance.construction import _process_lookup
from validphys.theorycovariance.construction import _check_correct_theory_combination_theoryconfig

from validphys.theorycovariance.output import matrix_plot_labels, _get_key
from validphys.theorycovariance.output import plot_corrmat_heatmap

log = logging.getLogger(__name__)

matched_dataspecs_results = collect('results', ['dataspecs'])

LabeledShifts = namedtuple('LabeledShifts',
    ('experiment_name', 'dataset_name', 'shifts'))

@check_two_dataspecs
def dataspecs_dataset_prediction_shift(matched_dataspecs_results, experiment_name,
                                       dataset_name):
    """Compute the difference in theory predictions between two dataspecs.
    This can be used in combination with `matched_datasets_from_dataspecs`
    It returns a ``LabeledShifts`` containing ``dataset_name``,
    ``experiment_name`` and ``shifts``.
    """
    r1, r2 = matched_dataspecs_results
    res =  r1[1].central_value - r2[1].central_value
    return LabeledShifts(dataset_name=dataset_name,
                         experiment_name=experiment_name, shifts=res)

matched_dataspecs_dataset_prediction_shift = collect(
    'dataspecs_dataset_prediction_shift', ['dataspecs'])

def shift_vector(matched_dataspecs_dataset_prediction_shift,
                 matched_dataspecs_dataset_theory):
    all_shifts = np.concatenate(
        [val.shifts for val in matched_dataspecs_dataset_prediction_shift])
    all_theory = np.concatenate(
        [val.shifts for val in matched_dataspecs_dataset_theory])
    norm_shifts = all_shifts/all_theory
    dsnames = np.concatenate([
        np.full(len(val.shifts), val.dataset_name, dtype=object)
        for val in matched_dataspecs_dataset_prediction_shift
    ])
    point_indexes = np.concatenate([
        np.arange(len(val.shifts))
        for val in matched_dataspecs_dataset_prediction_shift
    ])
    index = pd.MultiIndex.from_arrays(
        [dsnames, point_indexes],
        names=["Dataset name", "Point"])
    return pd.DataFrame(norm_shifts, index=index)

def dataspecs_dataset_theory(matched_dataspecs_results, experiment_name, dataset_name):
    central = matched_dataspecs_results[0]
    res = central[1].central_value
    return LabeledShifts(dataset_name=dataset_name,
                         experiment_name=experiment_name, shifts=res)

matched_dataspecs_dataset_theory = collect('dataspecs_dataset_theory', ['dataspecs'])

def theory_vector(matched_dataspecs_dataset_theory):
    all_theory = np.concatenate(
        [val.shifts for val in matched_dataspecs_dataset_theory])
    dsnames = np.concatenate([
        np.full(len(val.shifts), val.dataset_name, dtype=object)
        for val in matched_dataspecs_dataset_theory
    ])
    point_indexes = np.concatenate([
        np.arange(len(val.shifts))
        for val in matched_dataspecs_dataset_theory
    ])
    index = pd.MultiIndex.from_arrays(
        [dsnames, point_indexes],
        names=["Dataset name", "Point"])
    return pd.DataFrame(all_theory, index=index)

def dataspecs_dataset_alltheory(matched_dataspecs_results, experiment_name, dataset_name):
    others = matched_dataspecs_results[1:]
    res = [other[1].central_value for other in others]
    return LabeledShifts(dataset_name=dataset_name,
                         experiment_name=experiment_name, shifts=res)

matched_dataspecs_dataset_alltheory = collect('dataspecs_dataset_alltheory', ['dataspecs'])

def alltheory_vector(matched_dataspecs_dataset_alltheory, matched_dataspecs_dataset_theory):
    all_theory = np.concatenate(
        [val.shifts for val in matched_dataspecs_dataset_alltheory], axis=1)
    dsnames = np.concatenate([
        np.full(len(val.shifts),
        val.dataset_name, dtype=object)
        for val in matched_dataspecs_dataset_theory
    ])
    point_indexes = np.concatenate([
        np.arange(len(val.shifts))
        for val in matched_dataspecs_dataset_theory
    ])
    index = pd.MultiIndex.from_arrays(
        [dsnames, point_indexes],
        names=["Dataset name", "Point"])
    theory_vectors = []
    for theoryvector in all_theory:
        theory_vectors.append(pd.DataFrame(theoryvector, index=index))
    return theory_vectors

all_matched_results = collect('matched_dataspecs_results',
                              ['dataspecs'])

def combine_by_type_dataspecs(all_matched_results, matched_dataspecs_dataset_name):
    return combine_by_type(all_matched_results, matched_dataspecs_dataset_name)

dataspecs_theoryids = collect('theoryid', ['theoryconfig', 'original', 'dataspecs'])

def process_starting_points_dataspecs(combine_by_type_dataspecs):
    return process_starting_points(combine_by_type_dataspecs)

@make_argcheck
def _check_correct_theory_combination_dataspecs(dataspecs_theoryids,
                                                fivetheories:(str, type(None)) = None):
    return _check_correct_theory_combination.__wrapped__(
        dataspecs_theoryids, fivetheories)

@_check_correct_theory_combination_dataspecs
def covs_pt_prescrip_dataspecs(combine_by_type_dataspecs,
                               process_starting_points_dataspecs,
                               dataspecs_theoryids,
                               fivetheories: (str, type(None)) = None):
    return covs_pt_prescrip(combine_by_type_dataspecs, process_starting_points_dataspecs,
                            dataspecs_theoryids, fivetheories)

def covmap_dataspecs(combine_by_type_dataspecs, matched_dataspecs_dataset_name):
    return covmap(combine_by_type_dataspecs, matched_dataspecs_dataset_name)

matched_dataspecs_experiment_name = collect(
    'experiment_name', ['dataspecs'])
matched_dataspecs_dataset_name = collect(
    'dataset_name', ['dataspecs'])
matched_cuts_datasets = collect('dataset', ['dataspecs'])
all_matched_datasets = collect('matched_cuts_datasets',
                               ['dataspecs'])


def all_matched_data_lengths(all_matched_datasets):
    lens = []
    for rlist in all_matched_datasets:
        lens.append(rlist[0].load().GetNData())
    return lens

def matched_experiments_index(matched_dataspecs_dataset_name,
                              all_matched_data_lengths):
    dsnames = matched_dataspecs_dataset_name
    lens = all_matched_data_lengths
    dsnames = np.concatenate([
        np.full(l, dsname, dtype=object)
        for (l, dsname) in zip(lens, dsnames)
    ])
    point_indexes = np.concatenate([
        np.arange(l)
        for l in lens
    ])
    index = pd.MultiIndex.from_arrays(
        [dsnames, point_indexes],
        names=["Dataset name", "Point"])
    return index

@table
def theory_covmat_custom_dataspecs(covs_pt_prescrip_dataspecs, covmap_dataspecs,
                                   matched_experiments_index):
    return theory_covmat_custom(covs_pt_prescrip_dataspecs, covmap_dataspecs,
                                matched_experiments_index)

thx_corrmat = collect('theory_corrmat_custom_dataspecs',
                      ['combined_shift_and_theory_dataspecs', 'theoryconfig'])

shx_corrmat = collect('matched_datasets_shift_matrix_correlations',
                      ['combined_shift_and_theory_dataspecs', 'shiftconfig'])

thx_covmat = collect('theory_covmat_custom_dataspecs',
                     ['combined_shift_and_theory_dataspecs', 'theoryconfig'])

combined_dataspecs_results = collect('all_matched_results',
                                     ['combined_shift_and_theory_dataspecs', 'theoryconfig'])

shx_vector = collect('shift_vector', ['combined_shift_and_theory_dataspecs', 'shiftconfig'])

thx_vector = collect('theory_vector', ['combined_shift_and_theory_dataspecs', 'theoryconfig'])

allthx_vector = collect('alltheory_vector', ['combined_shift_and_theory_dataspecs', 'theoryconfig'])

def theory_matrix_threshold(theory_threshold:(int, float) = 0):
    """Returns the threshold below which theory correlation elements are set to
    zero when comparing to shift correlation matrix"""
    return theory_threshold

@table
def theory_corrmat_custom_dataspecs(theory_covmat_custom_dataspecs):
    """Calculates the theory correlation matrix for scale variations
    with variations by process type"""
    mat = theory_corrmat(theory_covmat_custom_dataspecs)
    return mat

@figure
def plot_thcorrmat_heatmap_custom_dataspecs(theory_corrmat_custom_dataspecs, theoryids):
    """Matrix plot of the theory correlation matrix, correlations by process type"""
    l = len(theoryids)
    fig = plot_corrmat_heatmap(theory_corrmat_custom_dataspecs,
                               f"Theory correlation matrix for {l} points")
    return fig

@_check_correct_theory_combination_theoryconfig
def evals_nonzero_basis(allthx_vector, thx_covmat, thx_vector,
                        collected_theoryids,
                        fivetheories:(str, type(None)) = None,
                        seventheories:(str, type(None)) = None):
    """Projects the theory covariance matrix from the data space into
    the basis of non-zero eigenvalues, dependent on point-prescription.
    Then returns the eigenvalues (w) and eigenvectors (v)
    in the data space."""

    def shuffle_list(l, shift):
        i=0
        newlist = l.copy()
        while i <= (shift-1):
            newlist.append(newlist.pop(0))
            i = i + 1
        return newlist

    covmat = (thx_covmat[0]/(np.outer(thx_vector[0], thx_vector[0])))
    # constructing vectors of shifts due to scale variation
    diffs = [((thx_vector[0] - scalevarvector)/thx_vector[0])
             for scalevarvector in allthx_vector[0]]
    # number of points in point prescription
    num_pts = len(diffs) + 1
    # constructing dictionary of datasets in each process type
    indexlist = list(diffs[0].index.values)
    procdict = {}
    for index in indexlist:
        name = index[0]
        proc = _process_lookup(name)
        if proc not in list(procdict.keys()):
            procdict[proc] = [name]
        elif name not in procdict[proc]:
            procdict[proc].append(name)
    # splitting up the scale-varied shift vectors into different spaces per process
    splitdiffs = []
    for process, dslist in procdict.items():
        alldatasets = [y for x in list(procdict.values()) for y in x]
        otherdatasets = [x for x in alldatasets if x not in procdict[process]]
        for diff in diffs:
            splitdiff = diff.copy()
            for ds in otherdatasets:
                splitdiff.loc[ds] = 0
            splitdiffs.append(splitdiff)
    # --------------------------------------------------
    # CONSTRUCTING THE LINEARLY INDEPENDENT VECTORS
    # treating each prescription on a case-by-case basis
	# Notation:
	# e.g. pp => (mu_0; mu_i) = (+;+)
	#      mz => (mu_0; mu_i) = (-;0)
	#      zp => (mu_0; mu_i) = (0;+) ...
	# for a process i,
	# and total vectors are notated like
	# (mu_0; mu_1, mu_2, ..., mu_p)
    if num_pts == 3:
        # N.B. mu_0 correlated with mu_i
        xs = []
        pps = splitdiffs[::(num_pts-1)]
        mms = shuffle_list(splitdiffs,1)[::(num_pts-1)]
        # Constructing (+, +, +, ...)
        xs.append(sum(pps))
        # Constructing the p vectors with one minus
	    # (-, +, + ...) + cyclic
        for procloc, mm in enumerate(mms):
            newvec = pps[0].copy()
            newvec.loc[:]=0
            subpps = pps.copy()
            del subpps[procloc]
            newvec = newvec + sum(subpps) + mm
            xs.append(newvec)
    elif (num_pts == 5) and (fivetheories == "nobar"):
        pzs = splitdiffs[::(num_pts-1)]
        mzs = shuffle_list(splitdiffs,1)[::(num_pts-1)]
        zps = shuffle_list(splitdiffs,2)[::(num_pts-1)]
        zms = shuffle_list(splitdiffs,3)[::(num_pts-1)]
        xs = []
        # Constructing (+; 0, 0, 0 ...)
	    #              (-; 0, 0, 0 ...)
	    #              (0; +, +, + ...)
        xs.append(sum(pzs))
        xs.append(sum(mzs))
        xs.append(sum(zps))
        # Constructing the p vectors with one minus
        # (0; -, +, + ...) + cyclic
        for procloc, zm in enumerate(zms):
            newvec = zps[0].copy()
            newvec.loc[:] = 0
            subzps = zps.copy()
            del subzps[procloc]
            newvec = newvec + sum(subzps) + zm
            xs.append(newvec)
    elif (num_pts == 5) and (fivetheories == "bar"):
        pps = splitdiffs[::(num_pts-1)]
        mms = shuffle_list(splitdiffs,1)[::(num_pts-1)]
        pms = shuffle_list(splitdiffs,2)[::(num_pts-1)]
        mps = shuffle_list(splitdiffs,3)[::(num_pts-1)]
        xs = []
        # Constructing (+/-; +, + ...)
        xs.append(sum(pps))
        xs.append(sum(mps))
        # Constructing the 2p vectors with one minus
	    # (+; -, +, + ...) + cyclic
        for procloc, pm in enumerate(pms):
            newvec = pms[0].copy()
            newvec.loc[:] = 0
            subpps = pps.copy()
            del subpps[procloc]
            newvec = newvec + sum(subpps) + pm
            xs.append(newvec)
        # (-; -, +, + ...) + cyclic
        for procloc, mm in enumerate(mms):
            newvec = mms[0].copy()
            newvec.loc[:] = 0
            submps = mps.copy()
            del submps[procloc]
            newvec = newvec + sum(submps) + mm
            xs.append(newvec)
    elif (num_pts == 7) and (seventheories != "original"):
        pzs = splitdiffs[::(num_pts-1)]
        mzs = shuffle_list(splitdiffs,1)[::(num_pts-1)]
        zps = shuffle_list(splitdiffs,2)[::(num_pts-1)]
        zms = shuffle_list(splitdiffs,3)[::(num_pts-1)]
        pps = shuffle_list(splitdiffs,4)[::(num_pts-1)]
        mms = shuffle_list(splitdiffs,5)[::(num_pts-1)]
        xs = []
        # 7pt is the sum of 3pts and 5pts
        # 3pt-like part:
        xs.append(sum(pps))
        for procloc, mm in enumerate(mms):
            newvec = pps[0].copy()
            newvec.loc[:]=0
            subpps = pps.copy()
            del subpps[procloc]
            newvec = newvec + sum(subpps) + mm
            xs.append(newvec)
        # 5pt-like part:
        xs.append(sum(pzs))
        xs.append(sum(mzs))
        xs.append(sum(zps))
        for procloc, zm in enumerate(zms):
            newvec = zps[0].copy()
            newvec.loc[:] = 0
            subzps = zps.copy()
            del subzps[procloc]
            newvec = newvec + sum(subzps) + zm
            xs.append(newvec)
    elif num_pts == 9:
        pzs = splitdiffs[::(num_pts-1)]
        mzs = shuffle_list(splitdiffs,1)[::(num_pts-1)]
        zps = shuffle_list(splitdiffs,2)[::(num_pts-1)]
        zms = shuffle_list(splitdiffs,3)[::(num_pts-1)]
        pps = shuffle_list(splitdiffs,4)[::(num_pts-1)]
        mms = shuffle_list(splitdiffs,5)[::(num_pts-1)]
        pms = shuffle_list(splitdiffs,6)[::(num_pts-1)]
        mps = shuffle_list(splitdiffs,7)[::(num_pts-1)]
        xs = []
        # Constructing (+/-/0; +, +, ...)
        xs.append(sum(pps))
        xs.append(sum(mps))
        xs.append(sum(zps))
        # Constructing (+/-/0; -, +, + ...) + cyclic
        for procloc, zm in enumerate(zms):
            newvec = zps[0].copy()
            newvec.loc[:] = 0
            subzps = zps.copy()
            del subzps[procloc]
            newvec = newvec + sum(subzps) + zm
            xs.append(newvec)
        for procloc, pm in enumerate(pms):
            newvec = pps[0].copy()
            newvec.loc[:] = 0
            subpps = pps.copy()
            del subpps[procloc]
            newvec = newvec + sum(subpps) + pm
            xs.append(newvec)
        for procloc, mm in enumerate(mms):
            newvec = mps[0].copy()
            newvec.loc[:] = 0
            submps = mps.copy()
            del submps[procloc]
            newvec = newvec + sum(submps) + mm
            xs.append(newvec)
        # Constructing (+/-; 0, +, +, ...) + cyclic
        for procloc, pz in enumerate(pzs):
            newvec = pps[0].copy()
            newvec.loc[:] = 0
            subpps = pps.copy()
            del subpps[procloc]
            newvec = newvec + sum(subpps) + pz
            xs.append(newvec)
        for procloc, mz in enumerate(mzs):
            newvec = mps[0].copy()
            newvec.loc[:] = 0
            submps = mps.copy()
            del submps[procloc]
            newvec = newvec + sum(submps) + mz
            xs.append(newvec)
    # ------------------------------------------------
    # Orthonormalising vectors according to Gram-Schmidt
    ys = [x/np.linalg.norm(x) for x in xs]
    for i in range(1, len(xs)):
        for j in range(0,i):
            ys[i] = ys[i] - (ys[i].T.dot(ys[j]))[0][0]*ys[j]/np.linalg.norm(ys[j])
            ys[i] = ys[i]/np.linalg.norm(ys[i])
    # Projecting covariance matrix onto subspace of non-zero eigenvalues
    p = pd.concat(ys, axis=1)
    projected_matrix = (p.T).dot(covmat.dot(p))
    w, v_projected = la.eigh(projected_matrix)
    # Finding eigenvectors in data space
    v = p.dot(v_projected)
    return w, v

def theory_shift_test(shx_vector, evals_nonzero_basis):
    """Compares the NNLO-NLO shift, f, with the eigenvectors and eigenvalues of the
    theory covariance matrix, and returns the component of the NNLO-NLO shift
    space which is missed by the covariance matrix space: fmiss, as well as the
    projections of the shift vector onto each of the eigenvectors: projectors."""
    w, v = evals_nonzero_basis
    v = np.real(v)
    # NNLO-NLO shift vector
    f = -shx_vector[0].values.T[0]
    # Projecting the shift vector onto each of the eigenvectors
    projectors = np.sum(f*v.T, axis=1)
    # Initialise array of zeros and set precision to same as FK tables
    projected_evectors = np.zeros((len(projectors), (len(f))), dtype=np.float32)
    for i, projector in enumerate(projectors):
        projected_evectors[i] = projector*v[:,i]
    fmiss = f - np.sum(projected_evectors, axis=0)
    return w, v, projectors, f, fmiss

@table
def theory_covmat_eigenvalues(theory_shift_test):
    """Returns a table of s = sqrt(eigenvalue), the projector and
    the ratio of the two, ordered by largest eigenvalue."""
    w = theory_shift_test[0]
    projectors = theory_shift_test[2]
    s = np.sqrt(np.abs(w))
    projectors = np.ndarray.tolist(projectors)
    ratio= projectors/s
    table = pd.DataFrame([s[::-1], projectors[::-1], ratio[::-1]],
                         index = [r'$s_a$', r'$\delta_a$', r'$\delta_a/s_a$'],
                         columns = np.arange(1,len(s)+1,1))
    return table

def efficiency(theory_shift_test):
    """Returns (efficiency = 1 - fmiss/f) with which the theory
    covariance matrix encapsulates the NNLO-NLO shift."""
    f = theory_shift_test[3]
    fmiss = theory_shift_test[4]
    fmod = np.sqrt(np.sum(f**2))
    fmiss_mod = np.sqrt(np.sum(fmiss**2))
    efficiency = 1 - fmiss_mod/fmod
    print(f"efficiency = {efficiency}")
    return efficiency

def validation_theory_chi2(theory_shift_test):
    """Returns the theory chi2 for comparing NNLO-NLO shift
    with theory covariance matrix."""
    projectors = theory_shift_test[2]
    evals = theory_shift_test[0]
    ratio = projectors/np.sqrt(np.abs(evals))
    th_chi2 = 1/len(evals)*np.sum(ratio**2)
    print(f"Theory chi2 = {th_chi2}")
    return th_chi2

@figure
def projector_eigenvalue_ratio(theory_shift_test):
    """Produces a plot of the ratio between the projectors and the square roots
    of the corresponding eigenvalues."""
    evals = theory_shift_test[0][::-1]
    projectors = theory_shift_test[2][::-1]
    fmiss = theory_shift_test[4]
    fmiss_mod = np.sqrt(np.sum(fmiss**2))
    ratio = np.abs(projectors)/np.sqrt(np.abs(evals))
    # Initialise array of zeros and set precision to same as FK tables
    # Ordering according to shift vector
    mask = np.argsort(np.abs(projectors))[::-1]
    evals = np.asarray(evals)[mask]
    projectors = projectors[mask]
    ratio = ratio[mask]
    xvals = np.arange(1,len(evals)+1,1)
    # Plotting
    fig, (ax1, ax2) = plt.subplots(2, figsize=(5,5))
    ax1.plot(xvals, np.abs(projectors), 's', label = r'|$\delta_a$|')
    ax1.plot(xvals, np.sqrt(np.abs(evals)), 'o', label = r'$|s_a|$')
    ax1.plot(0, fmiss_mod, '*', label=r'$|\delta_{miss}|$', color='b')
    ax2.plot(xvals,ratio, 'D', color="red")
    ax2.plot(0,0, '.', color="w")
    ax1.set_title(f"Number of eigenvalues = {len(evals)}", fontsize=10)
    ax1.set_yscale('log')
    ax2.set_yscale('log')
    ax1.legend()
    labels = [item.get_text() for item in ax1.get_xticklabels()]
    ax1.set_xticklabels(labels)
    ax2.set_xticklabels(labels)
    ax2.axhline(y=3, color='k', label=r'|$\delta_a$/$s_a$| = 3')
    ax2.legend()
    ax2.set_ylabel(r"|$\delta_a$/$s_a$|")
    print(f"Subspace dimension = {len(evals)}")
    return fig

@figure
def shift_diag_cov_comparison(shx_vector, thx_covmat, thx_vector):
    """Produces a plot of a comparison between the NNLO-NLO shift and the
    envelope given by the diagonal elements of the theory covariance matrix."""
    matrix = thx_covmat[0]/(np.outer(thx_vector[0], thx_vector[0]))
    fnorm = -shx_vector[0]
    indexlist = list(matrix.index.values)
    # adding process index for plotting, and reindexing matrices and vectors
    dsnames = []
    processnames= []
    ids = []
    for index in indexlist:
        name = index[0]
        i = index[1]
        dsnames.append(name)
        ids.append(i)
        proc = _process_lookup(name)
        processnames.append(proc)
    tripleindex = pd.MultiIndex.from_arrays([processnames, dsnames, ids],
                        names = ("process", "dataset", "id"))
    matrix = pd.DataFrame(matrix.values, index=tripleindex, columns=tripleindex)
    matrix.sort_index(0, inplace=True)
    matrix.sort_index(1, inplace=True)
    oldindex = matrix.index.tolist()
    newindex = sorted(oldindex, key=_get_key)
    matrix = matrix.reindex(newindex)
    matrix = (matrix.T.reindex(newindex)).T
    sqrtdiags = np.sqrt(np.diag(matrix))
    fnorm = pd.DataFrame(fnorm.values, index=tripleindex)
    fnorm.sort_index(0, inplace=True)
    fnorm = fnorm.reindex(newindex)
    # Plotting
    fig, ax = plt.subplots(figsize=(20,10))
    ax.plot(sqrtdiags*100, '.-', label="Theory", color = "red")
    ax.plot(-sqrtdiags*100, '.-', color = "red")
    ax.plot(fnorm.values*100, '.-', label="NNLO-NLO Shift", color = "black")
    ticklocs, ticklabels, startlocs = matrix_plot_labels(matrix)
    plt.xticks(ticklocs, ticklabels, rotation=45, fontsize=20)
    ax.vlines(startlocs, -70, 70, linestyles='dashed')
    ax.margins(x=0, y=0)
    ax.set_ylabel("% of central theory", fontsize=20)
    ax.legend(fontsize=20)
    ax.yaxis.set_tick_params(labelsize=20)
    return fig
