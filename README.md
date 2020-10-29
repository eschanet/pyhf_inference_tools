## Pyhf conversion workflow

This repository gathers a bunch of scripts and tools to convert the HF output from an analysis into pyhf workspaces (`BkgOnly.json` and `patchset.json`). It also allows to create simplified versions of the likelihood using `simplify`. It further allows to cross-check the results of the simplified likelihood by comparing them with the full results from the analysis.

Parts of this repository's scripts are inspired by gstark's [comnpress+3Loffshell combination infrastructure](https://gitlab.cern.ch/gstark/ewk-combination-3loffshell-compressed).

### Signal patch

Creating a signal patch is as easy as running

```
python3 make_signalpatch.py --bkg-only <BkgOnly.json> --output-file <output-file>
```

### Simplified signal patch

A simplified signal patch only contains nominal signal yields and no uncertainties. You can construct such a signal patch file from any full signal patch file using

```
python3 make_simplified_signalpatch.py --group <group> --output-file <output-file>
```

### Fitting all workspaces

Fitting all workspaces can be done using 

```
python3 run_cls.py --group <group>
```

Alternatively, once can also use `run_patchset.py` to run over an existing set of `BkgOnly.json` and `patchset.json` files built e.g. using `make_signalpatch.py` from above.


### Running fit over entire patchset

Running a fit over the entire patchset using a provided likelihood can be done using:

```
python3 run_patchset.py --group <group>
```

This defaults to using the full likelihood. You can also specify `--simplified` in order to run using the simplified likelihood.


### Creating harvest

The results of the fits need to be harvested and converted into the right format for the HistFitter plotting tools to be able to use them. This can be done by running

```
python3 harvest.py --group <group>
```

### Plotting results

