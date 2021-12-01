from tkinter import *
import tkinter.ttk as ttk
import tkinter.font as tkFont
from PIL import Image, ImageTk
from functools import partial

import numpy as np
import pandas as pd
import cv2

import requests

from module import similar
from module import kakaopay
from data import dummy

''' init '''
cam = cv2.VideoCapture(0)
data = []
quantity = 0
amount = 0
similarList = pd.DataFrame()

database = pd.read_csv('./data/products.csv')

url = 'https://d714-203-250-148-130.ngrok.io/predict'

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

def sendData(url): 
    files = {'file':open('./data/captured_img.png', 'rb') } 
    res = requests.post(url,files=files) 
    
    return res.json()

def updateList(data):
    global quantity, amount
    total_quantity = 0
    total_amount = 0

    table.delete(*table.get_children())

    for i in range(0,len(data)):
        if i%2==0 : 
            tagname = 'evenrow'
        else : 
            tagname = 'oddrow'

        table.insert("",'end',tag=tagname,
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

        plus[i].place(x=410,y=30+(i*40),width=30,height=30)
        minus[i].place(x=340,y=30+(i*40),width=30,height=30)

    count.config(text=str(total_quantity),font=gothic30b)
    total.config(text=str(total_amount),font=gothic30b)

    table.tag_configure('evenrow',background='#f2f2f2')
    table.tag_configure('oddrow',background='#ffffff')
    
    quantity = total_quantity
    amount = total_amount

def onCapture():
    global data
    
    init()
    ret,img = cam.read()
    if ret == False:
        print("Camera is Not Ready!")
        exit()
    
    # test
    img = cv2.imread('./data/test.jpeg',cv2.IMREAD_COLOR)

    cv2.imwrite('./data/captured_img.png',img)

    resize_img = cv2.resize(img,dsize=(240,140),interpolation=cv2.INTER_AREA)
    cvt_img = cv2.cvtColor(resize_img,cv2.COLOR_BGR2RGB)

    GUI_img = Image.fromarray(cvt_img)
    imgtk = ImageTk.PhotoImage(image=GUI_img)

    response = sendData(url)
    
    #detected_data = dummy.data
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
            "name" : info['name'].item(),
            "price" : info['price'].item(), 
            "quantity" : status[key]
        }
        detected_data.append(item)

    # tkinter update
    picture.imgtk = imgtk
    picture.configure(image=imgtk)
    btn1.config(text='재촬영')
    
    data = detected_data

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
def openSearch():
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
    search.configure(background='#f2f2f2')

    text = Label(search)
    text.config(text='상품 검색',font=gothic20b,background='#f2f2f2')
    text.place(x=110,y=50)

    input = Entry(search,highlightbackground='#f2f2f2')
    input.place(x=17,y=100,width=210)

    set = Button(search, command=getEntry, highlightbackground='#f2f2f2',highlightthickness=0, font=gothic13, bg='#ffffff')
    set.config(text='검색')
    set.place(x=230,y=100,width=50,height=30)

    # output
    sframe1 =  Frame(search,highlightbackground='#A5AEBA',highlightthickness=0)
    sframe1.config(width=265,height=150)
    sframe1.place(x=17,y=150)

    sscrollbar = Scrollbar(sframe1)
    sscrollbar.pack(side='right',fill='y')

    slistbox = Listbox(sframe1,yscrollcommand=sscrollbar.set)
    slistbox.config(width=28,height=10)
    slistbox.pack(side='left')

    sscrollbar['command']=slistbox.yview

    sbtn1 = Button(search, width=25, height=4, command=updateData, highlightbackground='#f2f2f2',highlightthickness=0, font=gothic20b, bg='#FA6D6E',fg='#FA6D6E')#,fg='#ffffff')
    sbtn1.config(text='추가')
    sbtn1.place(x=17,y=350, width=265,height=80)

    sbtn2 = Button(search, width=25, height=4, command=destroy, highlightbackground='#f2f2f2',highlightthickness=0, font=gothic20b, bg='#ffffff')
    sbtn2.config(text='취소')
    sbtn2.place(x=17,y=450, width=265,height=80)

def openPayment():
    def destroy():
        payment.destroy()

    def kakaoApi():
        kakaopay.payment(data,quantity,amount)
        init()
        destroy()

    payment = Toplevel(tk)
    payment.title('결제')
    payment.geometry("300x550+100+100")
    payment.configure(background='#f2f2f2')

    text = Label(payment)
    text.config(text='상품 결제',font=gothic20b,background='#f2f2f2')
    text.place(x=110,y=50)

    pframe = Frame(payment,highlightbackground='#A5AEBA',highlightthickness=1,background='#ffffff')
    pframe.config(width=265,height=150)
    pframe.place(x=17,y=130)

    text = Label(payment,font=gothic15b,background='#ffffff', foreground='#5E5E5E')
    text.config(text=f'총 {quantity} 개')
    text.place(x=123,y=160)

    text = Label(payment,font=gothic30b,background='#ffffff', foreground='#FA6D6E')
    text.config(text=f"{amount} 원")
    text.place(x=95,y=200)

    pbtn1 = Button(payment, width=25, height=4, command=kakaoApi, highlightbackground='#f2f2f2',highlightthickness=0,font=gothic20b,bg='#FA6D6E',fg='#FA6D6E')#,fg='#ffffff')
    pbtn1.config(text='결제')
    pbtn1.place(x=17,y=350,width=265,height=80)

    pbtn2 = Button(payment, width=25, height=4, command=destroy,highlightbackground='#f2f2f2',highlightthickness=0,font=gothic20b,bg='#ffffff')
    pbtn2.config(text='취소')
    pbtn2.place(x=17,y=450, width=265,height=80)

if __name__ == '__main__':
    ''' tkinter '''
    tk = Tk()
    tk.title('muin')
    tk.geometry('965x650+30+30') # 가로 x 세로 + x좌표 + y좌표
    tk.resizable(False,False) # 크기 변경 불가
    tk.configure(background='#C5D1D9')
    
    # font set
    gothic13 = tkFont.Font(family='Malgun Gothic',weight='normal',size=13,slant='roman')
    gothic15 = tkFont.Font(family='Malgun Gothic',weight='normal',size=15,slant='roman')
    gothic15b = tkFont.Font(family='Malgun Gothic',weight='bold',size=15,slant='roman')
    gothic20b = tkFont.Font(family='Malgun Gothic',weight='bold',size=20,slant='roman')
    gothic30b = tkFont.Font(family='Malgun Gothic',weight='bold',size=30,slant='roman')

    # cam
    frame1 = Frame(tk,highlightbackground='#A4AEBA',highlightthickness=1)
    frame1.config(width=265,height=165, background='#3C3F44')
    frame1.place(x=50,y=50)

    picture = Label(tk)
    picture.configure(background='#3C3F44')
    picture.grid(row=10,columns=10)
    picture.place(x=60,y=60)

    # notice
    frame2 = Frame(tk,highlightbackground='#A4AEBA',highlightthickness=1)
    frame2.configure(background='#ffffff')
    frame2.config(width=265,height=260)
    frame2.place(x=50,y=250)

    text = Label(frame2)
    text.config(text='[ 사용방법 ]')
    text.configure(background='#fbff00',font=gothic15b)
    text.place(x=10,y=10)

    text = Label(frame2)
    text.config(text='1. 상품을 계산대 위에 올립니다.\n2. 촬영 버튼을 누릅니다.\n3.상품 리스트 확인 후 결제 버튼을 누릅니다.')
    text.configure(background='#ffffff',font=gothic13)
    text.place(x=10,y=40)

    text = Label(frame2)
    text.config(text='[ 주의사항 ]')
    text.configure(background='#fbff00',font=gothic15b)
    text.place(x=10,y=120)

    text = Label(frame2)
    text.config(text='1. 물품을 겹치면 인식이 안됩니다.\n2. 인식 오류 시 재촬영을 누르세요.\n3. 상품 검색버튼으로 추가할 수 있습니다.')
    text.configure(background='#ffffff',font=gothic13)
    text.place(x=10,y=150)

    # list
    frame3 = Frame(tk,highlightbackground='#A4AEBA',highlightthickness=1)
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
    table.column("1",width=20,anchor='c')
    table.column("2",width=90,anchor='c')
    table.column("3",width=160,anchor='c')
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
        plus.append(Button(table,highlightthickness=0))
        minus.append(Button(table,highlightthickness=0))

    for i in range(20):
        if i%2==0: bgColor = '#f2f2f2'
        else : bgColor = '#ffffff'

        plus[i].config(text='+',command=partial(plusCount,i),highlightbackground=bgColor,font=gothic15b,bg='#FA6D6E',fg='#FA6D6E')
        minus[i].config(text='-',command=partial(minusCount,i),highlightbackground=bgColor,font=gothic15b,bg='#0076BA',fg='#0076BA')

    # result
    frame4 = Frame(tk,highlightbackground='#A4AEBA',highlightthickness=1)
    frame4.config(width=565,height=80)
    frame4.configure(background='#ffffff')
    frame4.place(x=350,y=430)

    text = Label(frame4)
    text.config(text='총 수량',font=('',15),foreground='#5E5E5E')
    text.configure(background='#ffffff',font=gothic20b)
    text.place(x=20,y=25)

    text = Label(frame4)
    text.config(text='개',font=('',15),foreground='#5E5E5E')
    text.configure(background='#ffffff',font=gothic20b)
    text.place(x=180,y=25)

    count = Label(frame4)
    count.config(text='0',font=('',25),foreground='#0076BA')
    count.configure(background='#ffffff',font=gothic30b)
    count.place(x=120,y=18)

    total = Label(frame4)
    total.config(text='0',font=('',25),foreground='#0076BA')
    total.configure(background='#ffffff',font=gothic30b)
    total.place(x=380,y=18)

    text = Label(frame4)
    text.config(text='원',font=('',15),foreground='#5E5E5E')
    text.configure(background='#ffffff',font=gothic20b)
    text.place(x=500,y=25)

    # capture btn
    btn1 = Button(tk, highlightbackground='#C5D1D9',command=onCapture, font=gothic20b, bg='#FA6D6E',fg='#FA6D6E')#,fg='#ffffff')
    btn1.config(text='촬영')
    btn1.place(x=50,y=530, width=265, height=80)

    # search btn
    btn2 = Button(tk, highlightbackground='#C5D1D9',command=openSearch, font=gothic20b, bg='#ffffff')
    btn2.config(text='상품 검색')
    btn2.place(x=350,y=530, width=265, height=80)

    # pay btn
    btn3 = Button(tk, highlightbackground='#C5D1D9', command=openPayment, font=gothic20b, bg='#ffffff')
    btn3.config(text='결제')
    btn3.place(x=650,y=530,width=265, height=80)

    tk.mainloop()
