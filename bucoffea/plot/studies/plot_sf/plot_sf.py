#!/usr/bin/env python
import os
import uproot
from matplotlib import pyplot as plt
import matplotlib
pjoin = os.path.join

font = {'family' : 'normal',
        'size'   : 14}

matplotlib.rc('font', **font)

name = {
    'gjets' : '$\gamma$ + jets',
    'wjets' : 'W + jets',
    'zjets' : 'Z + jets',
}
def plot_nlo_ewk():
    outdir = './output'
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    fig = plt.gcf()
    fig.clf()
    for tag in ['gjets','zjets','wjets']:
        f = uproot.open(f'../../../data/sf/theory/merged_kfactors_{tag}.root')
        h = f['kfactor_monojet_ewk']
        plt.plot(0.5*(h.bins[:,0]+h.bins[:,1]), h.values,'o-', label=name[tag])
    plt.ylabel('LO -> NLO EWK SF')
    plt.xlabel('Boson $p_{T}$ (GeV)')

    plt.legend()
    fig.savefig(pjoin(outdir, f'nlo_ewk.pdf'))

def plot_consistency():
    outdir = './output'
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    fig = plt.gcf()
    fig.clf()
    for tag in ['zjets','wjets']:
        f = uproot.open(f'../../../data/sf/theory/merged_kfactors_{tag}.root')
        qcd = f['kfactor_monojet_qcd']
        ewk = f['kfactor_monojet_ewk']
        both = f['kfactor_monojet_qcd_ewk']

        plt.plot(0.5*(both.bins[:,0]+both.bins[:,1]), both.values,'o-', label=name[tag])
        plt.plot(0.5*(both.bins[:,0]+both.bins[:,1]), qcd.values*ewk.values,'o-', label=name[tag])
    plt.ylabel('LO -> NLO EWK SF')
    plt.xlabel('Boson $p_{T}$ (GeV)')

    plt.legend()
    fig.savefig(pjoin(outdir, f'consistency.pdf'))

plot_consistency()
plot_nlo_ewk()
    