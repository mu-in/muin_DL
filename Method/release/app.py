import io
import base64
import json
import numpy as np
import torch
import torch.nn as nn
import torchvision.transforms as transforms
import cv2
import PIL

from PIL import Image
from flask import Flask, jsonify, request
from torch.cuda.amp import autocast
from timm.models import create_model

from pathlib import Path
from models.common import Conv
from utils.datasets import LoadImages, LoadStreams
from utils.general import non_max_suppression , scale_coords
from utils.augmentations import letterbox
from utils.plots import Annotator, colors

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
device = 'device'

checkpoint_path = 'requirement/best_top1_validation.pth'
imagenet_class_index = json.load(open('requirement/index_to_name.json'))
checkpoint = torch.load(checkpoint_path)

class LotteNet(nn.Module):
    def __init__(self, cfg):
        super(LotteNet, self).__init__()
        self.model = create_model(
            model_name=cfg.model.model_name,
            pretrained=cfg.model.pretrained,
            num_classes=cfg.model.num_classes,
            drop_rate=cfg.model.drop_rate,
            drop_path_rate=cfg.model.drop_path,
        )

    @autocast()
    def forward(self, x):
        output = self.model(x)
        return output

def init_model(cfg, device):
    model = LotteNet(cfg)

    if device == 'cuda':
        model = model.cuda()
        model = nn.DataParallel(model)

    return model

model = init_model(cfg=checkpoint['cfg'],device='cuda')
model.module.load_state_dict(checkpoint['model'])
model.eval()

def transform_image(boxes):
    total_input = list()
    my_transforms = transforms.Compose([transforms.Resize((224,224)),
                                        transforms.ToTensor(),
                                        transforms.Normalize(
                                            [0.485, 0.456, 0.406],
                                            [0.229, 0.224, 0.225])])
    for i,box in enumerate(boxes):
        cv2.imwrite('temp.png',box)
        image = Image.open('temp.png').convert('RGB')
        total_input.append(my_transforms(image))
    return torch.stack(total_input)


def get_prediction(image_bytes): 
    boxes,detected_img = return_boxes(input_byte=image_bytes)
    tensor = transform_image(boxes)
    tensor = tensor.cuda()
    outputs = model.forward(tensor)
    _, y_hat = outputs.max(1)
    return y_hat.detach().cpu().numpy() , detected_img


@app.route('/predict', methods=['POST'])
def predict():
    response = dict()
    if request.method == 'POST':
        file = request.files['file']
        img_bytes = file.read()
        predicted_labels , img = get_prediction(image_bytes=img_bytes)
        output = list()
        for label in predicted_labels:
            id , name = imagenet_class_index[str(label)]
            output.append({id:name})
        response['output'] = output
        response['img'] = base64.b64encode(cv2.imencode('.jpg', img)[1]).decode()
        return jsonify(response)


class Ensemble(nn.ModuleList):
    # Ensemble of models
    def __init__(self):
        super().__init__()

    def forward(self, x, augment=False, profile=False, visualize=False):
        y = []
        for module in self:
            y.append(module(x, augment, profile, visualize)[0])
        # y = torch.stack(y).max(0)[0]  # max ensemble
        # y = torch.stack(y).mean(0)  # mean ensemble
        y = torch.cat(y, 1)  # nms ensemble
        return y, None  # inference, train output

def attempt_load(weights, map_location=None, inplace=True, fuse=True):
    from models.yolo import Detect, Model

    # Loads an ensemble of models weights=[a,b,c] or a single model weights=[a] or weights=a
    model = Ensemble()
    for w in weights if isinstance(weights, list) else [weights]:
        ckpt = torch.load(attempt_download(w), map_location=map_location)  # load
        if fuse:
            model.append(ckpt['ema' if ckpt.get('ema') else 'model'].float().fuse().eval())  # FP32 model
        else:
            model.append(ckpt['ema' if ckpt.get('ema') else 'model'].float().eval())  # without layer fuse

    # Compatibility updates
    for m in model.modules():
        if type(m) in [nn.Hardswish, nn.LeakyReLU, nn.ReLU, nn.ReLU6, nn.SiLU, Detect, Model]:
            m.inplace = inplace  # pytorch 1.7.0 compatibility
            if type(m) is Detect:
                if not isinstance(m.anchor_grid, list):  # new Detect Layer compatibility
                    delattr(m, 'anchor_grid')
                    setattr(m, 'anchor_grid', [torch.zeros(1)] * m.nl)
        elif type(m) is Conv:
            m._non_persistent_buffers_set = set()  # pytorch 1.6.0 compatibility

    if len(model) == 1:
        return model[-1]  # return model
    else:
        print(f'Ensemble created with {weights}\n')
        for k in ['names']:
            setattr(model, k, getattr(model[-1], k))
        model.stride = model[torch.argmax(torch.tensor([m.stride.max() for m in model])).int()].stride  # max stride
        return model  # return ensemble

def attempt_download(file, repo='ultralytics/yolov5'):  # from utils.downloads import *; attempt_download()
    # Attempt file download if does not exist
    file = Path(str(file).strip().replace("'", ''))
    return str(file)

def return_boxes(input_byte):

    weight_path = 'requirement/best.pt'

    USE_CUDA = torch.cuda.is_available()
    device = torch.device('cuda:0' if USE_CUDA else 'cpu')

    conf_thres = 0.25
    iou_thres = 0.45
    classes = None
    agnostic_nms = False
    max_det = 1000

    model = torch.jit.load(weight_path) if 'torchscript' in weight_path else attempt_load([weight_path], map_location=device)

    image = Image.open(io.BytesIO(input_byte))
    img0 = np.array(image)
    img0 = cv2.cvtColor(img0, cv2.COLOR_BGR2RGB)
    img = letterbox(img0, [640, 640], stride=32, auto=True)[0]
    img = np.ascontiguousarray(img)

    box_list = list()

    im0 = img0.copy()
    img = torch.from_numpy(img).to(device)
    img = img.float()
    img /= 255.0  # 0 - 255 to 0.0 - 1.0
    img = img.permute(2,0,1)

    if len(img.shape) == 3:
        img = img[None]  # expand for batch dim
    pred = model(img, augment=False, visualize=False)[0]
    pred = non_max_suppression(pred, conf_thres, iou_thres, classes, agnostic_nms, max_det=max_det)
    annotator = Annotator(im0, line_width=3, example=str('object'))

    for i, det in enumerate(pred):  # per image
        if len(det):
            det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()
            for *xyxy, conf, cls in reversed(det):
                detected_box = img0[int(xyxy[1].item()):int(xyxy[3].item()),int(xyxy[0].item()):int(xyxy[2].item())]
                box_list.append(detected_box)
                label = 'object ' + str(round(conf.item(),2))
                annotator.box_label(xyxy, label, color=colors(0, True))
    return box_list, im0



if __name__ == '__main__':

    app.run(host="0.0.0.0",debug=True,port=5000)