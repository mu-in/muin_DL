from yacs.config import CfgNode as CN

_C = CN()

_C.system = CN()
_C.system.save_step = 5

_C.model = CN()
_C.model.model_name = 'efficientnet_b0'
_C.model.pretrained = True
_C.model.num_classes = 9927
_C.model.drop_rate = 0.2
_C.model.drop_path = 0.2

_C.dataset = CN()
_C.dataset.pre_transform = True
_C.dataset.scale = (0.6, 1.0)
_C.dataset.batch_size = 768
_C.dataset.reprob = 0.2
_C.dataset.remode = 'pixel'
_C.dataset.aa = 'rand-m9-mstd0.5'
_C.dataset.train_interpolation = 'random'
_C.dataset.workers = 16

_C.optimizer = CN()
_C.optimizer.opt = 'rmsproptf'
_C.optimizer.lr = .048
_C.optimizer.opt_eps = .001
_C.optimizer.momentum = 0.9
_C.optimizer.weight_decay = 1e-5

_C.scheduler = CN()
_C.scheduler.sched = 'step'
_C.scheduler.epochs = 50
_C.scheduler.decay_epochs = 2.4
_C.scheduler.decay_rate = .97
_C.scheduler.warmup_lr = 1e-6
_C.scheduler.warmup_epochs = 3


def get_cfg_defaults():
    return _C.clone()
