import pandas as pd

df = pd.read_csv('products.csv')
df = df.loc[:,['data_id','category_large','name','price']]
df.columns = ['id','category','name','price']

names = list(df['name'])

# 초성 검출 함수
def getChosung(text):
    CHOSUNG_START_LETTER = 4352
    JAMO_START_LETTER = 44032
    JAMO_END_LETTER = 55203
    JAMO_CYCLE = 588

    def isHangul(ch):
        return ord(ch) >= JAMO_START_LETTER and ord(ch) <= JAMO_END_LETTER

    result = text

    for ch in text:
        if isHangul(ch): #한글이 아닌 글자는 걸러냅니다.
            result += chr(int((ord(ch) - JAMO_START_LETTER)/JAMO_CYCLE + CHOSUNG_START_LETTER) + 8252)     
            # +8252 가 핵심!! <- ord() 찍어봤더니 달랐음

    return result

def getSimilar(input):
    result = pd.DataFrame(columns=['id','category','name','price'])
    for idx, name in enumerate(names):
        if input in getChosung(name):
            result=result.append(df.iloc[idx],ignore_index=True)

    return result

if __name__=='__main__':
    print(getSimilar('ㅋㅊ'))
