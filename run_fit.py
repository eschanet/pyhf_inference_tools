#!/usr/bin/env python

import getopt
import sys
import os, os.path
import glob

import ROOT
from ROOT import gROOT, gSystem, gDirectory, RooAbsData, RooRandom, RooWorkspace, TFile

from math import fabs, isnan

## batch mode
sys.argv.insert(1, "-b")
gROOT.Reset()
gROOT.SetBatch(True)
del sys.argv[1]
ROOT.gSystem.Load("{0}/lib/libSusyFitter.so".format(os.getenv("HISTFITTER")))
gROOT.Reset()

if __name__ == "__main__":
    from configManager import configMgr

    configMgr.verbose = False
    configMgr.readFromTree = False
    configMgr.executeHistFactory = False
    configMgr.calculatorType = 0
    configMgr.nTOYS = 1000
    runInterpreter = False
    doFixParameters = False
    fixedPars = ""

    from ROOT import RooFitResult, RooStats, Util

    print "\n * * * Welcome to HistFitter * * *\n"

    try:
        opts, args = getopt.getopt(sys.argv[1:], "twfin:c:s:v:alpg:x")
    except Exception as e:
        print (e)
        sys.exit(0)

    for opt, arg in opts:
        if opt == "-t":
            configMgr.readFromTree = True
        elif opt == "-w":
            configMgr.executeHistFactory = True
        elif opt == "-v":
            configMgr.setVerbose(int(arg))
        elif opt == "-c":
            doFixParameters = True
            fixedPars = str(arg)
        pass

    gROOT.SetBatch(True)

    infile_list = glob.glob("results/*/*_combined_NormalMeasurement_model.root")

    # I think I have to vomit ...
    Util.PatchedGenerateFitFromWorkspace(
        "myFitConfig",
        infile_list[0],
        "",
        False,
        False,
        False,
        False,
        False,
        False,
        "",
        doFixParameters,
        fixedPars,
        True,
        False,
        False,
    )

    print "Leaving HypoTest... Bye!"
