import io
import json
import torch
import torch.nn as nn
import torchvision.transforms as transforms

from PIL import Image
from flask import Flask, jsonify, request
from torch.cuda.amp import autocast
from timm.models import create_model

app = Flask(__name__)

checkpoint_path = './best_top1_validation.pth'
imagenet_class_index = json.load(open('./index_to_name.json'))
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

def transform_image(image_bytes):
    my_transforms = transforms.Compose([transforms.Resize(256),
                                        transforms.CenterCrop(224),
                                        transforms.ToTensor(),
                                        transforms.Normalize(
                                            [0.485, 0.456, 0.406],
                                            [0.229, 0.224, 0.225])])
    image = Image.open(io.BytesIO(image_bytes))
    return my_transforms(image).unsqueeze(0)


def get_prediction(image_bytes):
    tensor = transform_image(image_bytes=image_bytes)
    outputs = model.forward(tensor)
    _, y_hat = outputs.max(1)
    predicted_idx = str(y_hat.item())
    return imagenet_class_index[predicted_idx]


@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        file = request.files['file']
        img_bytes = file.read()
        class_id, class_name = get_prediction(image_bytes=img_bytes)
        return jsonify({'class_id': class_id, 'class_name': class_name})

if __name__ == '__main__':

    app.run()