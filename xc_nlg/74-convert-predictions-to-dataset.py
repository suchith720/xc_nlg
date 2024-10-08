# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/74-convert-predictions-to-dataset.ipynb.

# %% auto 0
__all__ = ['data_dir', 'pred_name', 'preds', 'load_pred']

# %% ../nbs/74-convert-predictions-to-dataset.ipynb 2
import xclib.data.data_utils as du, os, numpy as np
from scipy import sparse
from xclib.utils.sparse import retain_topk

from xcai.basics import *

# %% ../nbs/74-convert-predictions-to-dataset.ipynb 4
def load_pred(fname):
    o = np.load(fname)
    return sparse.csr_matrix((o['data'], o['indices'], o['indptr']), dtype=np.float32)
    

# %% ../nbs/74-convert-predictions-to-dataset.ipynb 7
data_dir = '/home/scai/phd/aiz218323/Projects/XC_NLG/data/(mapped)LF-WikiSeeAlsoTitles-320K/'

pred_name = f'{data_dir}/category_renee_trn_X_Y.npz'
# preds = retain_topk(load_pred(pred_name), k=5)

preds = load_pred(pred_name)
du.write_sparse_file(preds, f'{data_dir}/category_renee_trn_X_Y.txt')

# %% ../nbs/74-convert-predictions-to-dataset.ipynb 10
pred_name = f'{data_dir}/category_renee_tst_X_Y.npz'
# preds = retain_topk(load_pred(pred_name), k=5)

preds = load_pred(pred_name)
du.write_sparse_file(preds, f'{data_dir}/category_renee_tst_X_Y.txt')

# %% ../nbs/74-convert-predictions-to-dataset.ipynb 11
preds = sparse.csr_matrix((312330, preds.shape[1]))
du.write_sparse_file(preds, f'{data_dir}/category_renee_lbl_X_Y.txt')

# %% ../nbs/74-convert-predictions-to-dataset.ipynb 14
data_dir = '/home/scai/phd/aiz218323/Projects/XC_NLG/data/(mapped)LF-WikiTitles-500K'

pred_name = f'{data_dir}/hyper_link_renee_trn_X_Y.npz'
#preds = retain_topk(load_pred(pred_name), k=5)

preds = sparse.load_npz(pred_name)
du.write_sparse_file(preds, f'{data_dir}/hyper_link_renee_trn_X_Y.txt')

# %% ../nbs/74-convert-predictions-to-dataset.ipynb 16
pred_name = f'{data_dir}/hyper_link_renee_tst_X_Y.npz'
# preds = retain_topk(load_pred(pred_name), k=5)

preds = sparse.load_npz(pred_name)
du.write_sparse_file(preds, f'{data_dir}/hyper_link_renee_tst_X_Y.txt')

# %% ../nbs/74-convert-predictions-to-dataset.ipynb 18
preds = sparse.csr_matrix((501070, 2148579))
du.write_sparse_file(preds, f'{data_dir}/hyper_link_renee_lbl_X_Y.txt')
