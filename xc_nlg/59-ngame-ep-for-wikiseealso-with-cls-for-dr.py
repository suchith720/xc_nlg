# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/59-ngame-ep-for-wikiseealso-with-cls-for-dr.ipynb.

# %% auto 0
__all__ = ['data_dir', 'pkl_dir', 'pkl_file', 'args', 'metric', 'bsz', 'model', 'learn']

# %% ../nbs/59-ngame-ep-for-wikiseealso-with-cls-for-dr.ipynb 2
import os,torch, torch.multiprocessing as mp, pickle
from xcai.basics import *
from xcai.models.PPP0XX import DBT011

# %% ../nbs/59-ngame-ep-for-wikiseealso-with-cls-for-dr.ipynb 4
os.environ['CUDA_VISIBLE_DEVICES'] = '0,1'
os.environ['WANDB_PROJECT']='xc-nlg_19-ngame-training-pipeline-with-multitriplet-loss-with-clustering'

# %% ../nbs/59-ngame-ep-for-wikiseealso-with-cls-for-dr.ipynb 5
data_dir = '/home/scai/phd/aiz218323/Projects/XC_NLG/data'

# %% ../nbs/59-ngame-ep-for-wikiseealso-with-cls-for-dr.ipynb 8
pkl_dir = '/home/scai/phd/aiz218323/scratch/datasets'
pkl_file = f'{pkl_dir}/processed/wikiseealso_data_distilbert-base-uncased_xcnlg_ngame.pkl'

# %% ../nbs/59-ngame-ep-for-wikiseealso-with-cls-for-dr.ipynb 10
with open(pkl_file, 'rb') as file: block = pickle.load(file)

# %% ../nbs/59-ngame-ep-for-wikiseealso-with-cls-for-dr.ipynb 12
args = XCLearningArguments(
    output_dir='/home/scai/phd/aiz218323/scratch/outputs/59-ngame-ep-for-wikiseealso-with-cls-for-dr',
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
    num_cluster_size_update_epochs=10,
    clustering_type='EXPO',
    minimum_cluster_size=1,
    maximum_cluster_size=300,
    target_indices_key='plbl2data_idx',
    target_pointer_key='plbl2data_data2ptr',
    use_encoder_parallel=True,
    max_grad_norm=None,
    fp16=True,
)

# %% ../nbs/59-ngame-ep-for-wikiseealso-with-cls-for-dr.ipynb 14
metric = PrecRecl(block.n_lbl, block.test.data_lbl_filterer, prop=block.train.dset.data.data_lbl,
                  pk=10, rk=200, rep_pk=[1, 3, 5, 10], rep_rk=[10, 100, 200])

# %% ../nbs/59-ngame-ep-for-wikiseealso-with-cls-for-dr.ipynb 15
bsz = max(args.per_device_train_batch_size, args.per_device_eval_batch_size)*torch.cuda.device_count()

model = DBT010.from_pretrained('distilbert-base-uncased', bsz=bsz, tn_targ=5000, margin=0.3, tau=0.1, 
                               n_negatives=5, apply_softmax=True, use_encoder_parallel=True)
model.init_dr_head()

# %% ../nbs/59-ngame-ep-for-wikiseealso-with-cls-for-dr.ipynb 16
learn = XCLearner(
    model=model, 
    args=args,
    train_dataset=block.train.dset,
    eval_dataset=block.test.dset,
    data_collator=block.collator,
    compute_metrics=metric,
)

# %% ../nbs/59-ngame-ep-for-wikiseealso-with-cls-for-dr.ipynb 19
if __name__ == '__main__':
    mp.freeze_support()
    learn.train()
