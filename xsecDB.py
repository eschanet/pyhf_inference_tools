#!/usr/bin/env python

import os
import pandas as pd


class CrossSectionDB:
    """
    A class for getting cross-sections (and filter efficiencies) from the central PMG xsec database.
    """

    db = pd.DataFrame()

    def __init__(
        self,
        dirname="/cvmfs/atlas.cern.ch/repo/sw/database/GroupData/dev/PMGTools/",
        filename="PMGxsecDB_mc16.txt",
        columns=[
            "dataset_number",
            "physics_short",
            "crossSection",
            "genFiltEff",
            "kFactor",
            "relUncertUP",
            "relUncertDOWN",
            "generator_name",
            "etag",
        ],
        separator="\t\t",
    ):

        self.filename = filename
        self.dirname = dirname

        self.db = pd.read_csv(
            os.path.join(dirname, filename),
            sep=separator,
            skiprows=1,
            header=None,
            names=columns,
        )

    def getMatch(self, field, dsid, etag=None):
        dsid = int(dsid)
        try:
            if etag:
                mask = (self.db["dataset_number"] == dsid) & (self.db["etag"] == etag)
            else:
                mask = (self.db["dataset_number"] == dsid)
            df = self.db.loc[mask, :]
        except Exception as e: # work on python 3.x
            print('Failed to get value: '+ str(e))
            return None

        if len(df.index) > 1:
            print(
                "More than one row with DSID "
                + str(dsid)
                + " found! Picking first one ..."
            )

        return df[field].values[0]

    def xsec(self, dsid, etag=None):
        return self.getMatch("crossSection", dsid, etag)

    def efficiency(self, dsid, etag=None):
        return self.getMatch("genFiltEff", dsid, etag)

    def kFactor(self, dsid, etag=None):
        return self.getMatch("kFactor", dsid, etag)

    def xsecTimesEff(self, dsid, etag=None):
        try:
            return self.xsec(dsid, etag) * self.efficiency(dsid, etag)
        except:
            return None

    def xsecTimesEffTimeskFac(self, dsid, etag=None):
        try:
            return self.xsec(dsid, etag) * self.efficiency(dsid, etag) * self.kFactor(dsid, etag)
        except:
            return None
