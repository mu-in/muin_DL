import json
import cv2
import tqdm
import argparse

def make_cropped_image(json_path):

    with open(json_path, 'r') as f:
        json_data = json.load(f)
        for i in tqdm.tqdm(range(len(json_data))):
            if len(json_data[i]['bbox']) == 0:
                continue
            img = cv2.imread(json_data[i]['image_path'],cv2.IMREAD_COLOR)
            x_min = json_data[i]['bbox'][0][0]
            x_max = json_data[i]['bbox'][0][2]
            y_min = json_data[i]['bbox'][0][1]
            y_max = json_data[i]['bbox'][0][3]
            cropped_img = img[y_min:y_max,x_min:x_max,:].copy()
            save_path = json_data[i]['image_path'].replace('Validation','Validation(cropped)')
            cv2.imwrite(save_path,cropped_img)

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json_path",  type=str, default=None, help="json_path")
    args = parser.parse_args() 
    return args

if __name__ =='__main__':

    args = get_args()

    make_cropped_image(json_path=args.json_path)
