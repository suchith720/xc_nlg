# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/19-ngame-training-pipeline-with-multitriplet-loss-with-clustering.ipynb.

# %% auto 0
__all__ = ['block', 'args', 'metric', 'bsz', 'model', 'learn']

# %% ../nbs/19-ngame-training-pipeline-with-multitriplet-loss-with-clustering.ipynb 4
import os,torch, torch.multiprocessing as mp
from xcai.basics import *
from xcai.models.MMM00X import DBT008

# %% ../nbs/19-ngame-training-pipeline-with-multitriplet-loss-with-clustering.ipynb 6
os.environ['CUDA_VISIBLE_DEVICES'] = '2,3'
os.environ['WANDB_PROJECT']='xc-nlg_19-ngame-training-pipeline-with-multitriplet-loss-with-clustering'

# %% ../nbs/19-ngame-training-pipeline-with-multitriplet-loss-with-clustering.ipynb 7
block = XCBlock.from_cfg('/home/aiscuser/scratch/datasets', 'data', valid_pct=0.001, tfm='xc', 
                         tokenizer='distilbert-base-uncased')

# %% ../nbs/19-ngame-training-pipeline-with-multitriplet-loss-with-clustering.ipynb 8
args = XCLearningArguments(
    output_dir='/home/aiscuser/outputs/19-ngame-training-pipeline-with-multitriplet-loss-with-clustering-2-7',
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
    representation_search_type='BRUTEFORCE',
    adam_epsilon=1e-6,
    warmup_steps=100,
    weight_decay=0.1,
    learning_rate=2e-5,
    group_by_cluster=True,
    num_clustering_warmup_epochs=2,
    num_cluster_update_epochs=2,
    num_cluster_size_update_epochs=4,
    clustering_type='EXPO',
    minimum_cluster_size=1,
    maximum_cluster_size=300,
    metric_for_best_model='P@1',
    load_best_model_at_end=True,
    fp16=True,
)

# %% ../nbs/19-ngame-training-pipeline-with-multitriplet-loss-with-clustering.ipynb 9
metric = PrecRecl(block.n_lbl, block.test.data_lbl_filterer, prop=block.train.dset.data.data_lbl,
                  pk=10, rk=200, rep_pk=[1, 3, 5, 10], rep_rk=[10, 100, 200])

# %% ../nbs/19-ngame-training-pipeline-with-multitriplet-loss-with-clustering.ipynb 11
bsz = max(args.per_device_train_batch_size, args.per_device_eval_batch_size)*torch.cuda.device_count()
model = DBT008.from_pretrained('distilbert-base-uncased', bsz=bsz, tn_targ=10_000, 
                               margin=0.3, tau=0.1, n_negatives=5, apply_softmax=True)

# %% ../nbs/19-ngame-training-pipeline-with-multitriplet-loss-with-clustering.ipynb 13
learn = XCLearner(
    model=model, 
    args=args,
    train_dataset=block.train.dset,
    eval_dataset=block.test.dset,
    data_collator=block.collator,
    compute_metrics=metric,
)

# %% ../nbs/19-ngame-training-pipeline-with-multitriplet-loss-with-clustering.ipynb 16
if __name__ == '__main__':
    mp.freeze_support()
    learn.train()
