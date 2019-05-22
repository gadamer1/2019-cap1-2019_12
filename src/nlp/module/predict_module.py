import pickle
import joblib
from konlpy.tag import Okt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import csv
import json
import numpy as np
import operator

def openStopword():
    f = open('stopwords.csv', 'r', encoding='utf-8')
    reader = csv.reader(f)
    stopwords = list()

    for row in reader:
        stopwords.append(row[0])

    return stopwords


def tokenizer(raw, pos=["Noun", "Verb"], stopword=openStopword()):
    okt = Okt()
    return [
        word for word, tag in okt.pos(
            raw,
            norm=True,
            stem=True
            )
            if len(word) > 1 and tag in pos and word not in stopword
        ]


#   예측 후 핵심역량 이름으로 return
def SVCpredict(model, text):
    keyword_names = ['글로벌역량', '능동', '도전', '성실', '소통', '인내심', '정직', '주인의식', '창의', '팀워크']
    result = model.predict([text])
    return keyword_names[result[0]-1]


#   decision function으로 예측 후 리스트 형태로 return
def SVCdecision(model, text):
    return model.decision_function([text]).tolist()[0]


#   분석 후 dictionary 형태로 return
def SVCproba(model, text):
    proba = model.predict_proba([text]).tolist()[0]
    proba = [format(proba[i], '.30f') for i in range(10)]
    keyword_eng = ['global', 'active', 'challenge', 'sincerity', 'communication', 'patient', 'honesty', 'responsibility', 'creative', 'teamwork']
    result = {}
    for i in range(10):
        result[keyword_eng[i]] = proba[i]
    return result

def Cosine(company_dict, company, user_text_dict):
    # cos = cosine_similarity(company_dict, user_text)
    cosine_dict = {}
    user_text = []

    for key in user_text_dict.keys():
        user_text.append(user_text_dict[key])

    for i in range(len(company_dict)):
        x = np.array(company_dict[company[i]]).reshape(1, -1)
        y = np.array(user_text).reshape(1, -1)
        cosine_dict[company[i]] = cosine_similarity(x, y)

    sorted(cosine_dict.items(), key=operator.itemgetter(1), reverse=True)

    sorted_company = []

    for key in cosine_dict.keys():
        sorted_company.append(key)

    top_company_name = sorted_company[0]
    top_company_value = company_dict[top_company_name]

    return (top_company_name, top_company_value, user_text)

#   분석 후 json으로 저장
def UserAnalysis(model, text):
    return json.dumps(SVCproba(model, text))


if __name__ == "__main__":
    vectorize = TfidfVectorizer(
        ngram_range=(1, 3),  # n-gram 3
        tokenizer=tokenizer,
        max_df=0.95,
        min_df=0,
        sublinear_tf=True
    )

    filename = 'SVC_PROB.joblib'
    svc_from_joblib = joblib.load(filename)

    keyword_names = ['글로벌역량', '능동', '도전', '성실', '소통', '인내심', '정직', '주인의식', '창의', '팀워크']
    job = ['architecture', 'IT', 'management', 'production', 'sales']
    company = ['samsung', 'hyundai', 'LG', 'SK', 'CJ']

    company_dict = {
        'samsung': [-0.8887642959439978, -0.2320497495038032, -0.3980158364286989, 0.07982216179178525,
                    -0.4634689585655357, -1.4945375211875371, -1.5887466236154073, -0.3994969557289842,
                    -1.9458319112295257, -0.6715375781390972],
        'hyundai': [-0.8228359594421046, -0.4560047847307666, -0.4392581998869604, 0.05151212010714745,
                    -0.37278093523020006, -1.441515818729987, -1.6143444997864906, -0.554804611382156,
                    -1.831011837725321, -0.6144309645563442],
        'LG': [-0.7620625480990436, -0.4474363044623253, -0.46674841323118554, 0.07333865957640484,
               -0.43207572092095403, -1.4279317971574639, -1.4718943563369267, -0.6400563343545634, -1.7959020562081858,
               -0.7120585840815354],
        'SK': [-0.7200478445244407, -0.4990252126738345, -0.4127369498124192, 0.006192507305919692,
               -0.41839920312881207, -1.4965564622475518, -1.4192891756133306, -0.552887345195595, -1.773997090857436,
               -0.6549712334986287],
        'CJ': [-0.7197954463771161, -0.3855618389458571, -0.5225478215844543, 0.010193007021379819, -0.2898697024011009,
               -1.865131533958604, -1.4985025101392337, -0.6209880454739807, -1.7121484451524631, -0.5946502637415154]
    } #테스트 데이터


    print(SVCproba(svc_from_joblib, "열정을 갖고 끊임없이 노력하는 사람"))
    print(SVCpredict(svc_from_joblib, "열정을 갖고 끊임없이 노력하는 사람"))
    print(UserAnalysis(svc_from_joblib, "열정을 갖고 끊임없이 노력하는 사람"))

    print((Cosine(company_dict, company, SVCproba(svc_from_joblib,"열정을 갖고 끊임없이 노력하는 사람"))))
