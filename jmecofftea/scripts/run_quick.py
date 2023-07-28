#!/usr/bin/env python

from jmecofftea.helpers.dataset import extract_year
from jmecofftea.processor.executor import run_uproot_job_nanoaod
from jmecofftea.helpers.cutflow import print_cutflow
from coffea.util import save
import coffea.processor as processor
import argparse

def parse_commandline():

    parser = argparse.ArgumentParser()
    parser.add_argument('processor', type=str, help='The processor to be run. (monojet or vbfhinv)')
    args = parser.parse_args()

    return args

def main():
    # 
    # Define the mapping between dataset name and the corresponding list of files we want to run on.
    # 
    fileset = {
        "Theo_Test_2023": [
            "/eos/user/t/tchatzis/CoffteaNTuples/muon2023C_CoffteaNTuple/data/out_1727.root"
        ],
    }

    # years = list(set(map(extract_year, fileset.keys())))
    # assert(len(years)==1)

    args = parse_commandline()
    processor_class = args.processor

    if args.processor == 'hlt':
        from jmecofftea.hlt.hltProcessor import hltProcessor
        processorInstance = hltProcessor()
        treename = 'Events'
    elif args.processor == 'jmenano':
        from jmecofftea.jmenano.jmeNanoProcessor import jmeNanoProcessor
        processorInstance = jmeNanoProcessor()
        treename = 'JMETriggerNTuple/Events'
    else:
        raise ValueError(f"Unknown value given for the processor argument: {args.processor}")

    for dataset, filelist in fileset.items():
        newlist = []
        for file in filelist:
            if file.startswith("/store/"):
                newlist.append("root://cms-xrd-global.cern.ch//" + file)
            else: newlist.append(file)
        fileset[dataset] = newlist

    executor_args = {
        "workers" : 4,
        "jmenano" : args.processor == "jmenano", # If jmenano=True, we're processing custom NTuples.
    }

    for dataset, filelist in fileset.items():
        print(f"Running on dataset: {dataset}")
        print(f"Number of files: {len(filelist)}")
        tmp = {dataset:filelist}

        output = run_uproot_job_nanoaod(tmp,
                                    treename=treename,
                                    processor_instance=processorInstance,
                                    executor=processor.futures_executor,
                                    executor_args=executor_args,
                                    chunksize=500000,
                                    )
        save(output, f"{processor_class}_{dataset}.coffea")
        # Debugging / testing output
        # debug_plot_output(output)
        print_cutflow(output, outfile=f'{processor_class}_cutflow_{dataset}.txt')

if __name__ == "__main__":
    main()
