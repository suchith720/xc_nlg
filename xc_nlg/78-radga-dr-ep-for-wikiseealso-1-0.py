# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/78-radga-dr-ep-for-wikiseealso.ipynb.

# %% auto 0
__all__ = ['pkl_dir', 'pkl_file', 'lco_meta', 'args', 'metric', 'bsz', 'model', 'learn']

# %% ../nbs/78-radga-dr-ep-for-wikiseealso.ipynb 3
import os,torch, torch.multiprocessing as mp, pickle
from xcai.basics import *
from xcai.models.radga import RAD006

# %% ../nbs/78-radga-dr-ep-for-wikiseealso.ipynb 5
os.environ['CUDA_VISIBLE_DEVICES'] = '0,1'
os.environ['WANDB_PROJECT']='xc-nlg_66-radga-dr-ep-for-wikiseealso-2'

# %% ../nbs/78-radga-dr-ep-for-wikiseealso.ipynb 7
pkl_dir = '/home/scai/phd/aiz218323/scratch/datasets/'
pkl_file = f'{pkl_dir}/processed/wikiseealso_data-metas_distilbert-base-uncased_rm_radga-cat-linker.pkl'

# %% ../nbs/78-radga-dr-ep-for-wikiseealso.ipynb 9
with open(pkl_file, 'rb') as file: block = pickle.load(file)

# %% ../nbs/78-radga-dr-ep-for-wikiseealso.ipynb 15
with open(f'{pkl_dir}/processed/corelations.pkl', 'rb') as file: data_corel, lbl_corel = pickle.load(file)

from xcai.data import MetaXCDataset, XCDataset
from scipy import sparse

lco_meta = MetaXCDataset('lco', sparse.csr_matrix((block.train.dset.n_data, block.n_lbl)), lbl_corel, 
                         block.train.dset.data.lbl_info)

block.train.dset.meta['lco_meta'] = lco_meta

# %% ../nbs/78-radga-dr-ep-for-wikiseealso.ipynb 16
from xcai.data import MetaXCDataset
block.train.dset.meta['hyb_meta'] = block.train.dset.meta['cat_meta']
block.test.dset.meta['hyb_meta'] = block.train.dset.meta['lnk_meta']

# %% ../nbs/78-radga-dr-ep-for-wikiseealso.ipynb 17
block.train.dset.meta['hyb_meta'] = MetaXCDataset('hyb', block.train.dset.meta['cat_meta'].data_meta, 
                                                  block.train.dset.meta['cat_meta'].lbl_meta,
                                                  block.train.dset.meta['cat_meta'].meta_info)
block.test.dset.meta['hyb_meta'] = MetaXCDataset('hyb', block.train.dset.meta['lnk_meta'].data_meta, 
                                                  block.train.dset.meta['lnk_meta'].lbl_meta,
                                                  block.train.dset.meta['lnk_meta'].meta_info)

# %% ../nbs/78-radga-dr-ep-for-wikiseealso.ipynb 18
block.collator.tfms.tfms[0].smp_features = [('lbl2data|hyb2lbl2data|lco2lbl2data', 1, (1,3,1)), 
                                            ('hyb2data',1,3)]

# %% ../nbs/78-radga-dr-ep-for-wikiseealso.ipynb 44
args = XCLearningArguments(
    output_dir='/home/scai/phd/aiz218323/scratch/outputs/78-radga-dr-ep-for-wikiseealso-1-0',
    logging_first_step=True,
    per_device_train_batch_size=10, #800,
    per_device_eval_batch_size=800,
    representation_num_beams=200,
    representation_accumulation_steps=10,
    save_strategy="steps",
    evaluation_strategy="steps",
    eval_steps=10, #5000,
    save_steps=10, #5000,
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
    representation_search_type='BRUTEFORCE',
    
    output_representation_attribute='data_fused_repr',
    label_representation_attribute='data_repr',
    metadata_representation_attribute='data_repr',
    data_augmentation_attribute='data_repr',
    representation_attribute='data_fused_repr',
    clustering_representation_attribute='data_fused_repr',
    
    group_by_cluster=True,
    num_clustering_warmup_epochs=10,
    num_cluster_update_epochs=5,
    num_cluster_size_update_epochs=25,
    use_data_metadata_for_clustering=True,
    clustering_type='EXPO',
    minimum_cluster_size=2,
    maximum_cluster_size=1600,

    metric_for_best_model='P@1',
    load_best_model_at_end=True,
    target_indices_key='plbl2data_idx',
    target_pointer_key='plbl2data_data2ptr',
    
    use_distributional_representation=False,
    use_encoder_parallel=True,
    max_grad_norm=None, 
    fp16=True,
    
    label_names=['hyb2data_idx', 'hyb2data_input_ids', 'hyb2data_attention_mask', 
                 'lco2lbl2data_idx', 'lco2lbl2data_input_ids', 'lco2lbl2data_attention_mask'],

    prune_metadata=False,
    num_metadata_prune_warmup_epochs=10,
    num_metadata_prune_epochs=5,
    metadata_prune_batch_size=2048,
    prune_metadata_names=['cat_meta'],
    use_data_metadata_for_pruning=True,

    predict_with_augmentation=False,
    use_augmentation_index_representation=True,
    
    data_aug_meta_name='hyb',
    augmentation_num_beams=3,
    data_aug_prefix='hyb',
    use_label_metadata=False,
    
    data_meta_batch_size=2048,
    augment_metadata=False,
    num_metadata_augment_warmup_epochs=10,
    num_metadata_augment_epochs=5,
)

# %% ../nbs/78-radga-dr-ep-for-wikiseealso.ipynb 45
metric = PrecRecl(block.n_lbl, block.test.data_lbl_filterer, prop=block.train.dset.data.data_lbl,
                  pk=10, rk=200, rep_pk=[1, 3, 5, 10], rep_rk=[10, 100, 200])

# %% ../nbs/78-radga-dr-ep-for-wikiseealso.ipynb 47
bsz = max(args.per_device_train_batch_size, args.per_device_eval_batch_size)*torch.cuda.device_count()

model = RAD006.from_pretrained('sentence-transformers/msmarco-distilbert-base-v4', batch_size=bsz, num_batch_labels=5000, 
                               margin=0.3, num_negatives=10, tau=0.1, apply_softmax=True,
                               
                               data_aug_meta_prefix='hyb2data', lbl2data_aug_meta_prefix=None, 
                               data_pred_meta_prefix=None, lbl2data_pred_meta_prefix='lco2lbl',

                               resize_length=5000, use_noise=True, shuffle_noise_pct=0.4, dropout_noise_pct=0.1,
                               
                               use_query_loss=True,

                               calib_margin=0.3, calib_num_negatives=10, calib_tau=0.1, calib_apply_softmax=True, calib_loss_weight=1.0,
                               use_calib_loss= True,
                               
                               meta_loss_weight=0.1, fusion_loss_weight=0.1, use_fusion_loss=True,
                               use_encoder_parallel=False)

model.init_retrieval_head()
model.init_cross_head()

# %% ../nbs/78-radga-dr-ep-for-wikiseealso.ipynb 49
learn = XCLearner(
    model=model, 
    args=args,
    train_dataset=block.train.dset,
    eval_dataset=block.test.dset,
    data_collator=block.collator,
    compute_metrics=metric,
)

# %% ../nbs/78-radga-dr-ep-for-wikiseealso.ipynb 52
if __name__ == '__main__':
    mp.freeze_support()
    learn.train()
    
