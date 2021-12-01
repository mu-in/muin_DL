import numpy as np
import os
import cv2
import json
import xmltodict
import glob
import random
import torch
import argparse
import tqdm
from collections import OrderedDict
from multiprocessing import Process

def find_intersection(set_1, set_2):
    lower_bounds = torch.max(set_1[:, :2].unsqueeze(1), set_2[:, :2].unsqueeze(0))
    upper_bounds = torch.min(set_1[:, 2:].unsqueeze(1), set_2[:, 2:].unsqueeze(0))
    intersection_dims = torch.clamp(upper_bounds - lower_bounds, min=0)
    return intersection_dims[:, :, 0] * intersection_dims[:, :, 1]


def find_jaccard_overlap(set_1, set_2):
    intersection = find_intersection(set_1, set_2)
    areas_set_1 = (set_1[:, 2] - set_1[:, 0]) * (set_1[:, 3] - set_1[:, 1])
    areas_set_2 = (set_2[:, 2] - set_2[:, 0]) * (set_2[:, 3] - set_2[:, 1])
    union = areas_set_1.unsqueeze(1) + areas_set_2.unsqueeze(0) - intersection

    return intersection / union


def get_COCO_format_box(box, resolution):
    width = box[2] - box[0]
    height = box[3] - box[1]
    center_x = (box[2] + box[0]) / 2
    center_y = (box[1] + box[3]) / 2

    return [center_x / resolution[0], center_y / resolution[1], width / resolution[0], height / resolution[1]]


def extract_edge_image(image): # to make edge detection image

    img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    Ix = cv2.Sobel(img, ddepth=cv2.CV_64F, dx=1, dy=0, ksize=3)  # x 방향 계산
    Iy = cv2.Sobel(img, ddepth=cv2.CV_64F, dx=0, dy=1, ksize=3)  # y 방향 계산
    mag = np.sqrt(np.square(Ix) + np.square(Iy))  # Gradient의 magnitude 계산

    # 정규화 후 최종 edge image 생성
    mag_ = (mag - mag.min()) / (mag.max() - mag.min()) * 255
    result = np.zeros(img.shape)
    id = np.where(mag_ > 20)
    result[id] = 255

    return result

def make_noise_bcg(to_paste, bcg_pathes): # to make noise bcg
    rand_idx = random.randint(0,len(bcg_pathes)-1) # randomly select among noise bcgs
    noise_bcg = cv2.imread(bcg_pathes[rand_idx])

    fill_idx = to_paste == [255,255,255] # 흰색인 영역의 인덱스 추출
    to_paste[fill_idx] = noise_bcg[fill_idx]
    to_paste = cv2.medianBlur(to_paste, 13) # 경계 제거를 위한 중간값 필터

    return to_paste

def rotate_img_45n(img):
    # 45도, 135도, 225도, 315도 중 하나로 회전
    rows,cols,_ = img.shape
    M = cv2.getRotationMatrix2D((cols/2,rows/2), random.choice([45, 135, 225, 315]), 0.7)
    rot_img = cv2.warpAffine(img,M,(cols,rows))
    # 검정으로 바뀐 영역 다시 흰색으로
    idx = rot_img == [0, 0, 0]
    rot_img[idx] = 255

    return rot_img 
    
def CoPy_and_Paste(file_list, args, index):
    n_objects = random.randrange(5, 11)
    to_paste = np.full((2988, 2988, 3), 255, dtype=np.uint8)  # 배경이미지 검정

    bcg_pathes = glob.glob(args.bcg_path + '/*.jpg') # noise background image path

    categories = list()
    resolutions = list()
    boxes = list()

    pre_boxes = torch.zeros(1, 4, dtype=torch.long)

    for j in range(n_objects):
        idx = random.randrange(0, len(file_list))
        line = file_list[idx]
        # .xml to .json
        with open(line, 'r', encoding='UTF8') as f:
            xmlString = f.read()
        f.close()

        obj_Info = json.loads(json.dumps(xmltodict.parse(xmlString), indent=4))

        if 'object' not in obj_Info['comp_cd']['annotation'].keys():
            continue
        elif 'dict' not in str(type(obj_Info['comp_cd']['annotation']['object'])):  # 복수 상품이미지 고려 X
            continue
        elif int(list(obj_Info['comp_cd']['annotation']['size'].values())[0]) != 2988:
            continue
        elif os.path.isfile(os.path.join(args.root_path, 'img', obj_Info['comp_cd']['div_cd']['item_cd'],
                                         obj_Info['comp_cd']['annotation']['filename'])) == False:
            continue
        # to_copy image
        to_copy = cv2.imread(os.path.join(args.root_path, 'img', obj_Info['comp_cd']['div_cd']['item_cd'],
                                          obj_Info['comp_cd']['annotation']['filename']), cv2.IMREAD_COLOR)
        if args.extract_edge == 1:  ## 추가
            to_copy = extract_edge_image(to_copy)
        
        if args.rotate_img == 1: ## 추가
            if random.randint(0,100) <= 50: # 40% 확률로 rotate
                to_copy = rotate_img_45n(to_copy)

        imageHeight, imageWidth = to_copy.shape[:2]

        resizeHeight = int(args.resize_ratio * imageHeight)
        resizeWidth = int(args.resize_ratio * imageWidth)

        to_copy_resize = cv2.resize(to_copy, (resizeHeight, resizeWidth), interpolation=cv2.INTER_CUBIC)

        # to_copy_resize image 속 object 별로 진행
        obj = obj_Info['comp_cd']['annotation']['object']

        dict_val_box = obj['bndbox'].values()
        list_box = list(dict_val_box)
        org_box = list(map(int, list_box))
        box = [round(j * args.resize_ratio) for j in org_box]

        # random offset + IOU -> occlusion 확인
        n_of_trial = 0
        while True:
            ## 랜덤 좌표
            ver = random.randint(0, 2988 - (box[3] - box[1]))
            hor = random.randint(0, 2988 - (box[2] - box[0]))

            new_box = []
            x_min, y_min, x_max, y_max = hor, ver, hor + (box[2] - box[0]), ver + (box[3] - box[1])
            new_box.append([x_min, y_min, x_max, y_max])

            # overlap 검사 실시
            new_box = torch.tensor(new_box)
            overlap = find_jaccard_overlap(pre_boxes, new_box).view([-1])
            overlap = overlap.tolist()

            check = 1
            for val in overlap:
                if val > 0.05: check = 0
            if check == 1: break  # occlusion 발생 X -> while 문 탈출

            n_of_trial = n_of_trial + 1
            if n_of_trial >= 10: break
        if n_of_trial >= 10: continue

        pre_boxes = torch.cat([pre_boxes, new_box], dim=0)

        # image copy & paste
        to_paste[ver:ver + (box[3] - box[1]), hor:hor + (box[2] - box[0])] = to_copy_resize[box[1]:box[3],
                                                                             box[0]:box[2]]

        # to make annotation file
        category = int(obj_Info['comp_cd']['div_cd']['item_cd'])  # category

        resolution_dict = obj_Info['comp_cd']['annotation']['size'].values()
        resolution = list(map(int, list(resolution_dict)))  # resolution

        categories.append(category)
        resolutions.append(resolution)
        boxes.append([hor, ver, hor + (box[2] - box[0]), ver + (box[3] - box[1])])

    # save final image
    image_path = os.path.join(args.save_path, 'img', f"img_{index}.jpg")
    make_noise_bcg(to_paste, bcg_pathes) ## make_noise_bcg
    cv2.imwrite(image_path, to_paste)

    f = open(os.path.join(args.save_path, 'annotation', f"img_{index}.txt"), 'w')
    for category, box, resolution in zip(categories, boxes, resolutions):
        box = get_COCO_format_box(box, resolution)
        f.write(str(0) + ' ')  # class는 object 하나로 통일
        f.write(str(box[0]) + ' ')
        f.write(str(box[1]) + ' ')
        f.write(str(box[2]) + ' ')
        f.write(str(box[3]) + '\n')
    f.close()


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root_path", type=str, default=None, help="root_path")
    parser.add_argument("--save_path", type=str, default=None, help="img_save_path")
    parser.add_argument("--resize_ratio", type=float, default=None, help="args.resize_ratio")
    parser.add_argument("--data_num", type=int, default=None, help="args.data_number")
    parser.add_argument("--num_process", type=int, default=None, help="args.data_number")
    parser.add_argument("--extract_edge", type=int, default=None, help="args.extract_edge")
    parser.add_argument("--rotate_img", type=int, default=None, help="args.rotate_img")
    parser.add_argument("--bcg_path", type=str, default=None, help="bcg_path")

    args = parser.parse_args()
    return args


if __name__ == '__main__':

    args = get_args()
    annotation_list = []

    file_pathes = glob.glob(os.path.join(args.root_path, 'annotation') + '/*/*')
    file_list = [file for file in file_pathes if file.endswith("_meta.xml")]

    random.shuffle(file_list)
    procs = []

    # 멀티 프로세싱 처리
    for i in tqdm.tqdm(range(0, args.data_num, args.num_process)):
        for number in range(i, (i + args.num_process)):
            proc = Process(target=CoPy_and_Paste, args=(file_list, args, number,))
            procs.append(proc)
            proc.start()
        for proc in procs:
            proc.join()
