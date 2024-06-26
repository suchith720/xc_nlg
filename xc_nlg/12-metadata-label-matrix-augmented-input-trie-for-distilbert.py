# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/12-metadata-label-matrix-augmented-input-trie-for-distilbert.ipynb.

# %% auto 0
__all__ = ['dump_dir', 'fname', 'mname', 'model', 'args', 'metric', 'learn', 'data_lbl', 'lbl_lbl', 'meta_lbl', 'meta_toks',
           'meta_info', 'trie', 'o', 'pred_fname']

# %% ../nbs/12-metadata-label-matrix-augmented-input-trie-for-distilbert.ipynb 2
import os, pandas as pd, warnings, torch, pickle, numpy as np
from tqdm.auto import tqdm
from scipy import stats

import xclib.utils.sparse as xs

from xcai.basics import *
from xcai.models.MMM00X import DBT007, DBT008
from xcai.transform import AugmentMetaInputIdsTfm

# %% ../nbs/12-metadata-label-matrix-augmented-input-trie-for-distilbert.ipynb 3
os.environ['WANDB_MODE'] = 'disabled'

# %% ../nbs/12-metadata-label-matrix-augmented-input-trie-for-distilbert.ipynb 4
dump_dir = '/scratch/scai/phd/aiz218323/Projects/xc_nlg/outputs/12-metadata-label-matrix-augmented-input-trie-for-distilbert'

# %% ../nbs/12-metadata-label-matrix-augmented-input-trie-for-distilbert.ipynb 5
fname = '/scratch/scai/phd/aiz218323/Projects/xc_nlg/outputs/05-metadata-augmented-input-and-trie-for-distilbert/data/block.pkl'
with open(fname, 'rb') as f: block, test_dset = pickle.load(f)

# %% ../nbs/12-metadata-label-matrix-augmented-input-trie-for-distilbert.ipynb 7
mname = f'/scratch/scai/phd/aiz218323/Projects/xc_nlg/outputs/05-metadata-augmented-input-and-trie-for-distilbert/distilbert-base-uncased_RB33-NAR-3+8-2_(mapped)LF-WikiSeeAlsoTitles-320K/checkpoint-190000'
model = DBT007.from_pretrained(mname, tn_targ=10_000, ig_tok=0)

# %% ../nbs/12-metadata-label-matrix-augmented-input-trie-for-distilbert.ipynb 8
args = XCLearningArguments(
    output_dir=f'{dump_dir}/distilbert-base-uncased_RB33-NAR-3+8-2_(mapped)LF-WikiSeeAlsoTitles-320K',
    generation_length_penalty=1.5,
    per_device_eval_batch_size=16,
    evaluation_strategy='steps',
    label_names=['lbl2data_idx'],
)

# %% ../nbs/12-metadata-label-matrix-augmented-input-trie-for-distilbert.ipynb 10
metric = PrecRecl(block.n_lbl, block.test.data_lbl_filterer, prop=block.train.dset.data.data_lbl,
                  pk=10, rk=200, rep_pk=[1, 3, 5, 10], rep_rk=[2, 3, 10, 50, 100, 200])

# %% ../nbs/12-metadata-label-matrix-augmented-input-trie-for-distilbert.ipynb 11
learn = XCLearner(
    model=model, 
    args=args,
    data_collator=block.collator, 
    compute_metrics=metric,
)

# %% ../nbs/12-metadata-label-matrix-augmented-input-trie-for-distilbert.ipynb 13
data_lbl = block.train.dset.data.data_lbl
lbl_lbl = data_lbl.T.dot(data_lbl).tocsr()
lbl_lbl.setdiag(1)

# %% ../nbs/12-metadata-label-matrix-augmented-input-trie-for-distilbert.ipynb 14
meta_lbl = block.train.dset.meta.hlk_meta.lbl_meta.T@lbl_lbl

# %% ../nbs/12-metadata-label-matrix-augmented-input-trie-for-distilbert.ipynb 15
meta_toks = block.train.dset.meta.hlk_meta.meta_info['input_ids']
meta_info = [o.indices.tolist() for o in meta_lbl]

trie = Trie.from_list(meta_toks, meta_info)

# %% ../nbs/12-metadata-label-matrix-augmented-input-trie-for-distilbert.ipynb 16
learn.tbs.trie = trie

# %% ../nbs/12-metadata-label-matrix-augmented-input-trie-for-distilbert.ipynb 17
learn.tbs.n_bm = learn.args.generation_num_beams = 20

# %% ../nbs/12-metadata-label-matrix-augmented-input-trie-for-distilbert.ipynb 21
o = learn.predict(block.test.dset)
print(o.metrics)

# %% ../nbs/12-metadata-label-matrix-augmented-input-trie-for-distilbert.ipynb 22
pred_fname = f'{dump_dir}/distilbert-base-uncased_RB33-NAR-3+8-2_(mapped)LF-WikiSeeAlsoTitles-320K/checkpoint-190000/predictions/test_lbl_atrie-hlk_n-bm-20.pth'
os.makedirs(os.path.dirname(pred_fname), exist_ok=True)
torch.save(o, pred_fname)
