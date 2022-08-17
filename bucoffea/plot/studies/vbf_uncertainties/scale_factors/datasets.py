# List of dataset ratios we'll look at for uncertainties
DATASETS = [
    {
        'tag' : 'zvv_over_wlv',
        'num': {
            'dataset': 'ZNJetsToNuNu_M-50_LHEFilterPtZ-FXFX_2017',
            'region' : 'sr_vbf_no_veto_all'
        },
        'den': {
            'dataset': 'WJetsToLNu_Pt-FXFX_2017',
            'region' : 'sr_vbf_no_veto_all',
        },
    },
    {
        'tag' : 'zvv_over_zmm',
        'num': {
            'dataset': 'ZNJetsToNuNu_M-50_LHEFilterPtZ-FXFX_2017',
            'region' : 'sr_vbf_no_veto_all'
        },
        'den': {
            'dataset': 'DYJetsToLL.*Pt.*FXFX_2017',
            'region' : 'cr_2m_vbf',
        },
    },
    {
        'tag' : 'zvv_over_zee',
        'num': {
            'dataset': 'ZNJetsToNuNu_M-50_LHEFilterPtZ-FXFX_2017',
            'region' : 'sr_vbf_no_veto_all'
        },
        'den': {
            'dataset': 'DYJetsToLL.*Pt.*FXFX_2017',
            'region' : 'cr_2e_vbf',
        },
    },
    {
        'tag' : 'zvv_over_gjets',
        'num': {
            'dataset': 'ZNJetsToNuNu_M-50_LHEFilterPtZ-FXFX_2017',
            'region' : 'sr_vbf_no_veto_all'
        },
        'den': {
            'dataset': 'GJets_DR-0p4_HT_MLM_2017',
            'region' : 'cr_g_vbf',
        },
    },
    {
        'tag' : 'wlv_over_wmunu',
        'num': {
            'dataset': 'WJetsToLNu_Pt-FXFX_2017',
            'region' : 'sr_vbf_no_veto_all'
        },
        'den': {
            'dataset': 'WJetsToLNu_Pt-FXFX_2017',
            'region' : 'cr_1m_vbf',
        },
    },
    {
        'tag' : 'wlv_over_wenu',
        'num': {
            'dataset': 'WJetsToLNu_Pt-FXFX_2017',
            'region' : 'sr_vbf_no_veto_all'
        },
        'den': {
            'dataset': 'WJetsToLNu_Pt-FXFX_2017',
            'region' : 'cr_1e_vbf',
        },
    },
]