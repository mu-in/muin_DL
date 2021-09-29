import io
import json
import os
import numpy as np
import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
from flask import Flask, jsonify, request


app = Flask(__name__)
model = models.densenet121(pretrained=True)               # ImageNet의 1000개 클래스를 학습
model.eval()                                              # autograd를 끄고



img_class_map = None
mapping_file_path = 'index_to_name.json'                  # 사람이 읽을 수 있는 ImageNet 클래스 이름
if os.path.isfile(mapping_file_path):
    with open (mapping_file_path) as f:
        img_class_map = json.load(f)



# Transform input into the form our model expects
def transform_image(infile):

    input_transforms = [transforms.Resize(224),           # 이미지 준비를 위해 여러 TorchVision transforms 사용
        transforms.Normalize([0.485, 0.456, 0.406],       # ImageNet 모델 입력에 대한 표준 정규화
            [0.229, 0.224, 0.225])]
    my_transforms = transforms.Compose(input_transforms)
    import pdb;pdb.set_trace()
    image = Image.open(infile)                            # 이미지 파일 열기
    image = torch.FloatTensor(np.array(image))
    print(image.shape)
    timg = my_transforms(image)                           # PIL 이미지를 적절한 모양의 PyTorch 텐서로 변환
    timg.unsqueeze_(0)                                    # PyTorch 모델은 배치 입력을 예상하므로 1짜리 배치를 만듦
    return timg


# Get a prediction
def get_prediction(input_tensor):
    outputs = model.forward(input_tensor)                 # 모든 ImageNet 클래스에 대한 가능성(likelihood) 얻기
    _, y_hat = outputs.max(1)                             # 가장 가능성 높은 클래스 추출
    prediction = y_hat.item()                             # PyTorch 텐서에서 int 값 추출
    return prediction

# Make the prediction human-readable
def render_prediction(prediction_idx):
    stridx = str(prediction_idx)
    class_name = 'Unknown'
    if img_class_map is not None:
        if stridx in img_class_map is not None:
            class_name = img_class_map[stridx][1]

    return prediction_idx, class_name


@app.route('/', methods=['GET'])
def root():
    return jsonify({'msg' : 'Try POSTing to the /predict endpoint with an RGB image attachment'})


@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        file = request.files['file']
        if file is not None:
            input_tensor = transform_image(file)
            prediction_idx = get_prediction(input_tensor)
            class_id, class_name = render_prediction(prediction_idx)
            return jsonify({'class_id': class_id, 'class_name': class_name})


if __name__ == '__main__':
    app.run()