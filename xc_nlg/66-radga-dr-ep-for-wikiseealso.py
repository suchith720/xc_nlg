# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/66-radga-dr-ep-for-wikiseealso.ipynb.

# %% auto 0
__all__ = ['data_dir', 'pkl_file', 'args', 'metric', 'bsz', 'model', 'learn']

# %% ../nbs/66-radga-dr-ep-for-wikiseealso.ipynb 3
import os,torch, torch.multiprocessing as mp, pickle
from xcai.basics import *
from xcai.models.radga import RAD002

# %% ../nbs/66-radga-dr-ep-for-wikiseealso.ipynb 5
os.environ['CUDA_VISIBLE_DEVICES'] = '0,1'
os.environ['WANDB_PROJECT']='xc-nlg_66-radga-dr-ep-for-wikiseealso'

# %% ../nbs/66-radga-dr-ep-for-wikiseealso.ipynb 10
data_dir = '/home/scai/phd/aiz218323/scratch/datasets/'
pkl_file = f'{pkl_dir}/processed/wikiseealso_data-metas_distilbert-base-uncased_rm_radga-cat-final.pkl'

# %% ../nbs/66-radga-dr-ep-for-wikiseealso.ipynb 15
with open(pkl_file, 'rb') as file: block = pickle.load(file)

# %% ../nbs/66-radga-dr-ep-for-wikiseealso.ipynb 17
args = XCLearningArguments(
    output_dir='/home/scai/phd/aiz218323/scratch/outputs/66-radga-dr-ep-for-wikiseealso-1-0',
    logging_first_step=True,
    per_device_train_batch_size=800,
    per_device_eval_batch_size=800,
    representation_num_beams=200,
    representation_accumulation_steps=10,
    representation_attribute="data_fused_repr",
    save_strategy="steps",
    evaluation_strategy="steps",
    eval_steps=5000,
    save_steps=5000,
    save_total_limit=5,
    num_train_epochs=300,
    predict_with_representation=True,
    adam_epsilon=1e-6,
    warmup_steps=100,
    weight_decay=0.0,
    learning_rate=2e-4,
    generation_num_beams=10,
    generation_length_penalty=1.5,
    predict_with_generation=True,
    representation_search_type='INDEX',
    group_by_cluster=True,
    num_clustering_warmup_epochs=10,
    num_cluster_update_epochs=5,
    num_cluster_size_update_epochs=25,
    clustering_type='EXPO',
    minimum_cluster_size=2,
    maximum_cluster_size=1600,
    output_concatenation_weight=1.0,
    metric_for_best_model='P@1',
    load_best_model_at_end=True,
    target_indices_key='plbl2data_idx',
    target_pointer_key='plbl2data_data2ptr',
    use_encoder_parallel=True,
    max_grad_norm=None,
    fp16=True,
    label_names=['cat2data_idx', 'cat2data_input_ids', 'cat2data_attention_mask'],
    # label_names=['hlk2data_idx', 'hlk2data_input_ids', 'hlk2data_attention_mask',
    #              'hlk2lbl2data_idx', 'hlk2lbl2data_input_ids', 'hlk2lbl2data_attention_mask'],
)

# %% ../nbs/66-radga-dr-ep-for-wikiseealso.ipynb 18
metric = PrecRecl(block.n_lbl, block.test.data_lbl_filterer, prop=block.train.dset.data.data_lbl,
                  pk=10, rk=200, rep_pk=[1, 3, 5, 10], rep_rk=[10, 100, 200])

# %% ../nbs/66-radga-dr-ep-for-wikiseealso.ipynb 19
bsz = max(args.per_device_train_batch_size, args.per_device_eval_batch_size)*torch.cuda.device_count()

model = RAD002.from_pretrained('sentence-transformers/msmarco-distilbert-base-v4', num_batch_labels=5000, batch_size=bsz,
                               margin=0.3, num_negatives=10, tau=0.1, apply_softmax=True,
                               
                               data_aug_meta_prefix='cat2data', lbl2data_aug_meta_prefix='cat2lbl', 
                               resize_length=5000,
                               
                               meta_loss_weight=0.3, pred_meta_prefix='hlk', 
                               
                               fusion_loss_weight=0.05, use_fusion_loss=False, use_noise=False, use_encoder_parallel=True)
model.init_retrieval_head()
model.init_cross_head()

# %% ../nbs/66-radga-dr-ep-for-wikiseealso.ipynb 20
learn = XCLearner(
    model=model, 
    args=args,
    train_dataset=block.train.dset,
    eval_dataset=block.test.dset,
    data_collator=block.collator,
    compute_metrics=metric,
)

# %% ../nbs/66-radga-dr-ep-for-wikiseealso.ipynb 24
if __name__ == '__main__':
    mp.freeze_support()
    learn.train()

# %% ../nbs/66-radga-dr-ep-for-wikiseealso.ipynb 26
args = XCLearningArguments(
    output_dir='/home/scai/phd/aiz218323/scratch/outputs/66-radga-dr-ep-for-wikiseealso-1-6',
    logging_first_step=True,
    per_device_train_batch_size=800,
    per_device_eval_batch_size=800,
    representation_num_beams=200,
    representation_accumulation_steps=10,
    output_representation_attribute="data_fused_repr",
    representation_attribute="data_fused_repr",
    
    predict_with_representation=True,
    representation_search_type='INDEX',
    
    metric_for_best_model='P@1',
    target_indices_key='plbl2data_idx',
    target_pointer_key='plbl2data_data2ptr',
    use_encoder_parallel=True,
    fp16=True,
    label_names=['cat2data_idx', 'cat2data_input_ids', 'cat2data_attention_mask'],
    # label_names=['hlk2data_idx', 'hlk2data_input_ids', 'hlk2data_attention_mask',
    #              'hlk2lbl2data_idx', 'hlk2lbl2data_input_ids', 'hlk2lbl2data_attention_mask'],

    predict_with_augmentation=False,
    use_augmentation_index_representation=True,
    
    data_aug_meta_name='cat',
    augmentation_num_beams=3,
    data_aug_prefix='aug',
    use_label_metadata=False,
)
