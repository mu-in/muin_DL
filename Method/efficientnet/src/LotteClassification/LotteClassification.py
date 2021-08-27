import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torch.cuda.amp import GradScaler, autocast
from torch.utils.tensorboard import SummaryWriter

from timm.data import resolve_data_config, create_loader
from timm.utils import AverageMeter, accuracy

import os
from tqdm import tqdm
from collections import OrderedDict

from . import initialize
from .utils import Logger
from .datasets import LotteProductDataset as LPD


class LotteClassification:
    def __init__(self):
        self.cfg = None
        self.device = None
        self.model = None
        self.scaler = GradScaler()
        self.optimizer = None
        self.scheduler = None
        self.data_config = None
        self.num_epochs = None
        self.label_to_name = None
        self.pre_transform = None

    def init_from_cfg(self, cfg_path=None, device='cuda'):
        assert device in ['cpu', 'cuda']

        # Init Config File
        self.cfg = initialize.init_cfg(cfg_path=cfg_path)
        self._init_from_cfg(self.cfg, device)

    def _init_from_cfg(self, cfg, device):
        self.device = device

        # Init Model
        self.model = initialize.init_model(cfg=cfg,
                                           device=device)

        # Init Optimizer
        self.optimizer = initialize.init_optimizer(cfg=cfg,
                                                   model=self.model)

        # Init Scheduler
        self.scheduler, self.num_epochs = initialize.init_scheduler(cfg=cfg,
                                                                    optimizer=self.optimizer)

        self.data_config = resolve_data_config(dict(cfg.dataset), model=self.model)
        self.pre_transform = transforms.Resize((256, 256)) if cfg.dataset.pre_transform else None

    def train(self, save_root, data_root):
        os.makedirs(os.path.join(save_root, 'checkpoint'))

        best_top1_validation_accuracy = 0.0
        best_top5_validation_accuracy = 0.0

        logger = Logger(log_dir=save_root, file_name='log.log')
        tensor_log = SummaryWriter(log_dir=save_root)

        train_set = LPD(root=data_root, partition='train',
                        pre_transform=self.pre_transform)
        train_loader = create_loader(train_set,
                                     input_size=self.data_config['input_size'],
                                     batch_size=self.cfg.dataset.batch_size,
                                     is_training=True,
                                     scale=self.cfg.dataset.scale,
                                     re_prob=self.cfg.dataset.reprob,
                                     re_mode=self.cfg.dataset.remode,
                                     auto_augment=self.cfg.dataset.aa,
                                     interpolation=self.cfg.dataset.train_interpolation,
                                     mean=self.data_config['mean'],
                                     std=self.data_config['std'],
                                     num_workers=self.cfg.dataset.workers)
        self.label_to_name = train_set.label_to_name

        validation_set = LPD(root=data_root, partition='validation', train_label=self.label_to_name,
                             pre_transform=self.pre_transform)
        validation_loader = create_loader(validation_set,
                                          input_size=self.data_config['input_size'],
                                          batch_size=self.cfg.dataset.batch_size,
                                          is_training=False,
                                          interpolation=self.data_config['interpolation'],
                                          mean=self.data_config['mean'],
                                          std=self.data_config['std'],
                                          num_workers=self.cfg.dataset.workers)

        # Train Full Epochs
        validation_step = 1
        for epoch in range(self.num_epochs):
            # Train
            train_metrics = self._train_one_epoch(data_loader=train_loader)
            self.scheduler.step(epoch + 1)

            # Log
            logger.write_epoch(epoch, self.num_epochs)
            logger.write('Train Loss: %.4lf | Train Top1 Accuracy: %.4lf | Train Top5 Accuracy: %.4lf' %
                         (train_metrics['loss'], train_metrics['top1'], train_metrics['top5']))

            tensor_log.add_scalar('Train/Loss', train_metrics['loss'], epoch)
            tensor_log.add_scalar('Train/Top1', train_metrics['top1'], epoch)
            tensor_log.add_scalar('Train/Top5', train_metrics['top5'], epoch)

            # Validation
            validation_metrics = self._inference(data_loader=validation_loader)

            # Log
            logger.write('Validation Loss: %.4lf | Validation Top1 Accuracy: %.4lf | Validation Top5 Accuracy: %.4lf' %
                         (validation_metrics['loss'], validation_metrics['top1'], validation_metrics['top5']))

            tensor_log.add_scalar('Validation/Loss', validation_metrics['loss'], epoch)
            tensor_log.add_scalar('Validation/Top1', validation_metrics['top1'], epoch)
            tensor_log.add_scalar('Validation/Top5', validation_metrics['top5'], epoch)

            # Save Checkpoints
            if epoch % self.cfg.system.save_step == 0:
                self.save_checkpoint(checkpoint_path=os.path.join(save_root, 'checkpoint', '%d.pth' % epoch))
            self.save_checkpoint(checkpoint_path=os.path.join(save_root, 'checkpoint', 'final.pth'))

            if best_top1_validation_accuracy < validation_metrics['top1']:
                best_top1_validation_accuracy = validation_metrics['top1']
                self.save_checkpoint(checkpoint_path=os.path.join(save_root, 'checkpoint', 'best_top1_validation.pth'))
            if best_top5_validation_accuracy < validation_metrics['top5']:
                best_top5_validation_accuracy = validation_metrics['top5']
                self.save_checkpoint(checkpoint_path=os.path.join(save_root, 'checkpoint', 'best_top5_validation.pth'))

        test_set = LPD(root=data_root, partition='test', train_label=self.label_to_name,
                       pre_transform=self.pre_transform)
        test_loader = create_loader(test_set,
                                    input_size=self.data_config['input_size'],
                                    batch_size=self.cfg.dataset.batch_size,
                                    is_training=False,
                                    interpolation=self.data_config['interpolation'],
                                    mean=self.data_config['mean'],
                                    std=self.data_config['std'],
                                    num_workers=self.cfg.dataset.workers)
        for checkpoint in ['best_top1_validation.pth', 'best_top5_validation.pth', 'final.pth']:
            self.load_checkpoint(checkpoint_path=os.path.join(save_root, 'checkpoint', checkpoint), device=self.device)
            test_metrics = self._inference(data_loader=test_loader)

            logger.write('Test Loss: %.4lf | Test Top1 Accuracy: %.4lf | Test Top5 Accuracy: %.4lf' %
                         (test_metrics['loss'], test_metrics['top1'], test_metrics['top5']))

    def _train_one_epoch(self, data_loader):
        losses_m = AverageMeter()
        top1_m = AverageMeter()
        top5_m = AverageMeter()

        loss_function = nn.CrossEntropyLoss()

        self.model.train()

        for data in tqdm(data_loader):
            input = data[0].to(self.device)
            target = data[1].to(self.device)

            self.optimizer.zero_grad()

            with autocast():
                output = self.model(input)
                loss = loss_function(output, target)

            self.scaler.scale(loss).backward()
            self.scaler.step(self.optimizer)
            self.scaler.update()

            torch.cuda.synchronize()

            with torch.no_grad():
                acc1, acc5 = accuracy(output, target, topk=(1, 5))

            losses_m.update(loss.item(), input.size(0))
            top1_m.update(acc1.item(), output.size(0))
            top5_m.update(acc5.item(), output.size(0))

        metrics = OrderedDict([('loss', losses_m.avg), ('top1', top1_m.avg), ('top5', top5_m.avg)])
        return metrics

    def inference(self, data_root):
        test_set = LPD(root=data_root, partition='test', train_label=self.label_to_name,
                       pre_transform=self.pre_transform, with_idx=True)
        test_loader = create_loader(test_set,
                                    input_size=self.data_config['input_size'],
                                    batch_size=self.cfg.dataset.batch_size,
                                    is_training=False,
                                    interpolation=self.data_config['interpolation'],
                                    mean=self.data_config['mean'],
                                    std=self.data_config['std'],
                                    num_workers=self.cfg.dataset.workers)

        test_results = self._inference(data_loader=test_loader, individually=True)
        sample_cnt = 0
        correct_cnt = 0
        incorrect_cnt = 0
        for individual_result in test_results['individual_results']:
            print(Logger.make_time_log(
                '%s: %s' % (individual_result[0], 'correct' if individual_result[1] else 'incorrect')))
            sample_cnt += 1
            if individual_result[1]:
                correct_cnt += 1
            else:
                incorrect_cnt += 1
        print(Logger.make_time_log('Test Loss: %.4lf | Test Top1 Accuracy: %.4lf | Test Top5 Accuracy: %.4lf' %
                                   (test_results['loss'], (100 * correct_cnt) / sample_cnt, test_results['top5'])))
        print(Logger.make_time_log('Total Test Sample: %d | Correct Sample: %d | Incorrect Sample: %d' %
                                   (sample_cnt, correct_cnt, incorrect_cnt)))

    def _inference(self, data_loader, individually=False):
        losses_m = AverageMeter()
        top1_m = AverageMeter()
        top5_m = AverageMeter()
        individual_results = [] if individually else None

        loss_function = nn.CrossEntropyLoss()

        self.model.eval()

        with torch.no_grad():
            for data in tqdm(data_loader):
                input = data[0].to(self.device)
                if individually:
                    target = data[1][:, 0].to(self.device)
                    data_idx = data[1][:, 1]
                else:
                    target = data[1].to(self.device)

                with autocast():
                    output = self.model(input)
                    loss = loss_function(output, target)

                acc1, acc5 = accuracy(output, target, topk=(1, 5))

                losses_m.update(loss.item(), input.size(0))
                top1_m.update(acc1.item(), output.size(0))
                top5_m.update(acc5.item(), output.size(0))

                if individually:
                    pred = output.max(1)[1]
                    correct_idx = (pred == target)
                    batch_individual_test = [(data_loader.dataset.images[data_idx[idx]], correct_idx[idx].item())
                                             for idx in range(data_idx.size(0))]
                    individual_results += batch_individual_test

        metrics = OrderedDict([('loss', losses_m.avg), ('top1', top1_m.avg), ('top5', top5_m.avg),
                               ('individual_results', individual_results)])
        return metrics

    def save_checkpoint(self, checkpoint_path):
        checkpoint = {
            'cfg': self.cfg,
            'model': self.model.module.state_dict(),
            'optimizer': self.optimizer.state_dict(),
            'scheduler': self.scheduler.state_dict(),
            'scaler': self.scaler.state_dict(),
            'num_epochs': self.num_epochs,
            'label_to_name': self.label_to_name,
        }

        torch.save(checkpoint, checkpoint_path)

    def load_checkpoint(self, checkpoint_path, device='cuda'):
        checkpoint = torch.load(checkpoint_path)

        self.cfg = checkpoint['cfg']
        self._init_from_cfg(self.cfg, device)

        self.model.module.load_state_dict(checkpoint['model'])
        self.optimizer.load_state_dict(checkpoint['optimizer'])
        self.scheduler.load_state_dict(checkpoint['scheduler'])
        self.scaler.load_state_dict(checkpoint['scaler'])
        self.num_epochs = checkpoint['num_epochs']
        self.label_to_name = checkpoint['label_to_name']
