## Pyhf conversion workflow

This repository gathers a bunch of scripts and tools to convert the HF output from an analysis into pyhf workspaces (`BkgOnly.json` and `patchset.json`). It also allows to create simplified versions of the likelihood using `simplify`. It further allows to cross-check the results of the simplified likelihood by comparing them with the full results from the analysis.

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