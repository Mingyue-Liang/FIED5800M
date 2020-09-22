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

def titleSentiment(title):#先对title进行判断
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
    sentiment_dic = { #30-34为了60行的print
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
            blob = TextBlob(row['content'])#对文本进行判断，根据textblog这个库获取情感
            score = round(blob.sentiment.polarity,5)
        df.loc[index, 'sentiment_score'] = score
        s_result = 'neutral'
        if score >= 0.2:
            s_result = 'positive'
        elif score < 0:
            s_result = 'negative'
        sentiment_dic[s_result] += 1 #为了68行验证，因为对一篇新闻进行分析，记录结果在控制台
        df.loc[index, 'sentiment_result'] = s_result #情感分类的结果
    
    print("title positive: %s items, negative: %s items" % (title_positive_num, title_negative_num))
    return df, sentiment_dic

f=open('TheNewYorkTimes_topic_result.csv','Economy')
s=input()
ls=[]
for i in f:
    ls.append(i.strip('\n').split(','))
print(ls)
count = 0

for i in ls:
    for j in i:
        if j==s:
            count+=1
print('{0}'.format(count))







if __name__ == "__main__": #即将调用的函数都在前面
    try:
        curpath = os.path.dirname(__file__)#获取路径，打开文件
        for file in FILES:
            publisher = file.split('.')[0]#通过文件名获取是哪个出版社
            path = os.path.join(curpath, file)
            df = pd.read_csv(path)
            print(file)
            df, sentiment_dic = getSentimentScore(df)#命名
            csv_name = os.path.join(curpath, publisher + '_sentiment_result.csv')#存成文件
            df.to_csv(csv_name, index = False, encoding = 'utf_8_sig')
            print(sentiment_dic)
#异常处理
    except Exception as e:
        print('Error: ', e)
        traceback.print_exc()
