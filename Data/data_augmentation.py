import numpy as np
import cv2
import json
import xmltodict
import glob
import random
import torch
import argparse
import tqdm
from collections import OrderedDict


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

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root_file_path",  type=str, default=None, help="root_path")
    parser.add_argument("--root_anno_path",  type=str, default=None, help="root_path")
    parser.add_argument("--img_save_path",  type=str, default=None, help="img_save_path")
    parser.add_argument("--json_save_path",  type=str, default=None, help="json_save_path")
    parser.add_argument("--resize_ratio",  type=float, default=None, help="args.resize_ratio")
    args = parser.parse_args() 
    return args


if __name__ == '__main__':

    args = get_args()
    annotation_list = []

    file_pathes = glob.glob(args.root_anno_path + '/*/*/*')
    file_list = [file for file in file_pathes if file.endswith("_meta.xml")]

    random.shuffle(file_list) 

    for i in tqdm.tqdm(range(len(file_list))):

        n_objects = random.randrange(5,11) 
        to_paste = np.full((2988, 2988, 3), 200, dtype=np.uint8) # 배경이미지 색 조정

        annotation_dict = OrderedDict()
        categories = list()
        pathes = list()
        resolutions = list()
        boxes = list()

        pre_boxes = torch.zeros(1, 4, dtype = torch.long) 

        for j in range(n_objects): # 이 Loop 구문에서 object 수 만큼 이미지 읽어서 합성 이미지 만드는 듯
            idx = random.randrange(0,len(file_list))
            line = file_list[idx]
            # .xml to .json
            with open(line,'r',encoding='UTF8') as f:
                xmlString = f.read()
            f.close()
            obj_Info = json.loads(json.dumps(xmltodict.parse(xmlString), indent=4))
            
            if 'object' not in obj_Info['comp_cd']['annotation'].keys():
                continue
            elif 'dict' not in str(type(obj_Info['comp_cd']['annotation']['object'])): # 복수 상품이미지 고려 X
                continue
            # to_copy image
            to_copy = cv2.imread(args.root_file_path + '/' + obj_Info['comp_cd']['div_cd']['item_cd'] + '/' + obj_Info['comp_cd']['annotation']['filename'] , cv2.IMREAD_COLOR) 

            imageHeight, imageWidth = to_copy.shape[:2]

            resizeHeight = int(args.resize_ratio * imageHeight)
            resizeWidth = int(args.resize_ratio * imageWidth)

            to_copy_resize = cv2.resize(to_copy, (resizeHeight, resizeWidth), interpolation = cv2.INTER_CUBIC)

            # to_copy_resize image 속 object 별로 진행
            obj = obj_Info['comp_cd']['annotation']['object']

            dict_val_box = obj['bndbox'].values()
            list_box = list(dict_val_box)
            org_box = list(map(int, list_box))
            box = [round(j*args.resize_ratio) for j in org_box] 

            # random offset + IOU -> occlusion 확인
            n_of_trial = 0
            while True:
                ## 랜덤 좌표
                ver = random.randint(0, 2988 - (box[3] - box[1]))
                hor = random.randint(0, 2988 - (box[2] - box[0])) 

                new_box = []
                x_min = hor
                y_min = ver
                x_max = hor + (box[2] - box[0])
                y_max = ver + (box[3] - box[1])
                new_box.append([x_min, y_min, x_max, y_max])

                # overlap 검사 실시
                new_box = torch.tensor(new_box)
                overlap = find_jaccard_overlap(pre_boxes, new_box).view([-1])
                overlap = overlap.tolist()

                check = 1
                for val in overlap: 
                    if val > 0.05: check = 0 
                if check == 1: break # occlusion 발생 X -> while 문 탈출
                
                n_of_trial = n_of_trial + 1
                if n_of_trial >= 10: break 
            if n_of_trial >=10: continue
            
            pre_boxes = torch.cat([pre_boxes, new_box], dim=0)
            
            # image copy & paste
            to_paste[ver:ver+(box[3]-box[1]), hor:hor+(box[2]-box[0])] = \
                                                        to_copy_resize[box[1]:box[3], box[0]:box[2]]

            # to make annotation file
            category = int(obj_Info['comp_cd']['div_cd']['item_cd']) # category
            
            resolution_dict = obj_Info['comp_cd']['annotation']['size'].values() 
            resolution = list(map(int, list(resolution_dict))) # resolution

            categories.append(category)
            resolutions.append(resolution)
            boxes.append([hor, ver,hor+(box[2]-box[0]), ver+(box[3]-box[1])])

        # save final image
        image_path = args.img_save_path + '/img' + str(i+1) + ".jpg"
        cv2.imwrite(image_path, to_paste)

        annotation_dict['categories'] = categories
        annotation_dict['pathes'] = image_path
        annotation_dict['resolutions'] = resolutions
        annotation_dict['boxes'] = boxes

        annotation_list.append(annotation_dict)

        # save final annotation
        with open(args.json_save_path, "w") as f: 
            json.dump(annotation_list, f, indent=2, ensure_ascii=False)
        f.close()
