"""
arclength.py

Module for the computation and presentation of arclengths.
"""
from collections import namedtuple, Sequence
import numbers

import numpy as np
import pandas as pd

from reportengine.figure import figure
from reportengine.table import table
from reportengine.checks import check_positive, make_argcheck

from validphys.pdfbases import Basis, check_basis, PDG_PARTONS
from validphys.pdfgrids import (xgrid, xplotting_grid)
from validphys.plots    import check_normalize_to
from validphys.core     import PDF

import matplotlib.pyplot as plt

#TODO This (or something like it) should be in Basis
damping_factors={r'\Sigma':True, 'g':True, 'photon':True,
                 'V':False, 'V3':False, 'V8':False,'V15':False, 'V24':False, 'V35':False,
                 'T3':True, 'T8':True, 'T15':True, 'T24':True,'T35':True}
for val in PDG_PARTONS:
    damping_factors[val] = True

ArcLengthGrid = namedtuple('ArcLengthGrid', ('basis', 'flavours', 'values'))
@check_positive('Q')
@make_argcheck(check_basis)
# Using the same questionable integration as validphys
def arc_lengths(pdf:PDF, Q:numbers.Real, 
                basis:(str, Basis)='flavour',
                flavours:(list, tuple, type(None))=None):
    """Compute arc lengths at scale Q"""
    lpdf = pdf.load()
    nmembers = lpdf.GetMembers()
    checked = check_basis(basis, flavours)
    basis, flavours = checked['basis'], checked['flavours']
    # x-grid points and limits in three segments
    npoints = 199 #200 intervals
    seg_min = [1e-6, 1e-4, 1e-2]
    seg_max = [1e-4, 1e-2, 1.0 ]
    res = np.zeros((len(flavours), nmembers))
    # Integrate the separate segments
    for iseg in range(len(seg_min)):
        a, b = seg_min[iseg], seg_max[iseg]
        eps = (b-a)/(npoints-1)
        x1grid = xgrid(a, b, 'linear', npoints)                  # Integration x-grid
        x0grid = xgrid(a-eps, b-eps, 'linear', npoints)          # x1 - epsilon
        f1grid = xplotting_grid(pdf, Q, x1grid, basis, flavours) # PDFs evaluated at x
        f0grid = xplotting_grid(pdf, Q, x0grid, basis, flavours) # PDFs evaluated at x-eps
        dfgrid = f1grid.grid_values - f0grid.grid_values         # Backwards-difference
        np.swapaxes(dfgrid, 1,2)
        for irep in range(nmembers):
            for ifl,fl in enumerate(flavours):
                dslice = dfgrid[irep][ifl]
                asqr = np.square(dslice * x1grid[1]) if damping_factors[fl] else np.square(dslice)
                res[ifl,irep] += np.sum(np.sqrt(eps*eps+asqr))
    return ArcLengthGrid(basis, flavours, res)

#@table
#def arc_length_table(arc_lengths):
#    """Return a table with the descriptive statistics of the arc lengths
#    over members of the PDF."""
#    #We don't  really want the count, which is going to be the same for all.
#    #Hence the .iloc[1:,:].
#    return pd.DataFrame(arc_lengths.values._asdict()).describe().iloc[1:,:]

@figure
@check_normalize_to
#TODO Should plot 68% C.I. Rather than stddev
def plot_arc_lengths(pdfs:Sequence, Q:numbers.Real, normalize_to:(type(None),int)=None):
    """Plot the arc lengths of a PDF set"""
    fig, ax = plt.subplots()
    if normalize_to is not None:
        ax.set_ylabel("Arc length (normalised)")
    else:
        ax.set_ylabel("Arc length")

    norm_cv = None
    if normalize_to is not None:
        norm_al = arc_lengths(pdfs[normalize_to], Q).values
        norm_cv = [ np.mean(fl) for fl in norm_al ]

    for ipdf, pdf in enumerate(pdfs):
        arclengths = arc_lengths(pdf, Q)
        alvalues = arclengths.values
        xvalues = np.array(range(len(arclengths.flavours)))
        xlabels  = [ '$'+arclengths.basis.elementlabel(fl)+'$' for fl in arclengths.flavours]
        yvalues = [ np.mean(fl) for fl in alvalues ]
        yerrors = [ np.std(fl)  for fl in alvalues]
        if norm_cv is not None:
            yvalues = np.divide(yvalues, norm_cv)
            yerrors = np.divide(yerrors, norm_cv)
        ##TODO should do a better job of this shift
        ax.errorbar(xvalues + ipdf/5.0, yvalues, yerr = yerrors, fmt='.', label=pdf.label)
        ax.set_xticks(xvalues)
        ax.set_xticklabels(xlabels)
        ax.legend()
    return fig
