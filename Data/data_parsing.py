# -*- coding: utf-8 -*-
from xml.etree.ElementTree import parse
from collections import OrderedDict
import tqdm
import json
import os

def parse_info(root_dir , split , save_root):
  
    root_dir = root_dir + '/' + split
    Total_annotation = list()
    for item in tqdm.tqdm(os.listdir(root_dir)):
        for product in os.listdir(root_dir + '/' + item):
            for ann in os.listdir(root_dir + '/' + item + '/' + product):
                if 'meta' in ann:
                    tree = parse(root_dir + '/' + item + '/' + product + '/' + ann)
                    root = tree.getroot()

                    for neighbor in root.iter('div_cd'):
                        name = neighbor.findtext('img_prod_nm')

                    for neighbor in root.iter('annotation'):
                        path = neighbor.findtext('path')

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

    with open(save_root + split + '_annotation.json','w',encoding="utf-8") as n:
      json.dump(Total_annotation,n,ensure_ascii=False,indent="\t")


if __name__ =='__main__':
    parse_info(root_dir = '/home/gtlim/workspace/Sejong_Term_Project/dataset/label' , split = 'Validation' , save_root = './')