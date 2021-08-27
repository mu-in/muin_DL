import torch
import torch.backends.cudnn
import random
import numpy as np

import argparse
import LotteClassification

CONFIG_PATH = '/root/cfg_path'
CHECKPOINT_PATH = '/root/checkpoint_path'
IMAGE_PATH = '/root/image_path'
DATA_ROOT = '/root/data_root'
SAVE_ROOT = '/root/save_root'

run_parser = argparse.ArgumentParser()
run_parser.add_argument('type', type=str, choices=['train', 'inference'])
run_parser.add_argument('--random_seed', type=int, default=4)
run_args = run_parser.parse_args()

torch.manual_seed(run_args.random_seed)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False
np.random.seed(run_args.random_seed)
random.seed(run_args.random_seed)

if run_args.type == 'train':
    lotte_classification = LotteClassification.LotteClassification()
    lotte_classification.init_from_cfg(cfg_path=CONFIG_PATH, device='cuda')

    lotte_classification.train(save_root=SAVE_ROOT, data_root=DATA_ROOT)
elif run_args.type == 'inference':
    lotte_classification = LotteClassification.LotteClassification()
    lotte_classification.load_checkpoint(checkpoint_path=CHECKPOINT_PATH, device='cuda')

    lotte_classification.inference(data_root=DATA_ROOT)
else:
    raise NotImplementedError
