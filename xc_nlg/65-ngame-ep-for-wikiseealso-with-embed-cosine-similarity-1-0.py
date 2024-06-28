# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/65-ngame-ep-for-wikiseealso-with-embed-cosine-similarity.ipynb.

# %% auto 0
__all__ = ['data_dir', 'pkl_dir', 'pkl_file', 'args', 'metric', 'bsz', 'model', 'learn']

# %% ../nbs/65-ngame-ep-for-wikiseealso-with-embed-cosine-similarity.ipynb 2
import os,torch, torch.multiprocessing as mp, pickle
from xcai.basics import *
from xcai.models.PPP0XX import DBT022

# %% ../nbs/65-ngame-ep-for-wikiseealso-with-embed-cosine-similarity.ipynb 4
os.environ['CUDA_VISIBLE_DEVICES'] = '0,1'
os.environ['WANDB_PROJECT']='xc-nlg_19-ngame-training-pipeline-with-multitriplet-loss-with-clustering'

# %% ../nbs/65-ngame-ep-for-wikiseealso-with-embed-cosine-similarity.ipynb 5
data_dir = '/home/scai/phd/aiz218323/Projects/XC_NLG/data'

# %% ../nbs/65-ngame-ep-for-wikiseealso-with-embed-cosine-similarity.ipynb 7
pkl_dir = '/home/scai/phd/aiz218323/scratch/datasets'
pkl_file = f'{pkl_dir}/processed/wikiseealso_data_distilbert-base-uncased_xcnlg_ngame.pkl'

# %% ../nbs/65-ngame-ep-for-wikiseealso-with-embed-cosine-similarity.ipynb 9
with open(pkl_file, 'rb') as file: block = pickle.load(file)

# %% ../nbs/65-ngame-ep-for-wikiseealso-with-embed-cosine-similarity.ipynb 12
args = XCLearningArguments(
    output_dir='/home/scai/phd/aiz218323/scratch/outputs/65-ngame-ep-for-wikiseealso-with-embed-cosine-similarity-1-0',
    logging_first_step=True,
    per_device_train_batch_size=800,
    per_device_eval_batch_size=800,
    representation_num_beams=200,
    representation_accumulation_steps=10,
    save_strategy="steps",
    evaluation_strategy="steps",
    eval_steps=2000,
    save_steps=2000,
    save_total_limit=5,
    num_train_epochs=300,
    predict_with_representation=True,
    representation_search_type='INDEX',
    adam_epsilon=1e-6,
    warmup_steps=100,
    weight_decay=0.0,
    learning_rate=2e-4,
    group_by_cluster=True,
    num_clustering_warmup_epochs=10,
    num_cluster_update_epochs=5,
    num_cluster_size_update_epochs=25,
    clustering_type='EXPO',
    minimum_cluster_size=2,
    maximum_cluster_size=1600,
    target_indices_key='plbl2data_idx',
    target_pointer_key='plbl2data_data2ptr',
    use_encoder_parallel=True,
    max_grad_norm=None,
    fp16=True,
)

# %% ../nbs/65-ngame-ep-for-wikiseealso-with-embed-cosine-similarity.ipynb 13
metric = PrecRecl(block.n_lbl, block.test.data_lbl_filterer, prop=block.train.dset.data.data_lbl,
                  pk=10, rk=200, rep_pk=[1, 3, 5, 10], rep_rk=[10, 100, 200])

# %% ../nbs/65-ngame-ep-for-wikiseealso-with-embed-cosine-similarity.ipynb 14
bsz = max(args.per_device_train_batch_size, args.per_device_eval_batch_size)*torch.cuda.device_count()

model = DBT022.from_pretrained('sentence-transformers/msmarco-distilbert-base-v4', bsz=bsz, tn_targ=5000, c_lw=0.01, margin=0.3, tau=0.1,
                               n_negatives=10, apply_softmax=True, use_encoder_parallel=True)
model.init_dr_head()

# %% ../nbs/65-ngame-ep-for-wikiseealso-with-embed-cosine-similarity.ipynb 15
learn = XCLearner(
    model=model,
    args=args,
    train_dataset=block.train.dset,
    eval_dataset=block.test.dset,
    data_collator=block.collator,
    compute_metrics=metric,
)

# %% ../nbs/65-ngame-ep-for-wikiseealso-with-embed-cosine-similarity.ipynb 18
if __name__ == '__main__':
    mp.freeze_support()
    learn.train()
