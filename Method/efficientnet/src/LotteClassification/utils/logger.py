import os
import time
from datetime import datetime
from pytz import timezone

from timm.utils import AverageMeter


class Logger:
    def __init__(self, log_dir, file_name, is_print=True, exist_ok=True):
        self.log_path = os.path.join(log_dir, file_name)
        self.is_print = is_print
        self.prev_time = time.time()
        self.time_m = AverageMeter()

        if not exist_ok:
            assert not os.path.exists(self.log_path)

    def write(self, log, end='\n'):
        log = self.make_time_log(log)
        if self.is_print:
            print(log, end=end)
        with open(self.log_path, 'a') as f:
            f.write(log + end)

    def write_epoch(self, cur_epoch, total_epoch):
        self.time_m.update(time.time() - self.prev_time)
        time_per_epoch = sec_to_time(self.time_m.avg)
        total_eta = sec_to_time(self.time_m.avg * (total_epoch - cur_epoch - 1))

        self.write('Epoch %d/%d Complete | time per epoch: %s | total eta: %s' %
                   (cur_epoch, total_epoch, time_per_epoch, total_eta))
        self.prev_time = time.time()

    @staticmethod
    def make_time_log(log):
        fmt = "%Y-%m-%d %H:%M:%S %Z%z"
        kst_time = datetime.now(timezone('Asia/Seoul')).strftime(fmt)
        time_log = '%s: %s' % (kst_time, log)

        return time_log


def sec_to_time(sec):
    sec = int(sec)
    hour = sec // 3600
    min = (sec - (hour * 3600)) // 60
    sec = sec - (hour * 3600) - (min * 60)

    return '%d:%d:%d' % (hour, min, sec)
