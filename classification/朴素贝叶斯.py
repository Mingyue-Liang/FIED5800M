import os

from sklearn.feature_extraction.text import  TfidfVectorizer
import pandas as pd

import importlib, sys

importlib.reload(sys)
from sklearn.metrics import confusion_matrix
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

from sklearn.naive_bayes import MultinomialNB

import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False


fileList = os.listdir('./file')

fileList.sort()


def train_data():
    data1 = pd.DataFrame()
    for file in fileList:
        data = pd.read_csv('./file/'+file, usecols=['Theme', 'title', 'content', ], low_memory=False)

        data = data[data['Theme'].isin(['Health', 'Politics', 'Economy', 'Others'])]#取出已经标记好的数据
        data1 = data1.append(data)
    return data1


def get_confusion_matrix(method):
    '''获得个模型的评价指数——混淆矩阵'''

    plt.style.use({'figure.figsize': (7, 6)})
    f, ax = plt.subplots()
    labels = ['Health', 'Politics', 'Economy', 'Others']

    cm = confusion_matrix(y_test, y_predict, labels=labels)
    sns.heatmap(cm,
                ax=ax, annot=True, xticklabels=labels,
                yticklabels=labels,

                annot_kws={'size': 16, 'weight': 'bold', 'color': 'blue'}, fmt="d")

    ax.set_title('{}-confusion matrix'.format(method), fontsize=15)  # 标题
    ax.set_xlabel('predict', fontsize=15)  # x轴
    ax.set_ylabel('ture', fontsize=15)  # y轴
    plt.savefig('{}混淆矩阵.jpg'.format(method))

    plt.show()

data_all = train_data()

data_all = data_all.dropna()

train_x, test_x, y_train, y_test = train_test_split(data_all['content'], data_all['Theme'],
                                                    test_size=0.1)  # 分为训练数据，和测试集,利用内容进行分类
count_vec = TfidfVectorizer(binary=False, decode_error='ignore', stop_words='english')  # 文本向量化 tf_idf
x_train = count_vec.fit_transform(train_x)
x_test = count_vec.transform(test_x)

clf = MultinomialNB(alpha=0.001)  # 朴素贝叶斯模型
clf = clf.fit(x_train, y_train)

y_predict = clf.predict(x_test)
print('朴素贝叶斯模型报告：')
print(classification_report(y_test, y_predict))
get_confusion_matrix('朴素贝叶斯')#绘制混淆矩阵


"""下面为对数据进行预测标注"""
def pre_data():
    """读取需要预测的数据进行整合"""
    data1 = pd.DataFrame()
    for file in fileList:
        data = pd.read_csv('./file/'+file, usecols=['Theme', 'title', 'content', ], low_memory=False)

        data1 = data1.append(data)

    return data1


data_pre=pre_data()

data_pre=data_pre.dropna(subset=['content'])#删除内容为空的数据

x_pre = count_vec.transform(data_pre['content'])

y_predict = clf.predict(x_pre)

data_pre['result']=y_predict
data_pre.to_excel('结果.xlsx',encoding='gbk')




