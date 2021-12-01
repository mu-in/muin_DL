import cv2
import pyzbar.pyzbar as zbar
import time
import requests
import numpy as np

from module import key

cap = cv2.VideoCapture(0)
block = np.zeros((384,384,3),np.uint8)

qr = ''
cnt = 0

server = key.SERVER_URL

while True:
    success, frame = cap.read()

    if success:
        for code in zbar.decode(frame):
            if qr != code.data.decode("utf-8"):
                qr = code.data.decode("utf-8")
                res = requests.get(f'{server}/user/qrcode?seed={qr}')
                print(res.json())

                try:
                    if(res.json()['validation']==True):
                        cnt=30
        
                except:
                    pass
        
        if cnt==0:
            cv2.putText(frame,'show your QR',(30,50),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2,cv2.LINE_AA)
            cv2.imshow('cam',frame)
        else:
            cv2.putText(frame,'success!!',(30,50),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2,cv2.LINE_AA)
            cv2.imshow('cam',frame)
            cnt-=1

        key = cv2.waitKey(1)
        
        if key == 27: # esc
            break

cap.release()
cv2.destroyAllWindows()