# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00-nar-trie-inference-benchmarking.ipynb.

# %% auto 0
__all__ = ['block', 'args', 'mname', 'model', 'trie', 'metric', 'learn', 'metrics']

# %% ../nbs/00-nar-trie-inference-benchmarking.ipynb 4
import os, pandas as pd, warnings
from tqdm.auto import tqdm

from xcai.basics import *
from xcai.models.MMM00X import BT0002, RT0005

# %% ../nbs/00-nar-trie-inference-benchmarking.ipynb 9
os.environ['WANDB_MODE'] = 'disabled'

block = XCBlock.from_cfg('data', valid_pct=0.001, tokz='roberta-base')

args = XCLearningArguments(
    output_dir='/scratch/scai/phd/aiz218323/Projects/xc_nlg/outputs/default',
    generation_length_penalty=1.5,
    per_device_eval_batch_size=64,
    evaluation_strategy='steps',
    label_names=['lbl2data_idx'],
)

mname = '/home/scai/phd/aiz218323/Projects/XC_NLG/code/models/roberta-base_LM-NAR_LF-WikiSeeAlso-320K/checkpoint-174000'
model = RT0005.from_pretrained(mname, tn_targ=10_000, ig_tok=1)

trie = XCTrie.from_block(block)

# %% ../nbs/00-nar-trie-inference-benchmarking.ipynb 10
metric = PrecRecl(block.n_lbl, block.test.data_lbl_filterer, 
                  prop=block.train.dset.data.data_lbl, pk=10, rk=10, rep_pk=[1, 3, 5, 10], rep_rk=[10])

learn = XCLearner(
    model=model, 
    args=args,
    trie=trie,
    data_collator=block.collator, 
    compute_metrics=metric,
)

metrics = learn.evaluate(block.test.dset)
print(metrics)
