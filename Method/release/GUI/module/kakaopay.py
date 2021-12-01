import requests
import webbrowser
import time
import os

from module import key

ADMIN_KEY = key.ADMIN_KEY

server = key.SERVER_URL+'/payment'
kakao = key.KAKAO_URL

def postServer(data,total):
    products = []
    for i in range(len(data)):
        products.append({'id':data[i]['id'],'name':data[i]['name'],'quantity':data[i]['quantity']})
    
    param = {
        'storeUuid': 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaaaaaa',
        'stocks': products,
        'totalPrice': total,
    }
    
    res = requests.post(server, json=param)

    print(res.json())

def payment(data,quantity,total):
    header = {
        'Authorization':f'KakaoAK {ADMIN_KEY}',
        'Content-type':'application/x-www-form-urlencoded;charset=utf-8'
    }

    param = {
        'cid':'TC0ONETIME',
        'partner_order_id':'-',
        'partner_user_id':'-',
        'item_name':'뮤인 무인매장',
        'quantity':quantity,
        'total_amount':total,
        'tax_free_amount':0,
        'approval_url':'http://127.0.0.1:5000',
        'cancel_url':'http://127.0.0.1:5000',
        'fail_url':'http://127.0.0.1:5000'
    }

    res = requests.post(kakao, headers=header, params=param)
    redirect = res.json()

    webbrowser.open(url=redirect['next_redirect_pc_url'])
    
    time.sleep(15) # 15초 기다리고 닫기
    os.system("killall -9 'Safari'") # mac
    # os.system("taskkill /im chrome.exe /f") # window

    postServer(data,total) # 결제 내역 post

    return redirect['next_redirect_pc_url']

if __name__== '__main__':
    redirect = payment([{'id':1,'category':'test','name':'test','price':1000,'quantity':3}],3,3000)