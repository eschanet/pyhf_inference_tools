#!/usr/bin python3

import uproot
import pandas
import numpy as np

from atlasify import atlasify

import matplotlib.pyplot as plt

tree = uproot.open("/project/etp1/eschanet/pMSSM_scan/EW_Jeanette_test_run_1/susy-EricRun2_v2.root")
tree = tree["susy"]
df_tree = tree.pandas.df()
df_tree = df_tree.replace({"LSP_type": {1000024:4}})
df_tree = df_tree.fillna(-1)

fig, ax = plt.subplots()
fig.set_size_inches(5, 4)

plt.locator_params(axis='x', nbins=8)

df_tree = df_tree[abs(df_tree['EWSmear_ObsCLs_EwkOneLeptonTwoBjets2018__pyhfFit'])  > 0.0 ]
df_tree = df_tree[abs(df_tree['EWSmear_ObsCLs_EwkOneLeptonTwoBjets2018__fullLikelihood'])  > 0.0 ]

df_tree['abs_SR_h_Low'] = abs(df_tree['EWSmear_ObsCLs_EwkOneLeptonTwoBjets2018__SR_h_Low'])
df_tree['abs_SR_h_Med'] = abs(df_tree['EWSmear_ObsCLs_EwkOneLeptonTwoBjets2018__SR_h_Med'])
df_tree['abs_SR_h_High'] = abs(df_tree['EWSmear_ObsCLs_EwkOneLeptonTwoBjets2018__SR_h_High'])

y = abs(df_tree['EWSmear_ObsCLs_EwkOneLeptonTwoBjets2018__pyhfFit'])
x = abs(df_tree['EWSmear_ObsCLs_EwkOneLeptonTwoBjets2018__fullLikelihood'])
x2 = df_tree[['abs_SR_h_Low','abs_SR_h_Med','abs_SR_h_High']].min(axis=1)

# ax.scatter(x,y, s=20, facecolors='none', edgecolors='#686de0')
# ax.scatter(x2,y, s=20, facecolors='none',label='Single-bin likelihood', edgecolors='#686de0')
ax.scatter(x,y, s=20, facecolors='none',label='Full likelihood', edgecolors='#10ac84')

ax.plot((0, 1), linestyle='--', linewidth=1.2, c='#444444')
ax.axhspan(0.025, 0.075, alpha=0.1, edgecolor='none', color='red')

ax.legend(loc='upper left', bbox_to_anchor=(-0.01, 0.77))
ax.set_ylim([0,0.2])
ax.set_xlim([0,0.2])

# ax.set_xscale('log')
# ax.set_yscale('log')


# plt.xlabel('Discovery SRs',ha='right', x=1.0)
# plt.xlabel('Single-bin or full likelihood (obs. CLs)',ha='right', x=1.0)
plt.xlabel('Full likelihood (obs. CLs)',ha='right', x=1.0)
plt.ylabel('Simplified likelihood (obs. CLs)',ha='right', y=1.0)
fig.tight_layout()

atlasify.atlasify(  "Internal",
                    "$\sqrt{s}$ = 13 TeV, 139 fb$^{-1}$\n"
                    "5k pMSSM models",
                    enlarge=1.0, outside=False)
ax.minorticks_on()
# plt.tick_params(axis = "x", which = "both", bottom = False, top = False)

plt.savefig('mpl/fit_scatter_likelihoods_log.pdf')
