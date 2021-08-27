import torch.nn as nn
from torch.cuda.amp import autocast

from timm.models import create_model


class LotteNet(nn.Module):
    def __init__(self, cfg):
        super(LotteNet, self).__init__()
        self.model = create_model(
            model_name=cfg.model.model_name,
            pretrained=cfg.model.pretrained,
            num_classes=cfg.model.num_classes,
            drop_rate=cfg.model.drop_rate,
            drop_path_rate=cfg.model.drop_path,
        )

    @autocast()
    def forward(self, x):
        output = self.model(x)
        return output
