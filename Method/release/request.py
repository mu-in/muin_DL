import requests 
def send_data(url): 
    files = {'file':open('test.jpg', 'rb') } 
    res = requests.post(url,files=files) 
    return res.text 
if __name__ =='__main__':
    url = "https://d9b8-203-250-148-130.ngrok.io/predict" 
    print(send_data(url))
