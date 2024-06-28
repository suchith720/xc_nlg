# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/62-clover-ep-for-wikiseealso-with-clr-for-dr.ipynb.

# %% auto 0
__all__ = ['pkl_dir', 'pkl_file', 'args', 'test_dset', 'metric', 'bsz', 'model', 'learn']

# %% ../nbs/62-clover-ep-for-wikiseealso-with-clr-for-dr.ipynb 3
import os,torch, torch.multiprocessing as mp, pickle
from xcai.basics import *
from xcai.models.PPP0XX import DBT013, DBT014

# %% ../nbs/62-clover-ep-for-wikiseealso-with-clr-for-dr.ipynb 6
os.environ['CUDA_VISIBLE_DEVICES'] = '1'
os.environ['WANDB_PROJECT']='xc-nlg_22-oak-training-pipeline-with-multitriplet-loss-and-clustering'

# %% ../nbs/62-clover-ep-for-wikiseealso-with-clr-for-dr.ipynb 9
pkl_dir = '/home/scai/phd/aiz218323/scratch/datasets'
pkl_file = f'{pkl_dir}/processed/wikiseealso_data_distilbert-base-uncased_xcnlg_ngame.pkl'

# %% ../nbs/62-clover-ep-for-wikiseealso-with-clr-for-dr.ipynb 11
with open(pkl_file, 'rb') as file: block = pickle.load(file)

# %% ../nbs/62-clover-ep-for-wikiseealso-with-clr-for-dr.ipynb 13
args = XCLearningArguments(
    output_dir='/home/scai/phd/aiz218323/scratch/outputs/62-clover-ep-for-wikiseealso-with-clr-for-dr',
    logging_first_step=True,
    per_device_train_batch_size=700,
    per_device_eval_batch_size=700,
    representation_num_beams=200,
    representation_accumulation_steps=100,
    save_strategy="steps",
    evaluation_strategy='steps',
    eval_steps=1000,
    save_steps=1000,
    save_total_limit=5,
    num_train_epochs=300,
    predict_with_representation=True,
    adam_epsilon=1e-6,
    warmup_steps=100,
    weight_decay=0.1,
    learning_rate=2e-4,
    generation_num_beams=10,
    generation_length_penalty=1.5,
    predict_with_generation=True,
    representation_search_type='BRUTEFORCE',
    group_by_cluster=True,
    num_clustering_warmup_epochs=10,
    num_cluster_update_epochs=5,
    num_cluster_size_update_epochs=10,
    clustering_type='EXPO',
    minimum_cluster_size=1,
    maximum_cluster_size=300,
    output_concatenation_weight=1.0,
    metric_for_best_model='P@1',
    load_best_model_at_end=True,
    target_indices_key='plbl2data_idx',
    target_pointer_key='plbl2data_data2ptr',
    fp16=True,
)

# %% ../nbs/62-clover-ep-for-wikiseealso-with-clr-for-dr.ipynb 15
test_dset = block.test.dset.sample(n=2000, seed=50)
metric = PrecRecl(block.n_lbl, test_dset.data.data_lbl_filterer, prop=block.train.dset.data.data_lbl,
                  pk=10, rk=200, rep_pk=[1, 3, 5, 10], rep_rk=[10, 100, 200])

# %% ../nbs/62-clover-ep-for-wikiseealso-with-clr-for-dr.ipynb 16
bsz = max(args.per_device_train_batch_size, args.per_device_eval_batch_size)*torch.cuda.device_count()

model = DBT014.from_pretrained('distilbert-base-uncased', ig_tok=0, bsz=bsz, tn_targ=1000, margin=0.3, 
                               tau=0.1, n_negatives=10, apply_softmax=True, lw=1, tie_word_embeddings=False)
model.init_dr_head()
model.use_generation = False

# %% ../nbs/62-clover-ep-for-wikiseealso-with-clr-for-dr.ipynb 19
learn = XCLearner(
    model=model, 
    args=args,
    train_dataset=block.train.dset,
    eval_dataset=test_dset,
    data_collator=block.collator,
    compute_metrics=metric,
)

# %% ../nbs/62-clover-ep-for-wikiseealso-with-clr-for-dr.ipynb 23
if __name__ == '__main__':
    mp.freeze_support()
    learn.train()
