# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/67-1-ngame-ep-for-wikiseealso-with-input-concatenation-prediction.ipynb.

# %% auto 0
__all__ = ['data_dir', 'block', 'pkl_file', 'pkl_dir', 'args', 'metric', 'bsz', 'model', 'learn']

# %% ../nbs/67-1-ngame-ep-for-wikiseealso-with-input-concatenation-prediction.ipynb 2
from scipy import sparse
from tqdm.auto import tqdm
import os,torch, torch.multiprocessing as mp, pickle, numpy as np
from xcai.basics import *
from xcai.models.PPP0XX import DBT009,DBT011

# %% ../nbs/67-1-ngame-ep-for-wikiseealso-with-input-concatenation-prediction.ipynb 4
os.environ['CUDA_VISIBLE_DEVICES'] = '0,1'
os.environ['WANDB_PROJECT']='xc-nlg_66-radga-dr-ep-for-wikiseealso'

# %% ../nbs/67-1-ngame-ep-for-wikiseealso-with-input-concatenation-prediction.ipynb 6
data_dir = '/home/scai/phd/aiz218323/Projects/XC_NLG/data'

# %% ../nbs/67-1-ngame-ep-for-wikiseealso-with-input-concatenation-prediction.ipynb 7
block = XCBlock.from_cfg(data_dir, 'data_metas', tfm='xcnlg', tokenizer='distilbert-base-uncased',
                         smp_features=[('lbl2data',1,1)])

# %% ../nbs/67-1-ngame-ep-for-wikiseealso-with-input-concatenation-prediction.ipynb 13
block = AugmentMetaInputIdsTfm.apply(block, 'cat_meta', 'data', 128, True)
block = AugmentMetaInputIdsTfm.apply(block, 'cat_meta', 'lbl', 128, True)

# %% ../nbs/67-1-ngame-ep-for-wikiseealso-with-input-concatenation-prediction.ipynb 14
block = AugmentMetaInputIdsTfm.apply(block, 'hlk_meta', 'data', 128, True)
block = AugmentMetaInputIdsTfm.apply(block, 'hlk_meta', 'lbl', 128, True)

# %% ../nbs/67-1-ngame-ep-for-wikiseealso-with-input-concatenation-prediction.ipynb 16
pkl_dir = '/home/scai/phd/aiz218323/scratch/datasets'
pkl_file = f'{pkl_dir}/processed/wikiseealso_data-metas_distilbert-base-uncased_rm_radga-aug-cat-hlk-block-128.pkl'
with open(pkl_file, 'wb') as file: pickle.dump(block, file)
