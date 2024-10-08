# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/92-radga-dr-ep-for-wikiseealso-lora.ipynb.

# %% auto 0
__all__ = ['pkl_dir', 'pkl_file', 'data_meta', 'args', 'metric', 'bsz', 'base_model', 'model', 'learn']

# %% ../nbs/92-radga-dr-ep-for-wikiseealso-lora.ipynb 3
import os,torch, torch.multiprocessing as mp, pickle
from xcai.basics import *
from xcai.models.radga_lora import RAD001
from xclib.utils.sparse import retain_topk

from transformers import DistilBertConfig,DistilBertModel

# %% ../nbs/92-radga-dr-ep-for-wikiseealso-lora.ipynb 6
os.environ['CUDA_VISIBLE_DEVICES'] = '0,1'
os.environ['WANDB_PROJECT']='xc-nlg_66-radga-dr-ep-for-wikiseealso-2'

# %% ../nbs/92-radga-dr-ep-for-wikiseealso-lora.ipynb 8
pkl_dir = '/home/scai/phd/aiz218323/scratch/datasets/'
pkl_file = f'{pkl_dir}/processed/wikiseealso_data-linker_distilbert-base-uncased_rm_oak-linker.pkl'

# %% ../nbs/92-radga-dr-ep-for-wikiseealso-lora.ipynb 9
with open(pkl_file, 'rb') as file: block = pickle.load(file)

# %% ../nbs/92-radga-dr-ep-for-wikiseealso-lora.ipynb 11
data_meta = retain_topk(block.train.dset.meta.lnk_meta.data_meta, k=5)
block.train.dset.meta.lnk_meta.data_meta = data_meta
block.train.dset.meta.lnk_meta.curr_data_meta = data_meta

data_meta = retain_topk(block.test.dset.meta.lnk_meta.data_meta, k=3)
block.test.dset.meta.lnk_meta.data_meta = data_meta
block.test.dset.meta.lnk_meta.curr_data_meta = data_meta

# %% ../nbs/92-radga-dr-ep-for-wikiseealso-lora.ipynb 14
args = XCLearningArguments(
    output_dir='/home/scai/phd/aiz218323/scratch/outputs/92-radga-dr-ep-for-wikiseealso-lora-1-0',
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
    
    label_names=['lnk2data_idx', 'lnk2data_input_ids', 'lnk2data_attention_mask'],
    
    prune_metadata=False,
    num_metadata_prune_warmup_epochs=10,
    num_metadata_prune_epochs=5,
    metadata_prune_batch_size=2048,
    prune_metadata_names=['cat_meta'],
    use_data_metadata_for_pruning=True,

    predict_with_augmentation=False,
    use_augmentation_index_representation=True,
    
    data_aug_meta_name='lnk',
    augmentation_num_beams=3,
    data_aug_prefix='lnk',
    use_label_metadata=False,
    
    data_meta_batch_size=2048,
    augment_metadata=False,
    num_metadata_augment_warmup_epochs=10,
    num_metadata_augment_epochs=5,
)

# %% ../nbs/92-radga-dr-ep-for-wikiseealso-lora.ipynb 15
metric = PrecRecl(block.n_lbl, block.test.data_lbl_filterer, prop=block.train.dset.data.data_lbl,
                  pk=10, rk=200, rep_pk=[1, 3, 5, 10], rep_rk=[10, 100, 200])

# %% ../nbs/92-radga-dr-ep-for-wikiseealso-lora.ipynb 17
bsz = max(args.per_device_train_batch_size, args.per_device_eval_batch_size)*torch.cuda.device_count()

base_model = DistilBertModel.from_pretrained('sentence-transformers/msmarco-distilbert-base-v4')

model = RAD001(DistilBertConfig(), resize_length=5000, base_model=base_model, lora_r=8, lora_alpha=32,
               
               batch_size=100, num_batch_labels=5000, margin=0.3, num_negatives=10, tau=0.1, apply_softmax=True,
                               
               data_aug_meta_prefix='lnk2data', lbl2data_aug_meta_prefix=None, data_pred_meta_prefix=None, lbl2data_pred_meta_prefix=None,
               
               use_query_loss=True,
               
               calib_margin=0.05, calib_num_negatives=10, calib_tau=0.1, calib_apply_softmax=False, calib_loss_weight=0.1,
               use_calib_loss=True,
               
               meta_loss_weight=0.0, fusion_loss_weight=0.0, use_fusion_loss=False,
               use_encoder_parallel=False)

model.init_retrieval_head()
model.init_cross_head()

# %% ../nbs/92-radga-dr-ep-for-wikiseealso-lora.ipynb 20
learn = XCLearner(
    model=model, 
    args=args,
    train_dataset=block.train.dset,
    eval_dataset=test_dset, #block.test.dset,
    data_collator=block.collator,
    compute_metrics=metric,
)

# %% ../nbs/92-radga-dr-ep-for-wikiseealso-lora.ipynb 26
if __name__ == '__main__':
    mp.freeze_support()
    learn.train()
    
