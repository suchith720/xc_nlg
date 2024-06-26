# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/53-encoder-parallel-radga-with-cross-attention-loss-component-for-wikititles.ipynb.

# %% auto 0
__all__ = ['data_dir', 'pkl_dir', 'args', 'test_dset', 'metric', 'bsz', 'model', 'trie', 'learn']

# %% ../nbs/53-encoder-parallel-radga-with-cross-attention-loss-component-for-wikititles.ipynb 3
import os,sys,torch,pickle,torch.multiprocessing as mp, pickle
from xcai.basics import *
from xcai.models.radga import RAD001

# %% ../nbs/53-encoder-parallel-radga-with-cross-attention-loss-component-for-wikititles.ipynb 5
os.environ['CUDA_VISIBLE_DEVICES'] = '8,9,10,11,12,13'
os.environ['WANDB_PROJECT']='xc-nlg_53-encoder-parallel-radga-with-cross-attention-loss-component-for-wikititles'

# %% ../nbs/53-encoder-parallel-radga-with-cross-attention-loss-component-for-wikititles.ipynb 7
data_dir = '/home/aiscuser/scratch/datasets'

# %% ../nbs/53-encoder-parallel-radga-with-cross-attention-loss-component-for-wikititles.ipynb 10
pkl_dir = f'{data_dir}/processed/'

# %% ../nbs/53-encoder-parallel-radga-with-cross-attention-loss-component-for-wikititles.ipynb 12
with open(f'{pkl_dir}/wikititles_data-metas_distilbert-base-uncased_rm_radga-final.pkl', 'rb') as file: 
    block = pickle.load(file)

# %% ../nbs/53-encoder-parallel-radga-with-cross-attention-loss-component-for-wikititles.ipynb 14
args = XCLearningArguments(
    output_dir='/home/aiscuser/outputs/53-encoder-parallel-radga-with-cross-attention-loss-component-for-wikititles-1-0',
    logging_first_step=True,
    per_device_train_batch_size=200,
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
    use_encoder_parallel=True,
    metric_for_best_model='P@1_REPR',
    target_indices_key='plbl2data_idx',
    target_pointer_key='plbl2data_data2ptr',
    fp16=True,
    label_names=['sal2data_idx', 'sal2data_input_ids', 'sal2data_attention_mask',
                 'hlk2data_idx', 'hlk2data_input_ids', 'hlk2data_attention_mask'],
)

# %% ../nbs/53-encoder-parallel-radga-with-cross-attention-loss-component-for-wikititles.ipynb 16
test_dset = block.test.dset.sample(n=2000, seed=50)
metric = PrecRecl(block.n_lbl, test_dset.data.data_lbl_filterer, prop=block.train.dset.data.data_lbl,
                  pk=10, rk=200, rep_pk=[1, 3, 5, 10], rep_rk=[10, 100, 200])

# %% ../nbs/53-encoder-parallel-radga-with-cross-attention-loss-component-for-wikititles.ipynb 17
bsz = max(args.per_device_train_batch_size, args.per_device_eval_batch_size)*torch.cuda.device_count()


model = RAD001.from_pretrained('distilbert-base-uncased', num_batch_labels=5000, ignore_token=0, batch_size=bsz,
                               margin=0.3, num_negatives=5, tau=0.1, apply_softmax=True,
                               
                               data_aug_meta_prefix='hlk2data', lbl2data_aug_meta_prefix='hlk2lbl', 
                               resize_length=5000,
                               
                               gen_loss_weight=0.001, meta_loss_weight=0.3, pred_meta_prefix='sal', 
                               
                               fusion_loss_weight=0.1, tie_word_embeddings=False,
                               
                               use_fusion_loss=True, use_noise=True, use_encoder_parallel=True)

model.init_retrieval_head()
model.init_generation_head()

# %% ../nbs/53-encoder-parallel-radga-with-cross-attention-loss-component-for-wikititles.ipynb 18
trie = XCTrie.from_block(block)

# %% ../nbs/53-encoder-parallel-radga-with-cross-attention-loss-component-for-wikititles.ipynb 19
learn = XCLearner(
    model=model, 
    args=args,
    trie=trie,
    train_dataset=block.train.dset,
    eval_dataset=test_dset,
    data_collator=block.collator,
    compute_metrics=metric,
)

# %% ../nbs/53-encoder-parallel-radga-with-cross-attention-loss-component-for-wikititles.ipynb 21
if __name__ == '__main__':
    mp.freeze_support()
    learn.train()
    
