from gensim.models import Word2Vec
import pandas as pd

def finding_item(DB_list , query, top_k):

    candidate = list()
    for DB in DB_list:
        if query in DB:
            candidate.append(DB)
    
    if len(candidate) < top_k:
        return candidate
    else :
        return candidate[:top_k]

if __name__ == '__main__':

    DataBase = pd.read_csv('./DataBase.csv')
    DB_list = DataBase['name'].to_numpy()

    query = input("찾고자 하는 물품을 입력하세요 : ")

    candidate = finding_item(DB_list , query, 10)

    
