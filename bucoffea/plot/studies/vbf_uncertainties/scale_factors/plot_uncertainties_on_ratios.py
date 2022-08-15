#!/usr/bin/env python

import os
import sys
import re
import uproot
import warnings
import argparse
import numpy as np
import mplhep as hep

from matplotlib import pyplot as plt
from coffea import hist
from tqdm import tqdm
from klepto.archives import dir_archive
from pprint import pprint

from bucoffea.plot.util import (
    merge_extensions, 
    merge_datasets, 
    scale_xs_lumi, 
    fig_ratio,
    rebin_histogram,
    )

from datasets import DATASETS

pjoin = os.path.join

warnings.filterwarnings(action='ignore', category=RuntimeWarning, module='coffea')

def parse_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('inpath', help='Path to the merged accumulator input.')
    parser.add_argument('-v', '--variable', help='The variable to plot the uncertainties for.', default='cnn_score', choices=['cnn_score','mjj'])
    args = parser.parse_args()
    return args


def plot_unc_on_ratios(acc, unc_name, unc_config, outdir, variable):
    """
    Computes and plots the given uncertainty on V+jets ratios.
    """
    # Get the histogram with the uncertainty
    distribution = unc_config['histogram']
    acc.load(distribution)
    h = acc[distribution]

    h = merge_extensions(h, acc, reweight_pu=False)
    scale_xs_lumi(h)
    h = merge_datasets(h)

    # Rebin histogram
    if variable == 'mjj':
        mjj_ax = hist.Bin('mjj', r'$M_{jj} \ (GeV)$', [200., 400., 600., 900., 1200., 1500.,2000., 2750., 3500., 5000.])
        h = h.rebin('mjj', mjj_ax)
    elif variable == 'cnn_score':
        h = rebin_histogram(h, 'cnn_score')
    else:
        raise ValueError(f'Non-valid variable specified: {variable}')

    # Output ROOT file
    if unc_config['outputroot']:
        outputrootfile = uproot.recreate(pjoin(outdir, unc_config['outputroot']['name']))

    if 'L1Prefire' in unc_name or 'pileup' in unc_name:
        axname = 'uncertainty'
    else:
        axname = 'variation'

    # Loop over different ratios and plot uncertainties
    for DATASET in DATASETS:
        if 'onlyRun' in unc_config and unc_config['onlyRun'] != DATASET['tag']:
            continue

        fig, ax, rax = fig_ratio()
        h_num = h.integrate('region', DATASET['num']['region'])\
            .integrate('dataset', re.compile(DATASET['num']['dataset']))
        h_den = h.integrate('region', DATASET['den']['region'])\
            .integrate('dataset', re.compile(DATASET['den']['dataset']))

        # Nominal ratio
        h_num_nom = h_num.integrate(axname, unc_config['nominal'])
        h_den_nom = h_den.integrate(axname, unc_config['nominal'])

        data_err_opts = {
            'linestyle':'none',
            'marker': '.',
            'markersize': 10.,
            'color':'k',
        }

        r_nom = h_num_nom.values()[()] / h_den_nom.values()[()]
        bins = h_num_nom.axes()[0].edges()
        hist.plotratio(
            h_num_nom, 
            h_den_nom, 
            ax=ax, 
            unc='num', 
            error_opts=data_err_opts,
            label='Nominal'
        )

        # Varied ratios
        varied_ratios = {}
        for var in unc_config['variations']:
            h_num_var = h_num.integrate(axname, var)
            h_den_var = h_den.integrate(axname, var)

            r = h_num_var.values()[()] / h_den_var.values()[()]
            hep.histplot(r, bins=h_num_var.axes()[0].edges(), ax=ax, label=var)

            varied_ratios[var] = r

        # Plot ratio of ratios at the bottom panel
        for var, ratio in varied_ratios.items():
            rr = ratio / r_nom
            hep.histplot(rr, bins=bins, ax=rax, label=var, histtype='errorbar')

            if unc_config['outputroot'] and DATASET['tag'] == unc_config['outputroot']['save']:
                histo_name = unc_config['outputroot']['histos'][var]
                outputrootfile[histo_name] = (rr, bins)

        ax.legend()
        ax.set_ylabel('Ratio')
        
        rax.legend()
        rax.set_xlabel(r'$M_{jj} \ (GeV)$')
        rax.set_ylabel('Uncertainty')
        
        rax.grid(True)
        if 'L1Prefire' in unc_name or 'pileup' in unc_name:
            rax.set_ylim(0.9,1.1)
        else:
            rax.set_ylim(0.97,1.03)
    
        outpath = pjoin(outdir, f'{unc_name}_{DATASET["tag"]}_{variable}.pdf')
        fig.savefig(outpath)
        plt.close(fig)


def main():
    args = parse_cli()

    acc = dir_archive(args.inpath)
    acc.load('sumw')

    outtag = os.path.basename(args.inpath.rstrip('/'))

    # Output directory to save plots
    outdir = f'./output/{outtag}'
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    # List of uncertainties we'll look at
    uncertainties = {
        'L1Prefire_2017' : {
            'histogram'   : f'{args.variable}_unc',
            'nominal'     : 'prefireNom',
            'variations'  : ['prefireUp', 'prefireDown'],
            'outputroot'  : {
                'name' : f'prefire_uncs_TF_{args.variable}.root',
                'save' : 'zvv_over_wlv',
                'histos' : {
                    'prefireUp' : 'CMS_L1prefire_2017Up',
                    'prefireDown' : 'CMS_L1prefire_2017Down',
                }
            },
        },
        # 'pileup' : {
        #     'histogram'   : f'{args.variable}_unc',
        #     'nominal'     : 'puSFNom',
        #     'variations'  : ['puSFUp', 'puSFDown'],
        #     'outputroot'  : None,
        # },
        # 'ele_id_veto' : {
        #     'histogram'   : 'mjj_veto_weight',
        #     'nominal'     : 'nominal',
        #     'variations'  : ['ele_id_up', 'ele_id_dn'],
        #     'outputroot'  : None,
        #     'onlyRun'     : 'zvv_over_wlv',
        # },
        # 'ele_reco_veto' : {
        #     'histogram'   : 'mjj_veto_weight',
        #     'nominal'     : 'nominal',
        #     'variations'  : ['ele_reco_up', 'ele_reco_dn'],
        #     'outputroot'  : None,
        #     'onlyRun'     : 'zvv_over_wlv',
        # },
        # 'muon_id_veto' : {
        #     'histogram'   : 'mjj_veto_weight',
        #     'nominal'     : 'nominal',
        #     'variations'  : ['muon_id_up', 'muon_id_dn'],
        #     'outputroot'  : None,
        #     'onlyRun'     : 'zvv_over_wlv',
        # },
        # 'muon_iso_veto' : {
        #     'histogram'   : 'mjj_veto_weight',
        #     'nominal'     : 'nominal',
        #     'variations'  : ['muon_iso_up', 'muon_iso_dn'],
        #     'outputroot'  : None,
        #     'onlyRun'     : 'zvv_over_wlv',
        # },
        # 'tau_id_veto' : {
        #     'histogram'   : 'mjj_veto_weight',
        #     'nominal'     : 'nominal',
        #     'variations'  : ['tau_id_up', 'tau_id_dn'],
        #     'outputroot'  : None,
        #     'onlyRun'     : 'zvv_over_wlv',
        # },
    }

    for unc_name, unc_config in tqdm(uncertainties.items(), desc="Plotting uncertainties"):
        plot_unc_on_ratios(
            acc,
            unc_name=unc_name,
            unc_config=unc_config,
            outdir=outdir,
            variable=args.variable,
        )


if __name__ == '__main__':
    main()
