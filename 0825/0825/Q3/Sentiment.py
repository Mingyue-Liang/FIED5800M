# encoding = utf8
import os
import csv
import time
import copy
import traceback
import pandas as pd
from textblob import TextBlob
import pyecharts.options as opts
#  from pyecharts.charts import Line,Bar
from pyecharts.charts import Line

FILES = ['TheDailyTelegraph.csv', 'TheNewYorkTimes.csv', 'XinHua.csv']
title_negative_keywords = ["death toll", "new infections", "new cases", "daily deaths", "deaths", "new confirmed"]
title_positive_keywords = ["reduce", "decrease", "reducing", "reduced", "decreased", "decreasing"]

def titleSentiment(title):
    for i in range(len(title_negative_keywords)):
        n_word = title_negative_keywords[i]
        if n_word in title :
            for p_word in title_positive_keywords:
                if p_word in title:
                    return 1
            if '0' not in title:
                return -1
    return 0

def getSentimentScore(df):
    title_positive_num, title_negative_num = 0, 0
    sentiment_dic = {
        'positive' : 0,
        'neutral' : 0,
        'negative' : 0
    }
    for index, row in df.iterrows():
        s_result = 'neutral'
        score = titleSentiment(row['title'])
        if score == 1:
            title_positive_num += 1
        elif score == -1:
            title_negative_num += 1
        else:
            blob = TextBlob(row['content'])
            score = round(blob.sentiment.polarity,5)
        df.loc[index, 'sentiment_score'] = score
        s_result = 'neutral'
        if score >= 0.2:
            s_result = 'positive'
        elif score < 0:
            s_result = 'negative'
        sentiment_dic[s_result] += 1
        df.loc[index, 'sentiment_result'] = s_result
    
    print("title positive: %s items, negative: %s items" % (title_positive_num, title_negative_num))
    return df, sentiment_dic

if __name__ == "__main__":
    try:
        curpath = os.path.dirname(__file__)
        for file in FILES:
            publisher = file.split('.')[0]
            path = os.path.join(curpath, file)
            df = pd.read_csv(path)
            print(file)
            df, sentiment_dic = getSentimentScore(df)
            csv_name = os.path.join(curpath, publisher + '_sentiment_result.csv')
            df.to_csv(csv_name, index = False, encoding = 'utf_8_sig')
            print(sentiment_dic)

    except Exception as e:
        print('Error: ', e)
        traceback.print_exc()
