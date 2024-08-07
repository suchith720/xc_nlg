# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/79-ngame-ep-for-wikiseealso-hyperlink-linker.ipynb.

# %% auto 0
__all__ = ['data_dir', 'pkl_dir', 'pkl_file', 'idx', 'train_dset', 'test_dset', 'args', 'metric', 'bsz', 'model', 'learn']

# %% ../nbs/79-ngame-ep-for-wikiseealso-hyperlink-linker.ipynb 2
import os,torch, torch.multiprocessing as mp, pickle
from xcai.basics import *
from xcai.models.PPP0XX import DBT009,DBT011

# %% ../nbs/79-ngame-ep-for-wikiseealso-hyperlink-linker.ipynb 4
os.environ['CUDA_VISIBLE_DEVICES'] = '0,1'
os.environ['WANDB_PROJECT']='c-nlg_66-radga-dr-ep-for-wikiseealso'

# %% ../nbs/79-ngame-ep-for-wikiseealso-hyperlink-linker.ipynb 5
data_dir = '/home/scai/phd/aiz218323/Projects/XC_NLG/data'

# %% ../nbs/79-ngame-ep-for-wikiseealso-hyperlink-linker.ipynb 8
pkl_dir = '/home/scai/phd/aiz218323/scratch/datasets'
pkl_file = f'{pkl_dir}/processed/wikiseealso_data-metas_distilbert-base-uncased_rm_ngame.pkl'

# %% ../nbs/79-ngame-ep-for-wikiseealso-hyperlink-linker.ipynb 10
with open(pkl_file, 'rb') as file: block = pickle.load(file)

# %% ../nbs/79-ngame-ep-for-wikiseealso-hyperlink-linker.ipynb 11
import numpy as np
from xcai.data import MainXCDataset, XCDataset

# %% ../nbs/79-ngame-ep-for-wikiseealso-hyperlink-linker.ipynb 12
idx = np.where(block.train.dset.meta['hlk_meta'].data_meta.getnnz(axis=1) > 0)[0]
train_dset = block.train.dset._getitems(idx)

idx = np.where(block.test.dset.meta['hlk_meta'].data_meta.getnnz(axis=1) > 0)[0]
test_dset = block.test.dset._getitems(idx)

# %% ../nbs/79-ngame-ep-for-wikiseealso-hyperlink-linker.ipynb 13
train_dset = XCDataset(MainXCDataset(train_dset.data.data_info, train_dset.meta['hlk_meta'].data_meta, 
                                     train_dset.meta['hlk_meta'].meta_info))

test_dset = XCDataset(MainXCDataset(test_dset.data.data_info, test_dset.meta['hlk_meta'].data_meta, 
                                    test_dset.meta['hlk_meta'].meta_info))

# %% ../nbs/79-ngame-ep-for-wikiseealso-hyperlink-linker.ipynb 15
args = XCLearningArguments(
    output_dir='/home/scai/phd/aiz218323/scratch/outputs/79-ngame-ep-for-wikiseealso-hyperlink-linker-1-0',
    logging_first_step=True,
    per_device_train_batch_size=800,
    per_device_eval_batch_size=800,
    representation_num_beams=200,
    representation_accumulation_steps=10,
    save_strategy="steps",
    evaluation_strategy="steps",
    eval_steps=1000,
    save_steps=1000,
    save_total_limit=5,
    num_train_epochs=300,
    predict_with_representation=True,
    representation_search_type='BRUTEFORCE',
    adam_epsilon=1e-6,
    warmup_steps=100,
    weight_decay=0.01,
    learning_rate=2e-4,
    group_by_cluster=True,
    num_clustering_warmup_epochs=10,
    num_cluster_update_epochs=5,
    num_cluster_size_update_epochs=25,
    clustering_type='EXPO',
    minimum_cluster_size=1,
    maximum_cluster_size=1600,
    metric_for_best_model='P@1',
    load_best_model_at_end=True,
    target_indices_key='plbl2data_idx',
    target_pointer_key='plbl2data_data2ptr',
    use_encoder_parallel=True,
    max_grad_norm=None,
    fp16=True,
)

# %% ../nbs/79-ngame-ep-for-wikiseealso-hyperlink-linker.ipynb 17
metric = PrecRecl(test_dset.n_lbl, test_dset.data.data_lbl_filterer, prop=train_dset.data.data_lbl,
                  pk=10, rk=200, rep_pk=[1, 3, 5, 10], rep_rk=[10, 100, 200])

# %% ../nbs/79-ngame-ep-for-wikiseealso-hyperlink-linker.ipynb 18
bsz = max(args.per_device_train_batch_size, args.per_device_eval_batch_size)*torch.cuda.device_count()

model = DBT010.from_pretrained('sentence-transformers/msmarco-distilbert-base-v4', bsz=bsz, tn_targ=5000, margin=0.3, tau=0.1, 
                               n_negatives=10, apply_softmax=True, use_encoder_parallel=True)
model.init_dr_head()

# %% ../nbs/79-ngame-ep-for-wikiseealso-hyperlink-linker.ipynb 19
learn = XCLearner(
    model=model, 
    args=args,
    train_dataset=train_dset,
    eval_dataset=test_dset,
    data_collator=block.collator,
    compute_metrics=metric,
)

# %% ../nbs/79-ngame-ep-for-wikiseealso-hyperlink-linker.ipynb 22
if __name__ == '__main__':
    mp.freeze_support()
    learn.train()
