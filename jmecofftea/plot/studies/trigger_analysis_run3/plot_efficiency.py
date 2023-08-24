#!/usr/bin/env python3

"""
Python3 script to plot efficiency curves for triggers. The first argument it takes is the path to the
directory having the merged coffea files (i.e., the output of jmerge). In addition, it will take arguments
about the trigger names, the variable name to compute efficiency as a function of and a dataset name,
as explained further below. 

Usage:

> ./plot_efficiency.py /path/to/merged/coffea/files -t <trigger1> <trigger2> ... -v <variableName> -d <dataset>

where:

    - <trigger1> ...  : Space-separated name of triggers for which to plot efficiency.
    - <variableName>  : Name of the variable to plot the efficiency for.
    - <dataset>       : Name of the dataset to use, which also can be a regular expression to match multiple datasets at once.

An example with Muon 2023 dataset, to plot some jet trigger efficiencies:

> ./plot_efficiency.py /path/to/merged/coffea/files -t HLT_PFJet320 HLT_PFJet500 ... -v ak4_pt0 -d 'Muon.*2023.*'

"""

import os
import re
import argparse

from matplotlib import pyplot as plt
from coffea import hist
from klepto.archives import dir_archive

from jmecofftea.plot.style import trigger_names, binnings, markers, get_xaxis_range

pjoin = os.path.join

Bin = hist.Bin

error_opts = markers('data')

def parse_cli():
    """Command line parser."""
    parser = argparse.ArgumentParser()
    parser.add_argument("inpath", help="Path to the merged coffea files.")
    parser.add_argument("-t", "--triggers",  nargs='+', help="Space separated name(s) of the triggers to plot efficiency for.")
    parser.add_argument("-v", "--variable",  help="The variable to plot efficiency for.")
    parser.add_argument("-d", "--dataset",   help="Regular expression for the dataset name to compute efficiency with.")
    
    args = parser.parse_args()
    return args


def plot_efficiency_for_trigger(acc, outdir, trigger, variable, dataset):
    """
    Plots the efficiency curve for the given trigger.

    acc:       The accumulator with the merged coffea files.
    outdir:    Output directory to save plots.
    trigger:   Name of the trigger to compute efficiency for.
    variable:  Variable to plot efficiency as a function of.
    dataset:   Regular expression matching the dataset name to use.
    """
    print(f"Plotting efficiency for trigger: {trigger}")

    acc.load(variable)
    h = acc[variable]

    # Get the dataset(s) we're interested in
    h = h.integrate("dataset", re.compile(dataset))

    # Get the numerator and denominator histograms
    h_num = h.integrate("region", f"{trigger}_num")
    h_den = h.integrate("region", f"{trigger}_den")

    # Plot the efficiency
    fig, ax = plt.subplots()
    hist.plotratio(
        h_num, h_den,
        ax=ax,
        error_opts=error_opts,
    )

    # Some aesthetics
    ax.axhline(1, xmin=0, xmax=1, ls='--', color='k')
    ax.set_ylabel("Trigger Efficiency")

    ax.text(1,1,trigger,
        fontsize=12,
        ha="right",
        va="bottom",
        transform=ax.transAxes
    )
    
    # x-axis range
    xrange = get_xaxis_range(trigger)
    if xrange:
        ax.set_xlim(*xrange)

    # Save figure
    outpath = pjoin(outdir, f"{trigger}_eff_{variable}.pdf")
    fig.savefig(outpath)
    plt.close(fig)

def main():
    args = parse_cli()
    inpath = args.inpath
    acc = dir_archive(inpath)
    
    # Output directory to save plots
    outtag = os.path.basename(inpath.rstrip('/'))
    outdir = f'./output/{outtag}'
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    # Plot the efficiency for each trigger provided in the CLI
    for trigger in args.triggers:
        plot_efficiency_for_trigger(
            acc, 
            outdir,
            trigger=trigger,
            variable=args.variable,
            dataset=args.dataset,
        )

if __name__ == "__main__":
    main()