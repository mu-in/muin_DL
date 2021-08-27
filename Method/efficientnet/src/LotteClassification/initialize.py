import torch.nn as nn

from .models import LotteNet
from timm.optim import create_optimizer
from timm.scheduler import create_scheduler
from .utils.config import get_cfg_defaults


def init_cfg(cfg_path=None):
    cfg = get_cfg_defaults()
    if cfg_path is not None:
        cfg.merge_from_file(cfg_path)
    cfg.freeze()

    return cfg


def init_model(cfg, device):
    model = LotteNet(cfg)

    if device == 'cuda':
        model = model.cuda()
        model = nn.DataParallel(model)

    return model


def init_optimizer(cfg, model):
    optimizer = create_optimizer(cfg.optimizer, model)

    return optimizer


def init_scheduler(cfg, optimizer):
    scheduler = create_scheduler(cfg.scheduler, optimizer)

    return scheduler
