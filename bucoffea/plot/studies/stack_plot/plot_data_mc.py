#!/usr/bin/env python
import argparse
import warnings
import os
import re
import numpy as np
import mplhep as hep

from bucoffea.plot.plotter import plot_data_mc
from klepto.archives import dir_archive
from pprint import pprint
from distributions import distributions
from datetime import datetime
from tqdm import tqdm

pjoin = os.path.join

warnings.filterwarnings('ignore', category=RuntimeWarning)

def make_plot(args):
    acc = dir_archive(args.inpath)
    acc.load('sumw')
    acc.load('sumw2')

    outtag = re.findall('merged_.*', args.inpath)[0].replace('/','')

    for year in args.years:
        data = {
            'sr_vbf' : f'MET_{year}',
            'cr_1m_vbf' : f'MET_{year}',
            'cr_2m_vbf' : f'MET_{year}',
            'cr_1e_vbf' : f'EGamma_{year}',
            'cr_2e_vbf' : f'EGamma_{year}',
            'cr_g_vbf'  : f'EGamma_{year}',
        }

        mc = {
            'sr_vbf_no_veto_all' : re.compile(f'(ZNJetsToNuNu_M-50_LHEFilterPtZ-FXFX.*|EW.*|Top_FXFX.*|Diboson.*|DYJetsToLL_Pt_FXFX.*|WJetsToLNu_Pt-FXFX.*).*{year}'),
            'cr_1m_vbf' : re.compile(f'(EWKW.*|EWKZ.*ZToLL.*|Top_FXFX.*|Diboson.*|DYJetsToLL_Pt_FXFX.*|WJetsToLNu_Pt-FXFX.*).*{year}'),
            'cr_1e_vbf' : re.compile(f'(EWKW.*|EWKZ.*ZToLL.*|Top_FXFX.*|Diboson.*|DYJetsToLL_Pt_FXFX.*|WJetsToLNu_Pt-FXFX.*).*{year}'),
            'cr_2m_vbf' : re.compile(f'(EWKZ.*ZToLL.*|Top_FXFX.*|Diboson.*|DYJetsToLL_Pt_FXFX.*).*{year}'),
            'cr_2e_vbf' : re.compile(f'(EWKZ.*ZToLL.*|Top_FXFX.*|Diboson.*|DYJetsToLL_Pt_FXFX.*).*{year}'),
            'cr_g_vbf' : re.compile(f'(GJets_DR-0p4.*|VBFGamma.*|QCD_data.*|WJetsToLNu.*HT.*).*{year}'),
        }

        for data_region in data.keys():
            if not re.match(args.region, data_region):
                continue

            # Parameter to scale the MC by a constant normalization factor
            mcscale = args.mcscale
            # If we want to do 1/5th unblinding on the data
            if args.one_fifth_unblind and data_region == 'sr_vbf':
                mcscale *= 0.2

            # Pick the signal region with veto weights (instead of hard-lepton veto)
            # for the VBF signal region
            if data_region == 'sr_vbf':
                mc_region = 'sr_vbf_no_veto_all'
            else:
                mc_region = data_region

            for distribution in tqdm(distributions[data_region], desc="Plotting distributions"):
                if not re.match(args.distribution, distribution):
                    continue
                try:
                    plot_data_mc(acc, outtag, year,
                        data=data[data_region],
                        mc=mc[mc_region],
                        data_region=data_region,
                        mc_region=mc_region,
                        distribution=distribution,
                        mcscale=mcscale,
                        plot_signal='sr_vbf' in data_region,
                        jes_file='./jec/jes_uncs.root' if args.jes else None,
                        ulxs=not args.eoyxs,
                        fformats=args.fformats,
                    )
                except KeyError:
                    print(f'WARNING: {data_region} not found in inputs, skipping.')
                    continue

def commandline():
    parser = argparse.ArgumentParser(prog='Plotter.')
    parser.add_argument('inpath', type=str, help='Input folder to use.')
    parser.add_argument('--region', type=str, default='.*', help='Regex specifying the analysis regions to plot.')
    parser.add_argument('--distribution', type=str, default='.*', help='Regex specifying the distributions to plot.')
    parser.add_argument('--years', type=int, nargs='*', default=[2017,2018], help='Years to run on.')
    parser.add_argument('--one_fifth_unblind', action='store_true', help='1/5th unblinded data.')
    parser.add_argument('--fformats', nargs='*', default=['pdf'], help='Output file format for the plots, default is PDF only.')
    parser.add_argument('--jes', action='store_true', help='Plot JES+JER uncertainty bands.')
    parser.add_argument('--eoyxs', action='store_true', help='Use EOY XS for normalization, otherwise use UL XS.')
    parser.add_argument('--mcscale', type=float, default=1.0, help='Scale the MC by the given value.')
    args = parser.parse_args()
    return args

def dump_info(args):
    outdir = pjoin('./output/',list(filter(lambda x:x,args.inpath.split('/')))[-1])

    # Store the command line arguments in the INFO.txt file
    try:
        os.makedirs(outdir)
    except FileExistsError:
        pass
    
    infofile = pjoin(outdir, 'INFO.txt')
    with open(infofile, 'w+') as f:
        f.write(f'Plot script most recently created at: {datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}\n')
        f.write('Command line arguments:\n\n')
        cli = vars(args)
        for arg, val in cli.items():
            f.write(f'{arg}: {val}\n')

def main():
    args = commandline()
    dump_info(args)
    make_plot(args)    

if __name__ == "__main__":
    main()