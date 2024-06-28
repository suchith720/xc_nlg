# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/20-nar-training-pipeline-for-distilbert.ipynb.

# %% auto 0
__all__ = ['block', 'args', 'test_dset', 'metric', 'model', 'trie', 'learn']

# %% ../nbs/20-nar-training-pipeline-for-distilbert.ipynb 4
import os, torch
from xcai.basics import *
from xcai.models.MMM00X import DBT007
from xcai.transform import TriePruneInputIdsTfm

import matplotlib.pyplot as plt
set_plot_defaults()

# %% ../nbs/20-nar-training-pipeline-for-distilbert.ipynb 6
os.environ['CUDA_VISIBLE_DEVICES'] = '6,7'
os.environ['WANDB_PROJECT']='xc-nlg_20-nar-training-pipeline-for-distilbert'

# %% ../nbs/20-nar-training-pipeline-for-distilbert.ipynb 7
block = XCBlock.from_cfg('/home/aiscuser/scratch/datasets', 'data', valid_pct=0.001, tfm='xc', 
                         tokenizer='distilbert-base-uncased')

# %% ../nbs/20-nar-training-pipeline-for-distilbert.ipynb 13
args = XCLearningArguments(
    output_dir='/home/aiscuser/outputs/20-nar-training-pipeline-for-distilbert-2-1',
    logging_first_step=True,
    per_device_train_batch_size=128,
    per_device_eval_batch_size=128,
    representation_num_beams=200,
    representation_accumulation_steps=100,
    save_strategy="steps",
    evaluation_strategy='steps',
    eval_steps=2000,
    save_steps=2000,
    save_total_limit=5,
    num_train_epochs=50,
    adam_epsilon=1e-8,
    warmup_steps=0,
    weight_decay=0.1,
    learning_rate=1e-4,
    generation_num_beams=10,
    generation_length_penalty=1.5,
    predict_with_generation=True,
    label_names=['lbl2data_idx'],
)

# %% ../nbs/20-nar-training-pipeline-for-distilbert.ipynb 14
test_dset = block.test.dset.sample(n=2000, seed=50)
metric = PrecRecl(block.n_lbl, test_dset.data.data_lbl_filterer, prop=block.train.dset.data.data_lbl,
                  pk=10, rk=200, rep_pk=[1, 3, 5, 10], rep_rk=[10, 100, 200])

# %% ../nbs/20-nar-training-pipeline-for-distilbert.ipynb 15
model = DBT007.from_pretrained('distilbert-base-uncased', tn_targ=10_000, ig_tok=0)

# %% ../nbs/20-nar-training-pipeline-for-distilbert.ipynb 16
trie = XCTrie.from_block(block)

# %% ../nbs/20-nar-training-pipeline-for-distilbert.ipynb 17
learn = XCLearner(
    model=model, 
    args=args,
    trie=trie,
    train_dataset=block.train.dset,
    eval_dataset=test_dset,
    data_collator=block.collator,
    compute_metrics=metric,
)

# %% ../nbs/20-nar-training-pipeline-for-distilbert.ipynb 18
learn.train()
