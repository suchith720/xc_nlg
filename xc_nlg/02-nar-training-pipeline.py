# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/02-nar-training-pipeline.ipynb.

# %% auto 0
__all__ = ['block', 'args', 'metric', 'model', 'trie', 'learn']

# %% ../nbs/02-nar-training-pipeline.ipynb 4
import os
from xcai.basics import *
from xcai.models.MMM00X import BT0002

# %% ../nbs/02-nar-training-pipeline.ipynb 5
os.environ['WANDB_MODE'] = 'disabled'

# %% ../nbs/02-nar-training-pipeline.ipynb 6
block = XCBlock.from_cfg('data', valid_pct=0.002, tokz='bert-base-uncased')

# %% ../nbs/02-nar-training-pipeline.ipynb 7
args = XCLearningArguments(
    output_dir='/scratch/scai/phd/aiz218323/Projects/xc_nlg/outputs/default',
    per_device_train_batch_size=64,
    per_device_eval_batch_size=64,
    save_strategy="steps",
    evaluation_strategy='steps',
    eval_steps=2000,
    save_steps=2000,
    save_total_limit=5,
    weight_decay=0.01,
    num_train_epochs=3,
    generation_num_beams=10,
    generation_length_penalty=1.5,
    predict_with_generation=True,
    label_names=['lbl2data_idx'],
)

# %% ../nbs/02-nar-training-pipeline.ipynb 8
metric = PrecRecl(block.n_lbl, block.valid.data_lbl_filterer, prop=block.train.dset.data.data_lbl,
                  pk=10, rk=200, rep_pk=[1, 3, 5, 10], rep_rk=[10, 100, 200])

# %% ../nbs/02-nar-training-pipeline.ipynb 9
model = BT0002.from_pretrained('bert-base-uncased', tn_targ=10_000, ig_tok=0)

# %% ../nbs/02-nar-training-pipeline.ipynb 10
trie = XCTrie.from_block(block)

# %% ../nbs/02-nar-training-pipeline.ipynb 11
learn = XCLearner(
    model=model, 
    args=args,
    trie=trie,
    train_dataset=block.train.dset,
    eval_dataset=block.valid.dset,
    data_collator=block.collator,
    compute_metrics=metric,
)

# %% ../nbs/02-nar-training-pipeline.ipynb 12
learn.train()
