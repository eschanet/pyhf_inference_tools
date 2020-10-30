# JSON Likelihoods for strong-1L Analysis

The JSON likelihoods are serialized in this folder. This is done by providing a background-only workspace containing the signal/control channels at `BkgOnly.json` as well as patch files for each mass point on the signal phase-space explored in the analysis.

All [jsonpatches](http://jsonpatch.com/) are contained in the file `patchset.json`. Each patch is identified in `patchset.json` by the metadata field `"name": "[XX]_oneStep_[m1]_[m2]_[m3]"` where `XX` is either `GG` for gluino pair production or `SS` for squark pair production, `m1` is the mass of the gluino or squark, and `m2` is the mass of the lightest chargino and [m3] is the mass of the lightest neutralino.

## Producing signal workspaces

As an example, we use [python jsonpatch](https://python-json-patch.readthedocs.io/en/latest/) to make the full json likelihood workspace for the signal point `"GG_oneStep_2000_1012_24"`:

```
jsonpatch BkgOnly.json <(pyhf patchset extract patchset.json --name "GG_oneStep_2000_1012_24") > GG_oneStep_2000_1012_24.json
```

## Computing signal workspaces

For example, with [pyhf](https://scikit-hep.org/pyhf/), you can do any of the following:

```
pyhf cls BkgOnly.json --patch <(pyhf patchset extract patchset.json --name "GG_oneStep_2000_1012_24")

jsonpatch BkgOnly.json <(pyhf patchset extract patchset.json --name "GG_oneStep_2000_1012_24.json") | pyhf cls

pyhf cls GG_oneStep_2000_1012_24.json
```

