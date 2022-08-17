#!/usr/bin/env python

import os
import sys
import gzip
import pickle
import argparse
import numpy as np

from coffea.util import load
from pprint import pprint
from collections import defaultdict
from tqdm import tqdm

from bucoffea.scripts.to_tree import files_by_dataset
from bucoffea.plot.util import load_xs, lumi
from bucoffea.helpers.dataset import extract_year, is_data

pjoin = os.path.join

def commandline():
    parser = argparse.ArgumentParser(prog='Convert coffea files to pickle files per dataset.')
    parser.add_argument('files', type=str, nargs='+', help='Input .coffea files to use.')

    args = parser.parse_args()

    return args

def dump_to_pickle(args):
    filelists = files_by_dataset(args.files)

    # The stuff we're interested in + which tree they're on
    inputs = {
        'tree_ndarray' : [
            'JetImage_E',
            'JetImage_Et',
        ],
        'tree_float16' : [
            'JetImage_nEtaBins',
            'JetImage_nPhiBins',
            'weight_total',
            'mjj',
            'detajj',
            'dphijj',
            'njet',
            'leadak4_pt',
            'leadak4_eta',
            'leadak4_phi',
            'trailak4_pt',
            'trailak4_eta',
            'trailak4_phi',
            'recoil_pt',
            'recoil_phi',
            'score_0',
            'score_1',
        ]
    }

    branchnames = inputs['tree_ndarray'] + inputs['tree_float16']

    xs_dict = load_xs()
    sumw_dict = defaultdict(int)

    for dataset, files in tqdm(filelists.items()):
        # In the pkl file, we'll save information for each dataset separately
        data = {b: [] for b in branchnames}
        
        for fname in files:
            acc = load(fname)
            sumw_dict[dataset] += acc['sumw'][dataset]

            for treename, inputlist in inputs.items():
                region = 'sr_vbf' if is_data(dataset) else 'sr_vbf_no_veto_all'
                t = acc[treename][region]
                for input in inputlist:

                    d = t[input].value
                    if len(d) == 0:
                        continue

                    # Stack 2D pixel inputs
                    if treename == 'tree_ndarray':
                        data[input].extend(np.stack(d, axis=0))
                    else:
                        # For some reason uproot won't write float16 dtypes -> convert to float64
                        data[input].extend(np.array(d, dtype=np.float64)) 

        # Save XS and sumw
        if is_data(dataset):
            data['xs'] = 1
            data['sumw'] = 1
        else:
            data['xs'] = xs_dict[dataset]
            data['sumw'] = sumw_dict[dataset]
        
        outpath = pjoin(args.outdir, f'{dataset}.pkl.gz')
        # Compression level: 1 (fastest) - 9 (most compression)
        # Some data sizes are quite large (>1 GB) and takes a while to compress...
        # Compression level = 4 is pretty good for our goals 
        with gzip.open(outpath, mode='wb', compresslevel=4) as f:
            pickle.dump(data,f)

def main():
    args = commandline()
    indir = os.path.dirname(args.files[0]).split('/')[-1]
    outdir = f'./pkl/{indir}'

    if not os.path.exists(outdir):
        os.makedirs(outdir)
    
    args.outdir = outdir

    dump_to_pickle(args)

if __name__ == '__main__':
    main()
