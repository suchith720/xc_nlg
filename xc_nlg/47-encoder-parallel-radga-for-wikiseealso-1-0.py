# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/48-encoder-parallel-radga-with-cross-attention-loss-component-for-wikiseealso.ipynb.

# %% auto 0
__all__ = ['data_dir', 'pkl_dir', 'args', 'test_dset', 'metric', 'bsz', 'model', 'trie', 'learn']

# %% ../nbs/48-encoder-parallel-radga-with-cross-attention-loss-component-for-wikiseealso.ipynb 3
import os,sys,torch,pickle,torch.multiprocessing as mp, pickle
from xcai.basics import *
from xcai.models.PPP0XX import DBT020

# %% ../nbs/48-encoder-parallel-radga-with-cross-attention-loss-component-for-wikiseealso.ipynb 5
os.environ['CUDA_VISIBLE_DEVICES'] = '4,5,6,7'
os.environ['WANDB_PROJECT']='xc-nlg_38-radga-training-pipeline'

# %% ../nbs/48-encoder-parallel-radga-with-cross-attention-loss-component-for-wikiseealso.ipynb 7
data_dir = '/home/aiscuser/scratch/datasets'

# %% ../nbs/48-encoder-parallel-radga-with-cross-attention-loss-component-for-wikiseealso.ipynb 10
pkl_dir = f'{data_dir}/processed/'

# %% ../nbs/48-encoder-parallel-radga-with-cross-attention-loss-component-for-wikiseealso.ipynb 12
with open(f'{pkl_dir}/wikiseealso_data-metas_distilbert-base-uncased_rm_radga-encoder-parallel.pkl', 'rb') as file: 
    block = pickle.load(file)

# %% ../nbs/48-encoder-parallel-radga-with-cross-attention-loss-component-for-wikiseealso.ipynb 14
args = XCLearningArguments(
    output_dir='/home/aiscuser/outputs/47-encoder-parallel-radga-for-wikiseealso-1-0',
    logging_first_step=True,
    per_device_train_batch_size=600,
    per_device_eval_batch_size=100,
    representation_num_beams=200,
    representation_accumulation_steps=1,
    save_strategy="steps",
    evaluation_strategy='steps',
    eval_steps=1000,
    save_steps=1000,
    save_total_limit=5,
    num_train_epochs=300,
    predict_with_representation=True,
    adam_epsilon=1e-6,
    warmup_steps=100,
    weight_decay=0.01,
    learning_rate=2e-4,
    generation_num_beams=10,
    generation_length_penalty=1.5,
    predict_with_generation=True,
    representation_search_type='INDEX',
    group_by_cluster=True,
    num_clustering_warmup_epochs=10,
    num_cluster_update_epochs=5,
    num_cluster_size_update_epochs=10,
    clustering_type='EXPO',
    minimum_cluster_size=1,
    maximum_cluster_size=300,
    output_concatenation_weight=1.0,
    metric_for_best_model='P@1_REPR',
    target_indices_key='plbl2data_idx',
    target_pointer_key='plbl2data_data2ptr',
    fp16=True,
    label_names=['cat2data_idx', 'cat2data_input_ids', 'cat2data_attention_mask',
                 'cat2lbl2data_idx', 'cat2lbl2data_input_ids', 'cat2lbl2data_attention_mask',
                 'hlk2data_input_ids', 'hlk2data_attention_mask', 'hlk2data_idx',
                 'hlk2lbl2data_input_ids', 'hlk2lbl2data_attention_mask', 'hlk2lbl2data_idx'
                ],
)

# %% ../nbs/48-encoder-parallel-radga-with-cross-attention-loss-component-for-wikiseealso.ipynb 15
test_dset = block.test.dset.sample(n=2000, seed=50)
metric = PrecRecl(block.n_lbl, test_dset.data.data_lbl_filterer, prop=block.train.dset.data.data_lbl,
                  pk=10, rk=200, rep_pk=[1, 3, 5, 10], rep_rk=[10, 100, 200])

# %% ../nbs/48-encoder-parallel-radga-with-cross-attention-loss-component-for-wikiseealso.ipynb 16
bsz = max(args.per_device_train_batch_size, args.per_device_eval_batch_size)*torch.cuda.device_count()

model = DBT020.from_pretrained('distilbert-base-uncased', ig_tok=0, bsz=bsz, tn_targ=5000, tn_meta=5000, 
                               margin=0.3, tau=0.1, n_negatives=5, apply_softmax=True, lw=0.01, m_lw=0.3, 
                               pred_meta_prefix='cat', data_aug_meta_prefix='hlk2data', 
                               lbl2data_aug_meta_prefix='hlk2lbl', tie_word_embeddings=False)

model.init_dr_head()

# %% ../nbs/48-encoder-parallel-radga-with-cross-attention-loss-component-for-wikiseealso.ipynb 18
trie = XCTrie.from_block(block)

# %% ../nbs/48-encoder-parallel-radga-with-cross-attention-loss-component-for-wikiseealso.ipynb 19
learn = XCLearner(
    model=model, 
    args=args,
    trie=trie,
    train_dataset=block.train.dset,
    eval_dataset=test_dset,
    data_collator=block.collator,
    compute_metrics=metric,
)

# %% ../nbs/48-encoder-parallel-radga-with-cross-attention-loss-component-for-wikiseealso.ipynb 23
if __name__ == '__main__':
    mp.freeze_support()
    learn.train(resume_from_checkpoint=True)
    
