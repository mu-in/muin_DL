import requests
from PIL import Image
# curl -X POST -H "Content-Type: multipart/form-data" http://localhost:5000/predict -F "file=@kitten.jpg"

if __name__ =='__main__':
    resp = requests.post("http://localhost:5000/predict",
                     files={"file": open('/data3/taekguen/cropped_data/Validation/00000100003/10258_00_m_3.jpg','rb')})
    response = resp.json()
    
    print(response)