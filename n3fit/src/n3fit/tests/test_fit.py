"""
    Regression tests for n3fit

    This file will run a fit with a runcard which includes:
        - A DIS dataset
        - A Hadronic dataset
        - Two positivity sets
    And checks that the results have not changed from the previous iteration of the code

    If the results are known to need a change,
    it is necessary to flag _something_ to regenerate regression
"""

import os
import shutil
import pathlib
import logging
import tempfile
import subprocess as sp
from numpy.testing import assert_almost_equal

log = logging.getLogger(__name__)
REGRESSION_FOLDER = pathlib.Path().absolute() / "regressions"
QUICKNAME = "quickcard"
QUICKCARD = pathlib.Path().absolute() / f"{QUICKNAME}.yml"
EXE = "n3fit"
REPLICA = "1"


def load_data(path):
    """ Loads the info file of the fit into a list """
    info_file = path / f"{QUICKNAME}/nnfit/replica_{REPLICA}/{QUICKNAME}.fitinfo"
    with open(info_file, "r") as f:
        info = f.read()
        return info.split()

def compare_two(val1, val2, precision = 6):
    """ Compares value 1 and value 2 attending to their type """
    try:
        num_1 = float(val1)
        num_2 = float(val2)
        assert_almost_equal(num_1, num_2, decimal = precision)
    except ValueError:
        assert val1 == val2


def compare_lines(set1, set2):
    """ Returns true if the lines within set1 and set2 are the same
    The numbers are compared up to `precision`
    """
    for val1, val2 in zip(set1, set2):
        compare_two(val1, val2)

def test_fit():
    # create a /tmp folder
    tmp_name = tempfile.mkdtemp(prefix="nnpdf-")
    tmp_path = pathlib.Path(tmp_name)
    # cp runcard to tmp folder
    shutil.copy(QUICKCARD, tmp_path)
    os.chdir(tmp_path)
    # run the fit
    run_command = [EXE, QUICKCARD, REPLICA]
    sp.run(run_command)
    # read up the .fitinfo files
    new_fitinfo = load_data(tmp_path)
    old_fitinfo = load_data(REGRESSION_FOLDER)
    # compare to the previous .fitinfo file
    compare_lines(new_fitinfo, old_fitinfo)
