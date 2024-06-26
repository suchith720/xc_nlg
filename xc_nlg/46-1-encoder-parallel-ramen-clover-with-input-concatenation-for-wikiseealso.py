# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/46-1-encoder-parallel-ramen-clover-with-input-concatenation-for-wikiseealso.ipynb.

# %% auto 0
__all__ = ['data_dir', 'pkl_dir', 'pkl_file', 'block', 'args', 'output_dir', 'mname', 'bsz', 'model', 'trie', 'train_dset',
           'metric', 'learn', 'pred_dir', 'test_dset']

# %% ../nbs/46-1-encoder-parallel-ramen-clover-with-input-concatenation-for-wikiseealso.ipynb 3
import os,torch, torch.multiprocessing as mp, pickle
from scipy import sparse
from xcai.basics import *
from xcai.models.PPP0XX import DBT017

# %% ../nbs/46-1-encoder-parallel-ramen-clover-with-input-concatenation-for-wikiseealso.ipynb 5
os.environ['WANDB_MODE'] = 'disabled'

# %% ../nbs/46-1-encoder-parallel-ramen-clover-with-input-concatenation-for-wikiseealso.ipynb 6
os.environ['CUDA_VISIBLE_DEVICES'] = '0,1'
os.environ['WANDB_PROJECT']='xc-nlg_25-ramen-style-clover-training-with-input-augmentation'

# %% ../nbs/46-1-encoder-parallel-ramen-clover-with-input-concatenation-for-wikiseealso.ipynb 8
data_dir = '/home/aiscuser/scratch/datasets'

pkl_dir = f'{data_dir}/processed/'
pkl_file = f'{pkl_dir}/wikiseealso_data-metas_distilbert-base-uncased_rm_ramen-cat-encoder-parallel.pkl'

with open(pkl_file, 'rb') as file: block = pickle.load(file)

# %% ../nbs/46-1-encoder-parallel-ramen-clover-with-input-concatenation-for-wikiseealso.ipynb 9
block = AugmentMetaInputIdsTfm.apply(block, 'hlk_meta', 32, True)

block.train.dset.data.data_info['input_ids'] = block.train.dset.data.data_info['input_ids_aug_hlk']
block.train.dset.data.data_info['attention_mask'] = block.train.dset.data.data_info['attention_mask_aug_hlk']

block.test.dset.data.data_info['input_ids'] = block.test.dset.data.data_info['input_ids_aug_hlk']
block.test.dset.data.data_info['attention_mask'] = block.test.dset.data.data_info['attention_mask_aug_hlk']

# %% ../nbs/46-1-encoder-parallel-ramen-clover-with-input-concatenation-for-wikiseealso.ipynb 10
args = XCLearningArguments(
    output_dir='/home/aiscuser/outputs/46-encoder-parallel-ramen-clover-with-input-concatenation-for-wikiseealso-1-0',
    logging_first_step=True,
    per_device_train_batch_size=800,
    per_device_eval_batch_size=800,
    representation_num_beams=200,
    representation_accumulation_steps=100,
    predict_with_representation=True,
    generation_num_beams=10,
    generation_length_penalty=1.5,
    predict_with_generation=True,
    representation_search_type='BRUTEFORCE',
    output_concatenation_weight=1.0,
    target_indices_key='plbl2data_idx',
    target_pointer_key='plbl2data_data2ptr',
    fp16=True,
)

# %% ../nbs/46-1-encoder-parallel-ramen-clover-with-input-concatenation-for-wikiseealso.ipynb 12
output_dir = f"/home/aiscuser/scratch/Projects/xc_nlg/outputs/{os.path.basename(args.output_dir)}"
mname = f'{output_dir}/{os.path.basename(get_best_model(output_dir))}'

# %% ../nbs/46-1-encoder-parallel-ramen-clover-with-input-concatenation-for-wikiseealso.ipynb 13
bsz = max(args.per_device_train_batch_size, args.per_device_eval_batch_size)*torch.cuda.device_count()

model = DBT017.from_pretrained(mname, ig_tok=0, bsz=bsz, tn_targ=1000, margin=0.3, tau=0.1, 
                               n_negatives=5, apply_softmax=True, lw=0.01, m_lw=0.3, meta_prefix='cat', 
                               tie_word_embeddings=False)

# %% ../nbs/46-1-encoder-parallel-ramen-clover-with-input-concatenation-for-wikiseealso.ipynb 14
trie = XCTrie.from_block(block)

# %% ../nbs/46-1-encoder-parallel-ramen-clover-with-input-concatenation-for-wikiseealso.ipynb 15
train_dset = block.train.dset.sample(n=50_000, seed=50)
metric = PrecRecl(block.n_lbl, train_dset.data.data_lbl_filterer, prop=block.train.dset.data.data_lbl,
                  pk=10, rk=200, rep_pk=[1, 3, 5, 10], rep_rk=[10, 100, 200])

learn = XCLearner(model=model, args=args, trie=trie, train_dataset=block.train.dset, eval_dataset=train_dset,
                  data_collator=block.collator, compute_metrics=metric)

if __name__ == '__main__':
    mp.freeze_support()
    train_pred = learn.predict(train_dset)
    
display_metric(train_pred.metrics)

# %% ../nbs/46-1-encoder-parallel-ramen-clover-with-input-concatenation-for-wikiseealso.ipynb 16
pred_dir = f'{mname}/predictions/'
os.makedirs(pred_dir, exist_ok=True)
with open(f'{pred_dir}/train_predictions.pkl', 'wb') as file: pickle.dump(train_pred, file)

# %% ../nbs/46-1-encoder-parallel-ramen-clover-with-input-concatenation-for-wikiseealso.ipynb 19
test_dset = block.test.dset.sample(n=2000, seed=50)
metric = PrecRecl(block.n_lbl, block.test.data_lbl_filterer, prop=block.train.dset.data.data_lbl,
                  pk=10, rk=200, rep_pk=[1, 3, 5, 10], rep_rk=[10, 100, 200])

learn = XCLearner(model=model, args=args, trie=trie, train_dataset=block.train.dset, eval_dataset=test_dset,
                  data_collator=block.collator, compute_metrics=metric)

if __name__ == '__main__':
    mp.freeze_support()
    test_pred = learn.predict(block.test.dset)
    
display_metric(test_pred.metrics)

# %% ../nbs/46-1-encoder-parallel-ramen-clover-with-input-concatenation-for-wikiseealso.ipynb 20
pred_dir = f'{mname}/predictions/'
os.makedirs(pred_dir, exist_ok=True)
with open(f'{pred_dir}/test_predictions.pkl', 'wb') as file: pickle.dump(test_pred, file)
