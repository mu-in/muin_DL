import requests
from PIL import Image
# curl -X POST -H "Content-Type: multipart/form-data" http://localhost:5000/predict -F "file=@kitten.jpg"

if __name__ =='__main__':
    resp = requests.post("http://localhost:5000/predict",
                     files={"file": open('/home/gtlim/workspace/Muin_Term_Project/FLASK/kitten.jpg','rb')})
    response = resp.json()
    
    print(response)