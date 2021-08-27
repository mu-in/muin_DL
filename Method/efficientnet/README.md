# Lotte-10000
This repository provides training/evaluation code for Lotte 10,000 class product classification project.

### Maintainers
- Yeongwoo Nam

## Table Of Contents
- [Setup](#setup)
    * [Hardware](#hardware)
    * [Software](#software)
        * [Python3 Library](#python3-library)
    * [Dataset](#dataset)
        * [Split](#split)
- [Getting Started](#getting-started)
- [Training](#training)
- [Inference](#inference)
    * [Pre-trained Model](#pre-trained-model)

## Pre-requisite
The following sections list the requirements for training/evaluation the model.

### Hardware
Tested on:
- **CPU** - 2 x Intel(R) Xeon(R) Silver 4210R CPU @ 2.40GHz  
<img src="/media/CPU.png" width="40%" height="40%">

- **RAM** - 256 GB  
<img src="/media/Memory.png" width="65%" height="65%">

- **GPU** - 8 x GeForce RTX 2080 Ti (11 GB)  
<img src="/media/GPUs.png" width="50%" height="50%">

- **SSD** - Samsung MZ7LH3T8 (3.5 TB)  
<img src="/media/Storage.png" width="50%" height="50%">  
  
Terminal screen capture images are located inside the [media](media) folder.

### Software
Tested on:
- [Ubuntu 18.04](https://ubuntu.com/)  
<img src="/media/OS.png" width="85%" height="85%">

- [Python 3.6](https://www.python.org/) 
- [NVIDIA Driver 440](https://www.nvidia.com/Download/index.aspx)
- [NVIDIA Container Toolkit](https://github.com/NVIDIA/nvidia-docker)

#### Python3 Library
- [PyTorch 1.7.0](https://pytorch.org/)
- [Torchvision 0.8.1](https://pytorch.org/)
- [Timm 0.3.1](https://github.com/rwightman/pytorch-image-models)

See [requirements.txt](requirements.txt) for all python library.

### Dataset
Please keep the structure of the dataset as follows.
#### 📂 Directory Structure
```
Dataset
├── train
|   ├── class1
|   |   ├── image1
|   |   └── image2
|   └── class2
|   |   ├── image1
|   |   └── image2
├── validation          # same structure as train
└── test                # same structure as train
```

#### Dataset Split
Please, refer to the following for the data split list.
- [Train List](dataset/split/train.txt)
- [Validation List](dataset/split/validation.txt)
- [Test List](dataset/split/test.txt)

#### Error List
Please, refer to the following for a list of errors that occurred during the preprocessing process.
- [Error List](dataset/error_log.txt)  
`Image ${idx} crop error` means that there is an error in the ${idx}th bounding box of the .xml file.  
`Image open error` means that there is an error in the .jpg file.

## Getting Started
### Build Docker Image
```
git clone <repo_path>
cd Lotte-10000
docker build -t lotte-10000/classification:1.0.0 ./
```

## Training
### Usage
```bash
# In Lotte-10000 project folder
docker run \
    -v <PATH/TO/CONFIG.yaml>:/root/cfg_path \
    -v <PATH/TO/DATA_FOLDER>:/root/data_root \
    -v <PATH/TO/SAVE_FOLDER>:/root/save_root \
    -v $(pwd):/root/project \
    --ipc=host --gpus=all --rm \
    lotte-10000/classification:1.0.0 \
    python3 /root/project/src/docker_run.py train
```
**Notation**
- `<PATH>` means your `local environment path`. Please change `<PATH>` to the `local path of the file/folder`.
- Please write `<PATH>` in `absolute path`.
- Other options are required to run this project. Please leave it as it is.
- For training base model, use the `Lotte-10000/configs/efficientnet_b0_base.yaml` config file.
- For training ours model, use the `Lotte-10000/configs/efficientnet_b0_ours.yaml` config file.

### Demo Example
```bash
# This is a small dataset (10 class) Demo.
# In Lotte-10000 project folder
docker run \
    -v $(pwd)/demo/config.yaml:/root/cfg_path \
    -v $(pwd)/demo/data_root:/root/data_root \
    -v $(pwd)/demo/save_root:/root/save_root \
    -v $(pwd):/root/project \
    --ipc=host --gpus=all --rm \
    lotte-10000/classification:1.0.0 \
    python3 /root/project/src/docker_run.py train
```

## Inference
### Usage
```bash
# In Lotte-10000 project folder
docker run \
    -v <PATH/TO/CHECKPOINT.pth>:/root/checkpoint_path \
    -v <PATH/TO/DATA_FOLDER>:/root/data_root \
    -v $(pwd):/root/project \
    --ipc=host --gpus=all --rm \
    lotte-10000/classification:1.0.0 \
    python3 /root/project/src/docker_run.py inference
```
**Notation**
- `<PATH>` means your `local environment path`. Please change `<PATH>` to the `local path of the file/folder`.
- Please write `<PATH>` in `absolute path`.
- Other options are required to run this project. Please leave it as it is.
- For inference base model, use the `Lotte-10000/save_root/pretrained/base/checkpoint/best_top1_validation.pth` checkpoint file.
- For inference ours model, use the `Lotte-10000/save_root/pretrained/ours/checkpoint/best_top1_validation.pth` checkpoint file.

### Demo Example
```bash
# This is a small dataset (10 class) Demo.
# In Lotte-10000 project folder
docker run \
    -v $(pwd)/demo/checkpoint.pth:/root/checkpoint_path \
    -v $(pwd)/demo/data_root:/root/data_root \
    -v $(pwd):/root/project \
    --ipc=host --gpus=all --rm \
    lotte-10000/classification:1.0.0 \
    python3 /root/project/src/docker_run.py inference
```
### Pre-trained Model
The pretrained models are in the following directory:
- [Base Model](pretrained/base)
- [Ours Model](pretrained/ours)  
`checkpoint/best_top1_validation.pth` is the saved model.  
`log.log` is the training log.  
`test_log.txt` is the inference log.
