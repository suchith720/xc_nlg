# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/40-clover-with-input-metadata-fusion-training-pipeline.ipynb.

# %% auto 0
__all__ = ['block', 'args', 'test_dset', 'metric', 'bsz', 'model', 'trie', 'learn']

# %% ../nbs/40-clover-with-input-metadata-fusion-training-pipeline.ipynb 4
import os,sys,torch,pickle,torch.multiprocessing as mp
from xcai.basics import *

# %% ../nbs/40-clover-with-input-metadata-fusion-training-pipeline.ipynb 6
os.environ['CUDA_VISIBLE_DEVICES'] = '14,15'
os.environ['WANDB_PROJECT']='xc-nlg_40-clover-with-input-metadata-fusion-training-pipeline'

sys.path.append('/home/aiscuser/scratch/Projects/xc_nlg')

# %% ../nbs/40-clover-with-input-metadata-fusion-training-pipeline.ipynb 7
from .models.radga import *

# %% ../nbs/40-clover-with-input-metadata-fusion-training-pipeline.ipynb 9
block = XCBlock.from_cfg('/home/aiscuser/scratch/datasets', 'data_meta', valid_pct=0.001, 
                         tfm='xcnlg', tokenizer='distilbert-base-uncased', 
                         smp_features=[('lbl2data',1,2), ('hlk2data',1,4)], n_data_meta_samples=50)

# %% ../nbs/40-clover-with-input-metadata-fusion-training-pipeline.ipynb 13
args = XCLearningArguments(
    output_dir='/home/aiscuser/outputs/40-clover-with-input-metadata-fusion-training-pipeline-2-0',
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
    adam_epsilon=1e-6,
    warmup_steps=100,
    weight_decay=0.1,
    learning_rate=2e-4,
    generation_num_beams=10,
    generation_length_penalty=1.5,
    predict_with_generation=True,
    representation_search_type='BRUTEFORCE',
    group_by_cluster=True,
    num_clustering_warmup_epochs=1,
    num_cluster_update_epochs=2,
    num_cluster_size_update_epochs=4,
    clustering_type='EXPO',
    minimum_cluster_size=1,
    maximum_cluster_size=300,
    output_concatenation_weight=1.0,
    metric_for_best_model='P@1_REPR',
    target_indices_key='plbl2data_idx',
    target_pointer_key='plbl2data_data2ptr',
    fp16=True,
    label_names=['hlk2data_input_ids', 'hlk2data_attention_mask', 'hlk2data_data2ptr', 'hlk2data_idx'],
)

# %% ../nbs/40-clover-with-input-metadata-fusion-training-pipeline.ipynb 14
test_dset = block.test.dset.sample(n=2000, seed=50)
metric = PrecRecl(block.n_lbl, test_dset.data.data_lbl_filterer, prop=block.train.dset.data.data_lbl,
                  pk=10, rk=200, rep_pk=[1, 3, 5, 10], rep_rk=[10, 100, 200])

# %% ../nbs/40-clover-with-input-metadata-fusion-training-pipeline.ipynb 15
bsz = max(args.per_device_train_batch_size, args.per_device_eval_batch_size)*torch.cuda.device_count()

model = DBT018.from_pretrained('distilbert-base-uncased', ig_tok=0, bsz=bsz, tn_targ=10_000, tn_meta=10_000, 
                               margin=0.3, tau=0.1, n_negatives=5, apply_softmax=True, lw=0.01,
                               aug_meta_prefix='hlk', init_drh=True)

# %% ../nbs/40-clover-with-input-metadata-fusion-training-pipeline.ipynb 16
trie = XCTrie.from_block(block)

# %% ../nbs/40-clover-with-input-metadata-fusion-training-pipeline.ipynb 17
learn = XCLearner(
    model=model, 
    args=args,
    trie=trie,
    train_dataset=block.train.dset,
    eval_dataset=test_dset,
    data_collator=block.collator,
    compute_metrics=metric,
)

# %% ../nbs/40-clover-with-input-metadata-fusion-training-pipeline.ipynb 18
if __name__ == '__main__':
    mp.freeze_support()
    learn.train()
