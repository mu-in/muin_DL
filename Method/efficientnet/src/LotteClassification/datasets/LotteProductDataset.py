import os
import torch.utils.data as data
from PIL import Image


class LotteProductDataset(data.Dataset):
    def __init__(self, root, partition, pre_transform=None, transform=None, target_transform=None, train_label=None,
                 with_idx=False):
        self.root = root
        self.partition = partition
        self.pre_transform = pre_transform
        self.transform = transform
        self.target_transform = target_transform
        self.with_idx = with_idx

        class_list = sorted(os.listdir(os.path.join(self.root, self.partition)))
        self.name_to_label = {}
        self.label_to_name = {}
        self.images = []
        self.labels = []
        if train_label is not None:
            self.name_to_label = {train_label[key]: key for key in train_label.keys()}
            self.label_to_name = train_label
            for name in class_list:
                if name not in self.name_to_label.keys():
                    continue
                cur_img_list = os.listdir(os.path.join(os.path.join(self.root, self.partition, name)))
                cur_img_list = [os.path.join(self.root, self.partition, name, img) for img in cur_img_list]
                cur_label_list = [self.name_to_label[name] for _ in cur_img_list]
                self.images = self.images + cur_img_list
                self.labels = self.labels + cur_label_list
        else:
            for label, name in enumerate(class_list):
                self.name_to_label[name] = label
                self.label_to_name[label] = name
                cur_img_list = os.listdir(os.path.join(os.path.join(self.root, self.partition, name)))
                cur_img_list = [os.path.join(self.root, self.partition, name, img) for img in cur_img_list]
                cur_label_list = [label for _ in cur_img_list]
                self.images = self.images + cur_img_list
                self.labels = self.labels + cur_label_list

    def __getitem__(self, idx):
        image = Image.open(self.images[idx]).convert('RGB')

        if self.pre_transform is not None:
            image = self.pre_transform(image)

        if self.transform is not None:
            image = self.transform(image)

        label = self.labels[idx]
        if self.target_transform is not None:
            label = self.target_transform(label)

        if self.with_idx:
            return image, (label, idx)
        return image, label

    def __len__(self):
        return len(self.images)
