import tkinter.ttk as ttk
import numpy as np
import pandas as pd
import cv2
import requests 
import kakaopay
import similar
import requests

from typing import List
from tkinter import *
from functools import partial
from PIL import Image, ImageTk

''' init '''
cam = cv2.VideoCapture(0)
data = []
quantity = 0
amount = 0
similarList = pd.DataFrame()
url = "https://e9af-203-250-148-130.ngrok.io/predict" 
database = pd.read_csv('products.csv')


def send_data(url): 
    files = {'file':open('captured_img.png', 'rb') } 
    res = requests.post(url,files=files) 
    return res.json()

''' func '''
def init():
    table.delete(*table.get_children())
    for i in range(20):
        plus[i].place(x=900,y=900)
        minus[i].place(x=900,y=900)
    count.config(text=str(0),font=('',25),foreground='#0076BA')
    total.config(text=str(0),font=('',25),foreground='#0076BA')

    img = Image.fromarray(255 * np.ones(shape=[1, 1, 3], dtype=np.uint8))
    imgtk = ImageTk.PhotoImage(image=img)
    picture.imgtk = imgtk
    picture.configure(image=imgtk)
    btn1.config(text='촬영')

def updateList(data):
    global quantity, amount

    table.delete(*table.get_children()) # init list

    total_quantity = 0
    total_amount = 0
    for i in range(0,len(data)):
        table.insert("",'end',text=f"no.{i}",
            values=(
                i+1,
                data[i]['category'],
                data[i]['name'],
                data[i]['price'],
                data[i]['quantity'],
                data[i]['price']*data[i]['quantity']
            )
        )  
        total_quantity+=data[i]['quantity']
        total_amount+=data[i]['price']*data[i]['quantity']

        plus[i].place(x=400,y=30+(i*40))
        minus[i].place(x=330,y=30+(i*40))
    
    count.config(text=str(total_quantity),font=('',25),foreground='#0076BA')
    total.config(text=str(total_amount),font=('',25),foreground='#0076BA')
    
    quantity = total_quantity
    amount = total_amount


def onCapture():
    global data
    ret,img = cam.read()
    if ret == False:
        print("Camera is Not Ready!")
        exit()
    
    cv2.imwrite('captured_img.png',img)
    resize_img = cv2.resize(img,dsize=(240,140),interpolation=cv2.INTER_AREA)
    response = send_data(url)

    GUI_img = Image.fromarray(resize_img) # 모델에 이시키 가져가면 될듯?
    imgtk = ImageTk.PhotoImage(image=GUI_img)

    detected_data = list()
    status = dict()

    # 갯수 파악 
    for item in response['output']:
        key = list(item.keys())[0]
        if key in status.keys():
            status[key] += 1
        else : status[key] = 1

    # 데이터 정리
    for key in status.keys():
        info = database[database['class']==int(key)]
        item = {
            "id" : info['data_id'].item(),
            "category" : info['category_large'].item(),
            "name" : info['category_small'].item(),
            "price" : info['price'].item(), 
            "quantity" : status[key]
        }
        detected_data.append(item)

    # tkinter update
    picture.imgtk = imgtk
    picture.configure(image=imgtk)
    btn1.config(text='재촬영')

    updateList(detected_data)

def plusCount(i):
    global data
    data[i]['quantity']+=1

    updateList(data)
    
def minusCount(i):
    global data
    if data[i]['quantity']!=0:
        data[i]['quantity']-=1

    updateList(data)

'''  popup '''
def open_search():
    def destroy():
        search.destroy()

    def getEntry():
        global similarList

        similarList = pd.DataFrame()
        similarList = similar.getSimilar(input.get())

        slistbox.delete(0,END)
        for i in range(len(similarList)):
            slistbox.insert(i,similarList.loc[i,'name'])
    
    def updateData():
        global data

        try:
            choose = slistbox.curselection()
            i = choose[0]
            data.append({'id':similarList.loc[i,'id'],'category':similarList.loc[i,'category'],'name':similarList.loc[i,'name'],'price':similarList.loc[i,'price'],'quantity':1})
            updateList(data)
            destroy()
        except:
            pass
        
    search = Toplevel(tk)
    search.title('상품 검색')
    search.geometry("300x550+100+100")

    text = Label(search)
    text.config(text='상품 검색',font=('',20))
    text.place(x=110,y=50)

    input = Entry(search, width=23)
    input.place(x=17,y=100)

    set = Button(search, width=1, height=1, command=getEntry)
    set.config(text='검색')
    set.place(x=250,y=100)

    # output
    sframe1 =  Frame(search,highlightbackground='black',highlightthickness=1)
    sframe1.config(width=265,height=150)
    sframe1.place(x=17,y=150)

    sscrollbar = Scrollbar(sframe1)
    sscrollbar.pack(side='right',fill='y')

    slistbox = Listbox(sframe1,yscrollcommand=sscrollbar.set)
    slistbox.config(width=28,height=10)
    slistbox.pack(side='left')

    sscrollbar['command']=slistbox.yview

    sframe2 = Frame(search,highlightbackground='black',highlightthickness=1)
    sframe2.config(width=265,height=80)
    sframe2.place(x=17,y=350)

    sbtn1 = Button(sframe2, width=25, height=4, command=updateData)
    sbtn1.config(text='추가')
    sbtn1.place(x=0,y=0)

    sframe3 = Frame(search,highlightbackground='black',highlightthickness=1)
    sframe3.config(width=265,height=80)
    sframe3.place(x=17,y=450)

    sbtn2 = Button(sframe3, width=25, height=4, command=destroy)
    sbtn2.config(text='취소')
    sbtn2.place(x=0,y=0)

def open_payment():
    def destroy():
        payment.destroy()

    def kakaoApi():
        kakaopay.payment(data,quantity,amount)
        init()
        destroy()

    payment = Toplevel(tk)
    payment.title('결제')
    payment.geometry("300x550+100+100")

    text = Label(payment)
    text.config(text='상품 결제',font=('',20))
    text.place(x=110,y=50)

    pframe1 = Frame(payment,highlightbackground='black',highlightthickness=1)
    pframe1.config(width=265,height=150)
    pframe1.place(x=17,y=130)

    text = Label(payment)
    text.config(text=f'총 {quantity} 개',font=('',15))
    text.place(x=123,y=180)

    text = Label(payment)
    text.config(text=amount,font=('',20))
    text.place(x=95,y=220)

    text = Label(payment)
    text.config(text='원',font=('',20))
    text.place(x=160,y=220)

    pframe2 = Frame(payment,highlightbackground='black',highlightthickness=1)
    pframe2.config(width=265,height=80)
    pframe2.place(x=17,y=350)

    pbtn1 = Button(pframe2, width=25, height=4, command=kakaoApi)
    pbtn1.config(text='결제')
    pbtn1.place(x=0,y=0)

    pframe3 = Frame(payment,highlightbackground='black',highlightthickness=1)
    pframe3.config(width=265,height=80)
    pframe3.place(x=17,y=450)

    sbtn2 = Button(pframe3, width=25, height=4, command=destroy)
    sbtn2.config(text='취소')
    sbtn2.place(x=0,y=0)

if __name__ == '__main__':

    ''' tkinter '''
    tk = Tk()
    tk.title('muin')
    tk.geometry('965x650+30+30') # 가로 x 세로 + x좌표 + y좌표
    tk.resizable(False,False) # 크기 변경 불가

    # cam
    frame1 = Frame(tk,highlightbackground='black',highlightthickness=1)
    frame1.config(width=265,height=165)
    frame1.place(x=50,y=50)

    picture = Label(tk)
    picture.grid(row=10,columns=10)
    picture.place(x=60,y=60)

    # notice
    frame2 = Frame(tk,highlightbackground='black',highlightthickness=1)
    frame2.config(width=265,height=260)
    frame2.place(x=50,y=250)

    text = Label(frame2)
    text.config(text='[ 사용방법 ]')
    text.place(x=10,y=10)

    text = Label(frame2)
    text.config(text='1. 상품을 계산대 위에 올립니다.\n2. 촬영 버튼을 누릅니다.\n3.상품 리스트 확인 후 결제 버튼을 누릅니다.')
    text.place(x=10,y=40)

    text = Label(frame2)
    text.config(text='[ 주의사항 ]')
    text.place(x=10,y=120)

    text = Label(frame2)
    text.config(text='1. 물품을 겹치면 인식이 안됩니다.\n2. 인식 오류 시 재촬영을 누르세요.\n3. 상품 검색버튼으로 추가할 수 있습니다.')
    text.place(x=10,y=150)

    # list
    frame3 = Frame(tk,highlightbackground='black',highlightthickness=1)
    frame3.config(width=565,height=350)
    frame3.place(x=350,y=50)

    table = ttk.Treeview(frame3,selectmode='browse')
    table.config(height=8)
    table.pack(side='left')

    style = ttk.Style()
    style.configure('Treeview', rowheight=40)

    scrollbar = ttk.Scrollbar(frame3,orient='vertical',command=table.yview)
    scrollbar.pack(side='right',fill='y')

    table.configure(yscrollcommand=scrollbar.set)

    table['columns'] = ("1","2","3","4","5","6",)
    table['show']='headings'
    table.column("1",width=40,anchor='c')
    table.column("2",width=90,anchor='c')
    table.column("3",width=140,anchor='c')
    table.column("4",width=60,anchor='c')
    table.column("5",width=120,anchor='c')
    table.column("6",width=100,anchor='c')
    table.heading("1",text='No.')
    table.heading("2",text='대분류')
    table.heading("3",text='상품명')
    table.heading("4",text='단가')
    table.heading("5",text='수량')
    table.heading("6",text='총 금액')

    # init plus, minus btn - max 20
    plus = []
    minus = []

    for i in range(20):
        plus.append(Button(table, width=1, height=1))
        minus.append(Button(table, width=1, height=1))

    for i in range(20):
        plus[i].config(text='+',command=partial(plusCount,i))
        minus[i].config(text='-',command=partial(minusCount,i))

    # result
    frame4 = Frame(tk,highlightbackground='black',highlightthickness=1)
    frame4.config(width=565,height=80)
    frame4.place(x=350,y=430)

    text = Label(frame4)
    text.config(text='총 수량',font=('',15),foreground='#5E5E5E')
    text.place(x=20,y=25)

    text = Label(frame4)
    text.config(text='개',font=('',15),foreground='#5E5E5E')
    text.place(x=140,y=25)

    count = Label(frame4)
    count.config(text='0',font=('',25),foreground='#0076BA')
    count.place(x=100,y=18)

    total = Label(frame4)
    total.config(text='0',font=('',25),foreground='#0076BA')
    total.place(x=380,y=18)

    text = Label(frame4)
    text.config(text='원',font=('',15),foreground='#5E5E5E')
    text.place(x=500,y=25)

    # capture btn
    frame5 = Frame(tk,highlightbackground='black',highlightthickness=1)
    frame5.config(width=265,height=80)
    frame5.place(x=50,y=530)

    btn1 = Button(frame5, width=25, height=4, command=onCapture)
    btn1.config(text='촬영')
    btn1.place(x=0,y=0)

    # search btn
    frame6 = Frame(tk,highlightbackground='black',highlightthickness=1)
    frame6.config(width=265,height=80)
    frame6.place(x=350,y=530)

    btn2 = Button(frame6, width=25, height=4, command=open_search)
    btn2.config(text='상품 검색')
    btn2.place(x=0,y=0)

    # pay btn
    frame7 = Frame(tk,highlightbackground='black',highlightthickness=1)
    frame7.config(width=265,height=80)
    frame7.place(x=650,y=530)

    btn2 = Button(frame7, width=25, height=4, command=open_payment)
    btn2.config(text='결제')
    btn2.place(x=0,y=0)

    tk.mainloop()