# encoding = utf8
import os
import csv
import copy
import time
import traceback
import pyLDAvis.sklearn
import pandas as pd
import numpy as np
from nltk import *
from nltk.corpus import stopwords
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer

FILES = ['TheDailyTelegraph.csv', 'TheNewYorkTimes.csv', 'XinHua.csv']
Topic_dic = {
    'TheDailyTelegraph' : {0 : 'Health', 1 : 'Politics', 2 : 'Economy', 3 : 'Others'},
    'TheNewYorkTimes' : {0 : 'Economy', 1 : 'Others', 2 : 'Health', 3 : 'Politics'},
    'XinHua' : {0 : 'Health', 1 : 'Economy', 2 : 'Politics', 3 : 'Others'}
}

def replaceReturn(str):
    return str.replace('\n','').replace('\r','')

def make_folder(folder):
    if not os.path.isdir(folder):
        os.makedirs(folder)

# 关键词提取和向量转换
def extractKeywords(feature_model, n_features, max_df, min_df):
    # TF-IDF 提取特征
    if feature_model == 'TF-IDF':
        return TfidfVectorizer(strip_accents = 'unicode', max_features = n_features, max_df = max_df, min_df = min_df)
    # 根据词频提取特征
    else:
        return CountVectorizer(strip_accents = 'unicode', max_features = n_features, max_df = max_df, min_df = min_df)

# 获取每个主题中的关键词
def getTopWords(model, feature_names, n_top_words, n_type):
    top_words = [[] for i in range(n_type)]
    for topic_id, topic in enumerate(model.components_):
        top_words[topic_id] = " ".join([feature_names[i] for i in topic.argsort()[:- n_top_words - 1:-1]])
    return top_words

if __name__ == "__main__":
    try:
        all_starttime = time.time()
        curpath = os.path.dirname(__file__)
        stop_words = stopwords.words('english')
        with open('stopwords_en.txt', 'r') as f:
            lines = f.readlines()
            for line in lines:
                stop_words.append(replaceReturn(line))
        for w in ['!', ',', '.', '?', '(', ')', '--', 'Enditem', "“", "”", ":", "—"]:
            stop_words.append(w)
        stop_words = list(set(stop_words))
        for file in FILES:
            publisher = file.split('.')[0]
            save_folder = publisher + "_cluster"
            make_folder(save_folder)
            path = os.path.join(curpath, file)
            df = pd.read_csv(path)
            starttime = time.time()
            df['words'] = df['content'].apply(lambda x: " ".join([w for w in word_tokenize(x) if w.lower() not in stop_words]))
            endtime = time.time()
            print(u"去除停用词用时: %d 秒" % round(endtime - starttime, 0))
            national_news = df[df.type == 'national']
            international_news = df[df.type == 'international']
            print("%s : %d items, %d national news, %d international news" % ( file, len(df), len(national_news), len(international_news)))
            for type_name in ["national", "international"]:
                print("=" * 20, file, type_name, "=" * 20)
                df = copy.deepcopy(national_news) if type_name == "national" else copy.deepcopy(international_news)
                starttime = time.time()
                n_features = 1000
                # tf_vectorizer = extractKeywords('TF-IDF', n_features, 0.6, 0.001)
                tf_vectorizer = extractKeywords('Count', n_features, 0.6, 0.01)
                tf = tf_vectorizer.fit_transform(df.words)
                endtime = time.time()
                print(u"%s: %s生成特征用时: %d 秒" % (file, type_name, round(endtime - starttime, 0)))
                # 聚类个数
                for n_components in [4]:
                    starttime = time.time()
                    lda = LatentDirichletAllocation(n_components = n_components,
                                                    max_iter = 50,
                                                    learning_method = 'online',
                                                    learning_offset = 50.)
                    lda.fit(tf)
                    n_top_words = 30
                    tf_feature_names = tf_vectorizer.get_feature_names()
                    endtime = time.time()
                    print(u"%s: %s %d topic LDA训练用时: %d 秒" % (file, type_name, n_components, round(endtime - starttime, 0)))
                    print(u'困惑度为：%f' % lda.perplexity(tf, sub_sampling = False))

                    top_words = getTopWords(lda, tf_feature_names, n_top_words, n_components)
                    p = pyLDAvis.sklearn.prepare(lda, tf, tf_vectorizer)
                    html_name = type_name + '_' + str(n_components) + '_topic_LDA.html'
                    pyLDAvis.save_html(p, os.path.join(curpath, save_folder, html_name))

                    dic = Topic_dic[publisher]
                    # 创建文档-主题矩阵
                    tf1 = np.matrix(lda.transform(tf))
                    topic = tf1 / tf1.sum(axis = 1)
                    topic = topic.argmax(axis = 1)
                    df['topic'] = topic
                    df['topic'] = df['topic'].apply(lambda x: dic[x])
                    with open(os.path.join(curpath, save_folder, type_name + '_' + str(n_components) + '_topic_info.csv'), "w", encoding = "utf-8-sig",
                              newline = '') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow(['topic_id', 'topic', 'number', 'keywords'])
                        for k,v in dic.items():
                            print("%s topic : %d items" % (v, len(df[df.topic == v])))
                            writer.writerow([k, v, len(df[df.topic == v]), top_words[k]])
                    df = df[['title', 'byline', 'publish_date', 'length', 'content', 'topic']]
                    csv_name = os.path.join(curpath, save_folder, type_name + '_' + str(n_components) + '_topic_result.csv')
                    df.to_csv(csv_name, index = False, encoding = 'utf_8_sig')
                    print("=" * 60)
        all_endtime = time.time()
        print(u"共用时: %d 秒" % round(all_endtime - all_starttime, 0))
    except Exception as e:
        print('Error: ', e)
        traceback.print_exc()
