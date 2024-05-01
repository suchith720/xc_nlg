# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/09-anshul-trie-implementation.ipynb.

# %% auto 0
__all__ = ['dump_dir', 'fname', 'mname', 'model', 'args', 'metric', 'learn']

# %% ../nbs/09-anshul-trie-implementation.ipynb 2
import os, pandas as pd, warnings, torch, pickle, numpy as np
from typing import Dict, Optional, List
from tqdm.auto import tqdm
from scipy import stats
import scipy.sparse as sp
import torch.nn.functional as F
from itertools import chain

from xcai.basics import *
from xcai.models.MMM00X import DBT007, DBT008
from xcai.transform import AugmentMetaInputIdsTfm

# %% ../nbs/09-anshul-trie-implementation.ipynb 3
os.environ['WANDB_MODE'] = 'disabled'

# %% ../nbs/09-anshul-trie-implementation.ipynb 4
dump_dir = '/scratch/scai/phd/aiz218323/Projects/xc_nlg/outputs/05-metadata-augmented-input-and-trie-for-distilbert/'

# %% ../nbs/09-anshul-trie-implementation.ipynb 5
fname = '/scratch/scai/phd/aiz218323/Projects/xc_nlg/outputs/05-metadata-augmented-input-and-trie-for-distilbert/data/block.pkl'
with open(fname, 'rb') as f: block, test_dset = pickle.load(f)

# %% ../nbs/09-anshul-trie-implementation.ipynb 9
mname = f'/scratch/scai/phd/aiz218323/Projects/xc_nlg/outputs/05-metadata-augmented-input-and-trie-for-distilbert/distilbert-base-uncased_RB33-NAR-3+8-2_(mapped)LF-WikiSeeAlsoTitles-320K/checkpoint-190000'
model = DBT007.from_pretrained(mname, tn_targ=10_000, ig_tok=0)

# %% ../nbs/09-anshul-trie-implementation.ipynb 10
args = XCLearningArguments(
    output_dir=f'{dump_dir}/distilbert-base-uncased_RB33-NAR-3+8-2_(mapped)LF-WikiSeeAlsoTitles-320K',
    generation_length_penalty=1.5,
    per_device_eval_batch_size=16,
    evaluation_strategy='steps',
    label_names=['lbl2data_idx'],
)

# %% ../nbs/09-anshul-trie-implementation.ipynb 11
metric = PrecRecl(test_dset.n_lbl, test_dset.data.data_lbl_filterer, prop=block.train.dset.data.data_lbl,
                  pk=10, rk=200, rep_pk=[1, 3, 5, 10], rep_rk=[2, 3, 10, 50, 100, 200])

# %% ../nbs/09-anshul-trie-implementation.ipynb 12
learn = XCLearner(
    model=model, 
    args=args,
    data_collator=block.collator, 
    compute_metrics=metric,
)
