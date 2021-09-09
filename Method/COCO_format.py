import json
import argparse

def get_COCO_format_box(box , resolution):

    width = box[2] - box[0]
    height = box[3] - box[1]
    center_x = (box[2] + box[0]) / 2
    center_y = (box[1] + box[3]) /2 

    return [center_x / resolution[0] , center_y / resolution[1], width / resolution[0] , height / resolution[1]]

    
def get_parser():
    parser = argparse.ArgumentParser(description='Annotation Transform for COCO.')
    parser.add_argument('--path_to_json', type=str, required=True, help='path_to_annotation_json')
    parser.add_argument('--dir_to_save_txt', type=str, required=True, help='dir_to_save_txt')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = get_parser()
    with open(args.path_to_json,'r') as f:
        annotation = json.load(f)
    
    for anno in annotation:
        name = anno['pathes'].split('/')[-1].split('.')[0]
        f = open('/home/gtlim/workspace/Muin_Term_Project/yolov5/datasets/labels/' + name + '.txt' , 'w')
        for box , resolution in zip(anno['boxes'],anno['resolutions']):
            box = get_COCO_format_box(box,resolution)
            f.write('0 ') # class는 object 하나로 통일
            f.write(str(box[1])+' ')
            f.write(str(box[1])+' ')
            f.write(str(box[2])+' ')
            f.write(str(box[3])+'\n')
        f.close()
