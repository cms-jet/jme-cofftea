#!/usr/bin/env python3

"""
Python3 script to plot numerator and denominator regions for a given trigger, on the same plot.

Usage:

> ./plot_num_and_den.py /path/to/merged/coffea/files -t <trigger1> <trigger2> ... -v <variableName> -d <dataset>

where:

    - <trigger1> ...  : Space-separated name of triggers for which to plot numerator and denominator regions.
    - <variableName>  : Name of the variable to plot the efficiency for.
    - <dataset>       : Name of the dataset to use, which also can be a regular expression to match multiple datasets at once.

An example with Muon 2023 dataset, to plot numerator and denominator regions for some single jet triggers as a function of pt:

> ./plot_num_and_den.py /path/to/merged/coffea/files -t HLT_PFJet320 HLT_PFJet500 ... -v ak4_pt0 -d 'Muon.*2023.*'

"""


import os
import re
import argparse

from matplotlib import pyplot as plt
from coffea import hist
from klepto.archives import dir_archive

from jmecofftea.plot.style import trigger_names, binnings, markers, get_xaxis_range

pjoin = os.path.join


def parse_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("inpath", help="Path to the directory with the merged coffea files.")
    parser.add_argument("-t", "--triggers", nargs="+", help="The name of the triggers (space-separated) to plot numerator and denominator.")
    parser.add_argument("-v", "--variable", help="The name of the variable to plot.")
    parser.add_argument("-d", "--dataset",  help="Regular expression for the dataset to be processed.")

    args = parser.parse_args()
    return args


def plot_num_and_den(acc, outdir, triggers, dataset, variable, logy=True):
    """
    Plot numerator and denominator regions for the given list of triggers.
    """
    acc.load(variable)
    h = acc[variable]

    # Get the dataset(s) we're interested in
    h = h.integrate("dataset", re.compile(dataset))

    for trigger in triggers:
        print(f"Plotting num/denom regions for: {trigger}")
    
        # Filter the regions in the histogram
        histo = h[re.compile(f"{trigger}.*")]

        # Plot
        fig, ax = plt.subplots()
        hist.plot1d(histo, ax=ax, overlay="region")

        if logy:
            ax.set_yscale("log")
            ax.set_ylim(1e0,1e8)

        # x-axis range
        xrange = get_xaxis_range(trigger)
        if xrange:
            ax.set_xlim(*xrange)

        # Save figure
        outpath = pjoin(outdir, f"{trigger}_num_den_{variable}.pdf")
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

    # Plot numerator and denominator regions for each trigger
    plot_num_and_den(
        acc,
        outdir,
        triggers=args.triggers,
        variable=args.variable,
        dataset=args.dataset
    )


if __name__ == "__main__":
    main()