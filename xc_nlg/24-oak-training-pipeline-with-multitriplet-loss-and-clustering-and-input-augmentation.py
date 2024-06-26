# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/24-oak-training-pipeline-with-multitriplet-loss-and-clustering-and-input-augmentation.ipynb.

# %% auto 0
__all__ = ['block', 'args', 'test_dset', 'metric', 'bsz', 'model', 'tbs', 'learn']

# %% ../nbs/24-oak-training-pipeline-with-multitriplet-loss-and-clustering-and-input-augmentation.ipynb 4
import os,torch, torch.multiprocessing as mp
from xcai.basics import *
from xcai.models.MMM00X import DBT013
from xcai.transform import AugmentMetaInputIdsTfm
from xcai.generation.generate import XCTrieBeamSearch

# %% ../nbs/24-oak-training-pipeline-with-multitriplet-loss-and-clustering-and-input-augmentation.ipynb 6
os.environ['WANDB_PROJECT']='xc-nlg_24-oak-training-pipeline-with-multitriplet-loss-and-clustering-and-input-augmentation'

# %% ../nbs/24-oak-training-pipeline-with-multitriplet-loss-and-clustering-and-input-augmentation.ipynb 7
block = XCBlock.from_cfg('/home/aiscuser/scratch/datasets', 'data_meta', valid_pct=0.001, tfm='xc', 
                         tokenizer='distilbert-base-uncased')

# %% ../nbs/24-oak-training-pipeline-with-multitriplet-loss-and-clustering-and-input-augmentation.ipynb 8
block = AugmentMetaInputIdsTfm.apply(block, 'hlk_meta', 32, True)

# %% ../nbs/24-oak-training-pipeline-with-multitriplet-loss-and-clustering-and-input-augmentation.ipynb 9
block.train.dset.data.data_info['input_ids'] = block.train.dset.data.data_info['input_ids_aug_hlk']
block.train.dset.data.data_info['attention_mask'] = block.train.dset.data.data_info['attention_mask_aug_hlk']

# %% ../nbs/24-oak-training-pipeline-with-multitriplet-loss-and-clustering-and-input-augmentation.ipynb 10
args = XCLearningArguments(
    output_dir='/home/aiscuser/outputs/24-oak-training-pipeline-with-multitriplet-loss-and-clustering-and-input-augmentation',
    logging_first_step=True,
    per_device_train_batch_size=800,
    per_device_eval_batch_size=800,
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
    generation_num_beams=10,
    generation_length_penalty=0.0,
    predict_with_generation=True,
    label_names=['lbl2data_idx'],
    representation_search_type='BRUTEFORCE',
    group_by_cluster=True,
    num_clustering_warmup_epochs=10,
    num_cluster_update_epochs=5,
    clustering_type='EXPO',
    minimum_cluster_size=1,
)

# %% ../nbs/24-oak-training-pipeline-with-multitriplet-loss-and-clustering-and-input-augmentation.ipynb 11
test_dset = block.test.dset.sample(n=100, seed=50)

metric = PrecRecl(block.n_lbl, test_dset.data.data_lbl_filterer, prop=block.train.dset.data.data_lbl,
                  pk=10, rk=200, rep_pk=[1, 3, 5, 10], rep_rk=[10, 100, 200])

# %% ../nbs/24-oak-training-pipeline-with-multitriplet-loss-and-clustering-and-input-augmentation.ipynb 12
bsz = max(args.per_device_train_batch_size, args.per_device_eval_batch_size)*torch.cuda.device_count()

model = DBT013.from_pretrained('distilbert-base-uncased', ig_tok=0, bsz=bsz, tn_targ=10_000, margin=0.3, tau=0.1, 
                               n_negatives=50, apply_softmax=True, lw=4)

# %% ../nbs/24-oak-training-pipeline-with-multitriplet-loss-and-clustering-and-input-augmentation.ipynb 13
tbs = XCTrieBeamSearch.from_block(block, max_height=32, sos_id=101, eos_id=102, pad_token=0, 
                                  n_bm=10, len_penalty=0.0)

# %% ../nbs/24-oak-training-pipeline-with-multitriplet-loss-and-clustering-and-input-augmentation.ipynb 14
learn = XCLearner(
    model=model, 
    args=args,
    trie_generator=tbs,
    train_dataset=block.train.dset,
    eval_dataset=test_dset,
    data_collator=block.collator,
    compute_metrics=metric,
)

# %% ../nbs/24-oak-training-pipeline-with-multitriplet-loss-and-clustering-and-input-augmentation.ipynb 15
if __name__ == '__main__':
    mp.freeze_support()
    learn.train()
