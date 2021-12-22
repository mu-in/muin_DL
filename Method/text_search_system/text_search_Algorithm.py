import pandas as pd

def getChosung(text): # 초성 검출 함수

    CHOSUNG_START_LETTER = 4352
    JAMO_START_LETTER = 44032
    JAMO_END_LETTER = 55203
    JAMO_CYCLE = 588

    def isHangul(ch):
        return ord(ch) >= JAMO_START_LETTER and ord(ch) <= JAMO_END_LETTER

    result = text

    for ch in text:
        if isHangul(ch): # 해당 글자가 한글일 경우
            result += chr(int((ord(ch) - JAMO_START_LETTER)/JAMO_CYCLE + CHOSUNG_START_LETTER) + 8252)     
            # 추출한 초성 reult에 누적
    return result

if __name__ == '__main__':
    
    file_path = '' # 데이터 프레임 형태의 파일 경로 지정
    test_df = pd.DataFrame(pd.read_csv(file_path, encoding='CP949'))
    names = list(test_df['name']) # 과자 이름 list 생성

    input = 'ㅋㅊ' # 검색 예시) 'ㅋㅊ'

    for idx, name in enumerate(names):
        if input in getChosung(name):
            print('제품명: {:10s}   ,제품가격: {:5d}'.format(name, test_df.iloc[idx]['price']))
            print("")
