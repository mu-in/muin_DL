# -*- coding: utf-8 -*-
from xml.etree.ElementTree import parse
from collections import OrderedDict
import tqdm
import json
import os

def parse_info(root_dir , split , save_root ): # 필요한 annotation 정보 추출

    root_dir = root_dir + split
   
    data_distribution = dict()
    Total_annotation = list()
   
    for item in tqdm.tqdm(os.listdir(root_dir)): # item 별로 (과자 , 음료 , 유제품 ..)
        data_distribution[item] = len(os.listdir(root_dir + '/' + item)) 
        for i , product in enumerate(os.listdir(root_dir + '/' + item)): # 하나의 item에 속하는 종류 만큼(과자 중에서 무슨 과자 인지)
            for ann in os.listdir(root_dir + '/' + item + '/' + product):# (포카칩에 대한 여러장의 사진들 )
                if 'meta' in ann:
                    tree = parse(root_dir + '/' + item + '/' + product + '/' + ann)
                    root = tree.getroot()

                    for neighbor in root.iter('div_cd'):
                        name = neighbor.findtext('item_cd')

                    for neighbor in root.iter('annotation'):
                        path = neighbor.findtext('path')
                        path = '/data3/taekguen/dataset/' + split + '/' + name + '/' + path.split('/')[7]

                    for neighbor in root.iter('size'):
                        resolution = [int(neighbor.findtext('width')), int(neighbor.findtext('height')), int(neighbor.findtext('depth'))]

                    objects = list()
                    for neighbor in root.iter('bndbox'):
                        objects.append([int(neighbor.findtext('xmin')),int(neighbor.findtext('ymin')),int(neighbor.findtext('xmax')),int(neighbor.findtext('ymax'))])

                    information=OrderedDict()
                    information["category"] = name
                    information["image_path"] = path
                    information["resolution"] = resolution
                    information["bbox"] = objects

                    Total_annotation.append(information)

                else : continue


    for key in data_distribution.keys():
        print("종류 : {} , 상품 갯수 : {}".format(key,data_distribution[key]))

    print("전체 데이터 갯수({}) : {} ".format(split , len(Total_annotation)))
    with open(save_root + split + '_annotation.json','w',encoding="utf-8") as n:
      json.dump(Total_annotation,n,ensure_ascii=False,indent="\t")

def mapping_to_item_cd(anno_dir , target_dir): # item_cd 로 폴더 이름 바꿔주기
   
    for item in tqdm.tqdm(os.listdir(anno_dir)): 
        for product in os.listdir(anno_dir + item): 
            for ann in os.listdir(anno_dir + '/' + item + '/' + product):
                if 'meta' in ann:
                    tree = parse(anno_dir + '/' + item + '/' + product + '/' + ann)
                    root = tree.getroot()
                    for neighbor in root.iter('div_cd'):
                        name = neighbor.findtext('item_cd')
                    break
                else : continue
            os.rename(target_dir + product , target_dir + name)
            print("{} : {}".format(product,name))


if __name__ =='__main__':

    #parse_info(root_dir = '/home/gtlim/workspace/Muin_Term_Project/dataset/' , split = 'Validation' , save_root = './')
    #parse_info(root_dir = '/home/gtlim/workspace/Muin_Term_Project/dataset/' , split = 'Training' , save_root = './' )

    #mapping_to_item_cd(anno_dir = '/home/gtlim/workspace/Muin_Term_Project/dataset/Validation/' ,target_dir = '/data3/taekguen/dataset/Validation/')
