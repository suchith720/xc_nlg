# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/18-ngame-training-pipeline-with-soupcon-loss.ipynb.

# %% auto 0
__all__ = ['block', 'args', 'metric', 'model', 'learn']

# %% ../nbs/18-ngame-training-pipeline-with-soupcon-loss.ipynb 4
import os,torch
from xcai.basics import *
from xcai.models.MMM00X import DBT010

# %% ../nbs/18-ngame-training-pipeline-with-soupcon-loss.ipynb 6
os.environ['WANDB_PROJECT']='xc-nlg_18-ngame-training-pipeline-with-soupcon-loss'

# %% ../nbs/18-ngame-training-pipeline-with-soupcon-loss.ipynb 7
block = XCBlock.from_cfg('/home/aiscuser/scratch/datasets', 'data', valid_pct=0.001, tfm='xc', 
                         tokenizer='sentence-transformers/msmarco-distilbert-base-v4')

# %% ../nbs/18-ngame-training-pipeline-with-soupcon-loss.ipynb 8
args = XCLearningArguments(
    output_dir='/home/aiscuser/outputs/18-ngame-training-pipeline-with-soupcon-loss',
    logging_first_step=True,
    per_device_train_batch_size=1024,
    per_device_eval_batch_size=64,
    representation_num_beams=200,
    representation_accumulation_steps=100,
    save_strategy="steps",
    evaluation_strategy='steps',
    eval_steps=1000,
    save_steps=1000,
    save_total_limit=5,
    num_train_epochs=50,
    predict_with_representation=True,
    adam_epsilon=1e-6,
    warmup_steps=100,
    weight_decay=0.01,
    learning_rate=2e-4,
)

# %% ../nbs/18-ngame-training-pipeline-with-soupcon-loss.ipynb 9
metric = PrecRecl(block.n_lbl, block.test.data_lbl_filterer, prop=block.train.dset.data.data_lbl,
                  pk=10, rk=200, rep_pk=[1, 3, 5, 10], rep_rk=[10, 100, 200])

# %% ../nbs/18-ngame-training-pipeline-with-soupcon-loss.ipynb 11
model = DBT010.from_pretrained('sentence-transformers/msmarco-distilbert-base-v4', tau=1.0)

# %% ../nbs/18-ngame-training-pipeline-with-soupcon-loss.ipynb 12
learn = XCLearner(
    model=model, 
    args=args,
    train_dataset=block.train.dset,
    eval_dataset=block.test.dset,
    data_collator=block.collator,
    compute_metrics=metric,
)

# %% ../nbs/18-ngame-training-pipeline-with-soupcon-loss.ipynb 14
learn.train()
