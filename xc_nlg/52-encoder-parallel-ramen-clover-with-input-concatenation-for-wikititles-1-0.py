# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/52-encoder-parallel-ramen-clover-with-input-concatenation-for-wikititles.ipynb.

# %% auto 0
__all__ = ['data_dir', 'pkl_dir', 'block', 'args', 'test_dset', 'metric', 'bsz', 'model', 'trie', 'learn']

# %% ../nbs/52-encoder-parallel-ramen-clover-with-input-concatenation-for-wikititles.ipynb 3
import os,torch, torch.multiprocessing as mp, pickle
from xcai.basics import *
from xcai.models.PPP0XX import DBT017

# %% ../nbs/52-encoder-parallel-ramen-clover-with-input-concatenation-for-wikititles.ipynb 5
os.environ['CUDA_VISIBLE_DEVICES'] = '6,7'
os.environ['WANDB_PROJECT']='xc-nlg_52-encoder-parallel-ramen-clover-with-input-concatenation-for-wikititles'

# %% ../nbs/52-encoder-parallel-ramen-clover-with-input-concatenation-for-wikititles.ipynb 6
data_dir = '/home/aiscuser/scratch/datasets'

# %% ../nbs/52-encoder-parallel-ramen-clover-with-input-concatenation-for-wikititles.ipynb 8
pkl_dir = f'{data_dir}/processed/'

# %% ../nbs/52-encoder-parallel-ramen-clover-with-input-concatenation-for-wikititles.ipynb 10
with open(f'{pkl_dir}/wikititles_data-metas_distilbert-base-uncased_rm_ramen-sal-encoder-parallel.pkl', 'rb') as file: 
    block = pickle.load(file)

# %% ../nbs/52-encoder-parallel-ramen-clover-with-input-concatenation-for-wikititles.ipynb 11
block = AugmentMetaInputIdsTfm.apply(block, 'hlk_meta', 32, True)

block.train.dset.data.data_info['input_ids'] = block.train.dset.data.data_info['input_ids_aug_hlk']
block.train.dset.data.data_info['attention_mask'] = block.train.dset.data.data_info['attention_mask_aug_hlk']

block.test.dset.data.data_info['input_ids'] = block.test.dset.data.data_info['input_ids_aug_hlk']
block.test.dset.data.data_info['attention_mask'] = block.test.dset.data.data_info['attention_mask_aug_hlk']

# %% ../nbs/52-encoder-parallel-ramen-clover-with-input-concatenation-for-wikititles.ipynb 12
args = XCLearningArguments(
    output_dir='/home/aiscuser/outputs/52-encoder-parallel-ramen-clover-with-input-concatenation-for-wikititles-1-0',
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
    metric_for_best_model='P@1',
    load_best_model_at_end=True,
    target_indices_key='plbl2data_idx',
    target_pointer_key='plbl2data_data2ptr',
    fp16=True,
    label_names=['sal2data_idx', 'sal2data_input_ids', 'sal2data_attention_mask',
                 'sal2lbl2data_idx', 'sal2lbl2data_input_ids', 'sal2lbl2data_attention_mask'],
)

# %% ../nbs/52-encoder-parallel-ramen-clover-with-input-concatenation-for-wikititles.ipynb 13
test_dset = block.test.dset.sample(n=2000, seed=50)
metric = PrecRecl(block.n_lbl, test_dset.data.data_lbl_filterer, prop=block.train.dset.data.data_lbl,
                  pk=10, rk=200, rep_pk=[1, 3, 5, 10], rep_rk=[10, 100, 200])

# %% ../nbs/52-encoder-parallel-ramen-clover-with-input-concatenation-for-wikititles.ipynb 14
bsz = max(args.per_device_train_batch_size, args.per_device_eval_batch_size)*torch.cuda.device_count()

model = DBT017.from_pretrained('distilbert-base-uncased', ig_tok=0, bsz=bsz, tn_targ=5000, margin=0.3, tau=0.1, 
                               n_negatives=5, apply_softmax=True, lw=0.001, m_lw=0.3, meta_prefix='sal', 
                               tie_word_embeddings=False)
model.init_dr_head()

# %% ../nbs/52-encoder-parallel-ramen-clover-with-input-concatenation-for-wikititles.ipynb 15
trie = XCTrie.from_block(block)

# %% ../nbs/52-encoder-parallel-ramen-clover-with-input-concatenation-for-wikititles.ipynb 16
learn = XCLearner(
    model=model, 
    args=args,
    trie=trie,
    train_dataset=block.train.dset,
    eval_dataset=test_dset,
    data_collator=block.collator,
    compute_metrics=metric,
)

# %% ../nbs/52-encoder-parallel-ramen-clover-with-input-concatenation-for-wikititles.ipynb 20
if __name__ == '__main__':
    mp.freeze_support()
    learn.train()
