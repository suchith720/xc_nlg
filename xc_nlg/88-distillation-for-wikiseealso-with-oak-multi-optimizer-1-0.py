# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/88-distillation-for-wikiseealso-with-oak-multi-optimizer.ipynb.

# %% auto 0
__all__ = ['pkl_dir', 'pkl_file', 'data_meta', 'args', 'model_output', 'm_teacher', 'bsz', 'm_student', 'meta_embed_file',
           'model', 'metric', 'learn', 'MultipleOptimizer', 'MultipleScheduler']

# %% ../nbs/88-distillation-for-wikiseealso-with-oak-multi-optimizer.ipynb 2
import os,torch, torch.multiprocessing as mp, pickle, numpy as np, transformers
from transformers import DistilBertConfig

from xcai.basics import *
from xcai.models.oak import OAK001
from xcai.models.distillation import DTL004,TCH001,TCH002

from xclib.utils.sparse import retain_topk

from fastcore.utils import *

# %% ../nbs/88-distillation-for-wikiseealso-with-oak-multi-optimizer.ipynb 4
os.environ['CUDA_VISIBLE_DEVICES'] = '0,1'
os.environ['WANDB_PROJECT']='xc-nlg_83-oak-dr-ep-for-wikiseealso'

# %% ../nbs/88-distillation-for-wikiseealso-with-oak-multi-optimizer.ipynb 6
pkl_dir = '/home/scai/phd/aiz218323/scratch/datasets/'
pkl_file = f'{pkl_dir}/processed/wikiseealso_data-metas_distilbert-base-uncased_rm_radga-cat-linker.pkl'

# %% ../nbs/88-distillation-for-wikiseealso-with-oak-multi-optimizer.ipynb 7
with open(pkl_file, 'rb') as file: block = pickle.load(file)

# %% ../nbs/88-distillation-for-wikiseealso-with-oak-multi-optimizer.ipynb 8
data_meta = retain_topk(block.train.dset.meta.lnk_meta.data_meta, k=10)
block.train.dset.meta.lnk_meta.curr_data_meta = data_meta
block.train.dset.meta.lnk_meta.data_meta = data_meta

data_meta = retain_topk(block.test.dset.meta.lnk_meta.data_meta, k=3)
block.test.dset.meta.lnk_meta.curr_data_meta = data_meta
block.test.dset.meta.lnk_meta.data_meta = data_meta

# %% ../nbs/88-distillation-for-wikiseealso-with-oak-multi-optimizer.ipynb 10
import torch
from itertools import chain
from collections import defaultdict

# %% ../nbs/88-distillation-for-wikiseealso-with-oak-multi-optimizer.ipynb 11
class MultipleOptimizer(torch.optim.Optimizer):
    # Wrapper around multiple optimizers that should be executed at the same time
    def __init__(self, optimizers):
        self.optimizers = optimizers

    @property
    def state(self):
        state = defaultdict(dict)
        for optimizer in self.optimizers:
            state = {**state, **optimizer.state}
        return state

    @property
    def param_groups(self):
        param_groups = []
        for optimizer in self.optimizers:
            param_groups = param_groups + optimizer.param_groups
        return param_groups

    def __getstate__(self):
        return [optimizer.__getstate__() for optimizer in self.optimizers]

    def __setstate__(self, state):
        for opt_state, optimizer in zip(self.optimizers, state):
            optimizer.__setstate__(opt_state)

    def __repr__(self):
        format_string = self.__class__.__name__ + ' ('
        for optimizer in self.optimizers:
            format_string += '\n'
            format_string += optimizer.__repr__()
        format_string += ')'
        return format_string

    def _hook_for_profile(self):
        for optimizer in self.optimizers:
            optimizer._hook_for_profile()

    def state_dict(self):
        return [optimizer.state_dict() for optimizer in self.optimizers]

    def load_state_dict(self, state_dict):
        for state, optimizer in zip(state_dict, self.optimizers):
            optimizer.load_state_dict(state)

    def zero_grad(self, set_to_none: bool = False):
        for optimizer in self.optimizers:
            optimizer.zero_grad(set_to_none=set_to_none)

    def add_param_group(self, param_group):
        raise NotImplementedError()

    def step(self, closure=None):
        loss = None
        if closure is not None:
            with torch.enable_grad():
                loss = closure()

        for optimizer in self.optimizers:
            optimizer.step()

        return loss


# %% ../nbs/88-distillation-for-wikiseealso-with-oak-multi-optimizer.ipynb 12
class MultipleScheduler(object):

    def __init__(self, sched):
        self.schedulers = sched

    def step(self, *args, **kwargs):
        for sched in self.schedulers: sched.step(*args, **kwargs)

    def get_last_lr(self):
        return list(chain(*[s.get_last_lr() for s in self.schedulers]))

    def state_dict(self):
        return [sched.state_dict() for sched in self.schedulers]

    def load_state_dict(self, state_dict):
        for sched,state in zip(self.schedulers, state_dict):
            sched.load_state_dict(state)

# %% ../nbs/88-distillation-for-wikiseealso-with-oak-multi-optimizer.ipynb 13
@patch
def create_optimizer_and_scheduler(self:XCLearner, num_training_steps: int):
    NO_DECAY = ['bias', 'LayerNorm.weight']

    dense, sparse = [], []
    for k, p in model.named_parameters():
        if p.requires_grad:
            if "meta_embeddings" not in k: dense.append((k,p))
            else: sparse.append(p)

    params = [
        {'params': [p for n, p in dense if not any(nd in n for nd in NO_DECAY)], 'weight_decay': 0.01},
        {'params': [p for n, p in dense if any(nd in n for nd in NO_DECAY)], 'weight_decay': 0.0},
    ]

    optimizer_list = [torch.optim.AdamW(params, **{'lr': self.args.learning_rate, 'eps': 1e-6}),
                      torch.optim.AdamW(sparse, **{'lr': self.args.learning_rate * self.args.free_parameter_lr_coefficient, 'eps': 1e-6})]

    self.optimizer = MultipleOptimizer(optimizer_list)
    scheduler_list = [transformers.get_linear_schedule_with_warmup(self.optimizer.optimizers[0], num_warmup_steps=self.args.warmup_steps,
                                                                   num_training_steps=num_training_steps),
                        transformers.get_cosine_schedule_with_warmup(self.optimizer.optimizers[1],
                                                                     num_warmup_steps=self.args.free_parameter_warmup_steps,
                                                                     num_training_steps=num_training_steps)]

    self.lr_scheduler = MultipleScheduler(scheduler_list)

# %% ../nbs/88-distillation-for-wikiseealso-with-oak-multi-optimizer.ipynb 15
args = XCLearningArguments(
    output_dir='/home/scai/phd/aiz218323/scratch/outputs/88-distillation-for-wikiseealso-with-oak-multi-optimizer-1-0',
    logging_first_step=True,
    per_device_train_batch_size=800,
    per_device_eval_batch_size=800,
    representation_num_beams=200,
    representation_accumulation_steps=10,
    save_strategy="steps",
    evaluation_strategy="steps",
    eval_steps=5000,
    save_steps=5000,
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
    
    label_names=['lbl2data_idx', 'lbl2data_input_ids', 'lbl2data_attention_mask', 
                 'lnk2data_idx', 'lnk2data_input_ids', 'lnk2data_attention_mask'],
    
    prune_metadata=False,
    num_metadata_prune_warmup_epochs=10,
    num_metadata_prune_epochs=5,
    metadata_prune_batch_size=2048,
    prune_metadata_names=['lnk_meta'],
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


# %% ../nbs/88-distillation-for-wikiseealso-with-oak-multi-optimizer.ipynb 16
model_output = '/home/scai/phd/aiz218323/scratch/outputs/67-ngame-ep-for-wikiseealso-with-input-concatenation-1-4'
m_teacher = TCH001.from_pretrained(f'{model_output}/teacher', n_data=block.train.dset.n_data, n_lbl=block.n_lbl)

m_teacher.freeze_embeddings()
m_teacher.freeze_data_embeddings()

# %% ../nbs/88-distillation-for-wikiseealso-with-oak-multi-optimizer.ipynb 17
model_output = '/home/scai/phd/aiz218323/scratch/outputs/67-ngame-ep-for-wikiseealso-with-input-concatenation-1-4'
m_teacher = TCH002.from_pretrained(f'{model_output}/teacher', n_data=block.train.dset.n_data, n_lbl=block.n_lbl)

m_teacher.freeze_representations()
m_teacher.init_lbl_embeddings()

# %% ../nbs/88-distillation-for-wikiseealso-with-oak-multi-optimizer.ipynb 19
bsz = max(args.per_device_train_batch_size, args.per_device_eval_batch_size)*torch.cuda.device_count()

m_student = OAK001.from_pretrained('sentence-transformers/msmarco-distilbert-base-v4', batch_size=bsz, num_batch_labels=5000,
                                   margin=0.3, num_negatives=10, tau=0.1, apply_softmax=True,
                                   
                                   data_aug_meta_prefix='lnk2data', lbl2data_aug_meta_prefix=None,
                                   data_pred_meta_prefix=None, lbl2data_pred_meta_prefix=None,
                                   
                                   num_metadata=block.train.dset.meta['lnk_meta'].n_meta, resize_length=5000,
                                   
                                   calib_margin=0.05, calib_num_negatives=10, calib_tau=0.1, calib_apply_softmax=True,
                                   calib_loss_weight=0.1, use_calib_loss=True,
                                   
                                   use_query_loss=True,
                                   
                                   meta_loss_weight=0.0,
                                   
                                   fusion_loss_weight=0.1, use_fusion_loss=False,
                                   
                                   use_encoder_parallel=True)

m_student.init_retrieval_head()
m_student.init_cross_head()

meta_embed_file = '/home/aiscuser/scratch/OGB_Weights/LF-WikiSeeAlsoTitles-320K/emb_weights.npy'
# meta_embeddings = np.load(meta_embed_file)
# m_student.encoder.set_meta_embeddings(torch.tensor(meta_embeddings, dtype=torch.float32))

m_student.encoder.set_meta_embeddings(torch.zeros(block.train.dset.meta['lnk_meta'].n_meta, m_student.config.dim))

# %% ../nbs/88-distillation-for-wikiseealso-with-oak-multi-optimizer.ipynb 21
model = DTL004(DistilBertConfig(), m_student=m_student, m_teacher=m_teacher, bsz=bsz, tn_targ=5000, margin=0.3, tau=0.1, 
               n_negatives=10, apply_softmax=True, teacher_data_student_label_loss_weight=1.0, 
               student_data_teacher_label_loss_weight=1.0, data_mse_loss_weight=0.1, label_mse_loss_weight=0.1)


# %% ../nbs/88-distillation-for-wikiseealso-with-oak-multi-optimizer.ipynb 22
metric = PrecRecl(block.n_lbl, block.test.data_lbl_filterer, prop=block.train.dset.data.data_lbl,
                  pk=10, rk=200, rep_pk=[1, 3, 5, 10], rep_rk=[10, 100, 200])

# %% ../nbs/88-distillation-for-wikiseealso-with-oak-multi-optimizer.ipynb 23
learn = XCLearner(
    model=model, 
    args=args,
    train_dataset=block.train.dset,
    eval_dataset=block.test.dset,
    data_collator=block.collator,
    compute_metrics=metric,
)

# %% ../nbs/88-distillation-for-wikiseealso-with-oak-multi-optimizer.ipynb 26
if __name__ == '__main__':
    mp.freeze_support()
    learn.train()
