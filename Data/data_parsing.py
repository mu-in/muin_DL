import xmltodict
import tqdm
import os
import cv2
import json
import argparse

# 1. annotation 파일이 있는 지
# 2. object를 담은 사진인지
# 3. 사진의 크기가 2988이 맞는지
# 4. 사진이 정상적으로 읽히는 지
# 5. object가 하나인지 여러개인지

def make_cropped_image(root_dir , target_dir): 
   
    for split in tqdm.tqdm(os.listdir(root_dir)): 
        if split =='Validation':
            continue
        for item in tqdm.tqdm(os.listdir(os.path.join(root_dir,split,'annotation'))):
            if os.path.isdir(os.path.join(target_dir,split,item)) != True:
                os.mkdir(os.path.join(target_dir,split,item))
            for ann in os.listdir(os.path.join(root_dir,split,'annotation',item)):
                if 'meta' in ann:
                    with open(os.path.join(root_dir,split,'annotation',item,ann),'r',encoding='UTF8') as f:
                        xmlString = f.read()
                    obj_Info = json.loads(json.dumps(xmltodict.parse(xmlString), indent=4))

                    if 'object' not in obj_Info['comp_cd']['annotation'].keys(): 
                        continue
                    if int(list(obj_Info['comp_cd']['annotation']['size'].values())[0]) != 2988:
                        continue

                    file_name = obj_Info['comp_cd']['annotation']['filename']

                    if type(obj_Info['comp_cd']['annotation']['object']) == list:
                        bbox = obj_Info['comp_cd']['annotation']['object'][0]
                    else : bbox = obj_Info['comp_cd']['annotation']['object']

                    if os.path.isfile(os.path.join(root_dir,split,'img',item,file_name)) == False:
                        continue
                    img = cv2.imread(os.path.join(root_dir,split,'img',item,file_name))
                    
                    x_min = int(bbox['bndbox']['xmin'])
                    x_max = int(bbox['bndbox']['xmax'])
                    y_min = int(bbox['bndbox']['ymin'])
                    y_max = int(bbox['bndbox']['ymax'])

                    cropped_img = img[y_min:y_max,x_min:x_max,:].copy()

                    cv2.imwrite(os.path.join(target_dir,split,item,file_name),cropped_img)
                    f.close()

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root_dir",  type=str, default=None, help="root_dir")
    parser.add_argument("--target_dir",  type=str, default=None, help="target_dir")
    args = parser.parse_args() 
    return args


if __name__ =='__main__':

    args = get_args()
    make_cropped_image(args.root_dir,args.target_dir)
 