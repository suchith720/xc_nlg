# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/67-1-ngame-ep-for-wikiseealso-with-input-concatenation-prediction.ipynb.

# %% auto 0
__all__ = ['data_dir', 'block', 'pkl_dir', 'pkl_file', 'args', 'metric', 'output_dir', 'mname', 'bsz', 'model',
           'model_weight_file', 'model_weights', 'learn', 'o', 'pred_dir']

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
block = XCBlock.from_cfg(data_dir, 'data_metas', valid_pct=0.001, tfm='xcnlg', tokenizer='distilbert-base-uncased', 
                         smp_features=[('lbl2data',1,1)])

# %% ../nbs/67-1-ngame-ep-for-wikiseealso-with-input-concatenation-prediction.ipynb 27
pkl_dir = '/home/scai/phd/aiz218323/scratch/datasets'
pkl_file = f'{pkl_dir}/processed/wikiseealso_data-metas_distilbert-base-uncased_rm_radga-aug-cat-hlk-block-032.pkl'
with open(pkl_file, 'rb') as file: block = pickle.load(file)

# %% ../nbs/67-1-ngame-ep-for-wikiseealso-with-input-concatenation-prediction.ipynb 32
block.train.dset.data.data_info['input_ids'] = block.train.dset.data.data_info['input_ids_aug_cat']
block.train.dset.data.data_info['attention_mask'] = block.train.dset.data.data_info['attention_mask_aug_cat']
block.test.dset.data.data_info['input_ids'] = block.test.dset.data.data_info['input_ids_aug_cat']
block.test.dset.data.data_info['attention_mask'] = block.test.dset.data.data_info['attention_mask_aug_cat']

# %% ../nbs/67-1-ngame-ep-for-wikiseealso-with-input-concatenation-prediction.ipynb 33
block.train.dset.data.lbl_info['input_ids'] = block.train.dset.data.lbl_info['input_ids_aug_cat']
block.train.dset.data.lbl_info['attention_mask'] = block.train.dset.data.lbl_info['attention_mask_aug_cat']
block.test.dset.data.lbl_info['input_ids'] = block.test.dset.data.lbl_info['input_ids_aug_cat']
block.test.dset.data.lbl_info['attention_mask'] = block.test.dset.data.lbl_info['attention_mask_aug_cat']

# %% ../nbs/67-1-ngame-ep-for-wikiseealso-with-input-concatenation-prediction.ipynb 34
block.train.dset.data.data_info['input_ids'] = block.train.dset.data.lbl_info['input_ids_aug_hlk']
block.train.dset.data.data_info['attention_mask'] = block.train.dset.data.lbl_info['attention_mask_aug_hlk']
block.test.dset.data.data_info['input_ids'] = block.test.dset.data.lbl_info['input_ids_aug_hlk']
block.test.dset.data.data_info['attention_mask'] = block.test.dset.data.lbl_info['attention_mask_aug_hlk']

# %% ../nbs/67-1-ngame-ep-for-wikiseealso-with-input-concatenation-prediction.ipynb 35
block.train.dset.data.lbl_info['input_ids'] = block.train.dset.data.lbl_info['input_ids_aug_hlk']
block.train.dset.data.lbl_info['attention_mask'] = block.train.dset.data.lbl_info['attention_mask_aug_hlk']
block.test.dset.data.lbl_info['input_ids'] = block.test.dset.data.lbl_info['input_ids_aug_hlk']
block.test.dset.data.lbl_info['attention_mask'] = block.test.dset.data.lbl_info['attention_mask_aug_hlk']

# %% ../nbs/67-1-ngame-ep-for-wikiseealso-with-input-concatenation-prediction.ipynb 48
args = XCLearningArguments(
    output_dir='/home/scai/phd/aiz218323/scratch/outputs/67-ngame-ep-for-wikiseealso-with-input-concatenation-1-2',
    logging_first_step=True,
    per_device_train_batch_size=800,
    per_device_eval_batch_size=800,
    representation_num_beams=200,
    representation_accumulation_steps=100,
    predict_with_representation=True,
    representation_search_type='INDEX',
    target_indices_key='plbl2data_idx',
    target_pointer_key='plbl2data_data2ptr',
    use_encoder_parallel=True,
    fp16=True,
)

# %% ../nbs/67-1-ngame-ep-for-wikiseealso-with-input-concatenation-prediction.ipynb 49
metric = PrecRecl(block.n_lbl, block.test.data_lbl_filterer, prop=block.train.dset.data.data_lbl,
                  pk=10, rk=200, rep_pk=[1, 3, 5, 10], rep_rk=[10, 100, 200])

# %% ../nbs/67-1-ngame-ep-for-wikiseealso-with-input-concatenation-prediction.ipynb 50
output_dir = f"/home/scai/phd/aiz218323/scratch/outputs/{os.path.basename(args.output_dir)}"
mname = f'{output_dir}/{os.path.basename(get_best_model(output_dir))}'

# %% ../nbs/67-1-ngame-ep-for-wikiseealso-with-input-concatenation-prediction.ipynb 52
bsz = max(args.per_device_train_batch_size, args.per_device_eval_batch_size)*torch.cuda.device_count()

model = DBT009.from_pretrained('sentence-transformers/msmarco-distilbert-base-v4', bsz=bsz, tn_targ=5000, margin=0.3, tau=0.1,
                               n_negatives=10, apply_softmax=True, use_encoder_parallel=True)

# %% ../nbs/67-1-ngame-ep-for-wikiseealso-with-input-concatenation-prediction.ipynb 53
from safetensors import safe_open

model_weight_file = f'{mname}/model.safetensors'

model_weights = {}
with safe_open(model_weight_file, framework="pt") as file:
    for k in file.keys(): model_weights[k] = file.get_tensor(k)
        

# %% ../nbs/67-1-ngame-ep-for-wikiseealso-with-input-concatenation-prediction.ipynb 54
model.load_state_dict(model_weights, strict=False)

# %% ../nbs/67-1-ngame-ep-for-wikiseealso-with-input-concatenation-prediction.ipynb 56
learn = XCLearner(
    model=model, 
    args=args,
    train_dataset=block.train.dset,
    eval_dataset=block.test.dset,
    data_collator=block.collator,
    compute_metrics=metric,
)

# %% ../nbs/67-1-ngame-ep-for-wikiseealso-with-input-concatenation-prediction.ipynb 57
o = learn.predict(block.test.dset)

# %% ../nbs/67-1-ngame-ep-for-wikiseealso-with-input-concatenation-prediction.ipynb 60
pred_dir = f"{mname}/predictions/"
os.makedirs(pred_dir, exist_ok=True)

with open(f'{pred_dir}/test_predictions.pkl', 'wb') as file: pickle.dump(o, file)


# %% ../nbs/67-1-ngame-ep-for-wikiseealso-with-input-concatenation-prediction.ipynb 61
print(o.metrics)