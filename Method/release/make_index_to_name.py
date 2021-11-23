import json
import pandas as pd



if __name__ =='__main__':
    DB_path = '/DataBase.csv'
    DB = pd.read_csv(DB_path)

    json_file = dict()
    for i in range(DB.shape[0]):
        json_file[str(DB['data_id'][i])] = [str(DB['class'][i]),DB['name'][i]]

    with open('requirement/index_to_name_test.json', 'w', encoding='utf-8') as make_file:
        json.dump(json_file, make_file, ensure_ascii=False, indent="\t")
