# encoding = utf8
import os
import copy
import time
import traceback
import pandas as pd
import pyecharts.options as opts
from pyecharts.charts import Line, Bar
from cluster import Topic_dic

PUBLISHERS = ['TheDailyTelegraph', 'TheNewYorkTimes', 'XinHua']

Duration_dic = {
    'TheDailyTelegraph' : [['2020-01-22', '2020-03-23', 'incubation'], ['2020-03-24', '2020-05-02', 'outbreak'],
        ['2020-05-03', '2020-06-30', 'spread'], ['2020-07-01', '2020-07-23', '2nd outbreak']],
    'TheNewYorkTimes' : [['2020-01-21', '2020-03-16', 'incubation'], ['2020-03-17', '2020-05-05', 'outbreak'],
        ['2020-05-06', '2020-06-24', 'spread'], ['2020-06-25', '2020-07-23', '2nd outbreak']],
    'XinHua' : [['2020-01-15', '2020-01-23', 'incubation'], ['2020-01-24', '2020-02-13', 'outbreak'],
        ['2020-02-14', '2020-04-19', 'spread'], ['2020-04-20', '2020-07-27', 'recovery']]
}

topic_color_dic = {
    'Health' : '#c23531',
    'Politics' : '#2f4554',
    'Economy' : 'orange',
    'Others' : 'grey'
}

if __name__ == "__main__":
    try:
        curpath = os.path.dirname(__file__)
        for publisher in PUBLISHERS:
            for type_name in ['national', 'international']:
                path = os.path.join(curpath, publisher + '_topic_result.csv')
                df = pd.read_csv(path)
                df = df[df['type'] == type_name]
                df.sort_values(by = 'publish_date', inplace = True)
                print("%s - %s : %d items" % (publisher, type_name, len(df)))

                c = Line()
                publish_date = list(df.publish_date.unique())
                publish_date.sort()
                c.add_xaxis(publish_date)

                dic = Topic_dic[publisher]
                for topic in dic.values():
                    df_t = copy.deepcopy(df[df.topic == topic])
                    df_date = df_t['publish_date'].value_counts().to_dict()
                    y = [df_date[d] if d in df_date else 0 for d in publish_date]
                    c.add_yaxis(
                        topic,
                        y,
                        color = topic_color_dic[topic],
                        linestyle_opts = opts.LineStyleOpts(width = 2),
                        markpoint_opts = opts.MarkPointOpts(data = [opts.MarkPointItem(type_ = "max", name = "最大值")]),
                        label_opts = opts.LabelOpts(is_show = False)
                    )

                c.set_global_opts(
                    # title_opts = opts.TitleOpts(title = "The sentiment development of %s" % folder.split('_')[0]),
                    xaxis_opts = opts.AxisOpts(axislabel_opts = opts.LabelOpts(rotate = 45), name="Date"))
                html_name = os.path.join(curpath, publisher + '_' + type_name + '_topic_LineChart.html')
                c.render(html_name)

                d_list = []
                for index, row in df.iterrows():
                    if publisher == 'TheNewYorkTimes': 
                        publish_date_stamp = time.mktime(time.strptime(row['publish_date'], "%Y-%m-%d"))
                    else:
                        publish_date_stamp = time.mktime(time.strptime(row['publish_date'], "%Y/%m/%d"))
                    for item in Duration_dic[publisher]:
                        start_date_stamp = time.mktime(time.strptime(item[0], "%Y-%m-%d"))
                        end_date_stamp = time.mktime(time.strptime(item[1], "%Y-%m-%d"))
                        if publish_date_stamp >= start_date_stamp and publish_date_stamp <= end_date_stamp:
                            df.loc[index, 'duration'] = item[2]
                            if item[2] not in d_list:
                                d_list.append(item[2])
                            break
                b = Bar()
                b.add_xaxis(d_list)
                for value in Topic_dic[publisher].values():
                    d_num = []
                    for duration in d_list:
                        t_df = df[(df['topic'] == value) & (df['duration'] == duration)]
                        sum_df = df[df['duration'] == duration]
                        d_num.append(round(len(t_df)*100/len(sum_df), 1))
                    b.add_yaxis(
                        value,
                        d_num,
                        itemstyle_opts = opts.ItemStyleOpts(color = topic_color_dic[value]),
                        label_opts = opts.LabelOpts(formatter = "{c}%")
                    )
                    b.set_global_opts(
                         yaxis_opts = opts.AxisOpts(axislabel_opts=opts.LabelOpts(formatter="{value}%")
                    ))
                     #b.set_global_opts(
                        # title_opts = opts.TitleOpts(title = "The sentiment development of %s" % folder.split('_')[0]),
                        #  xaxis_opts = opts.AxisOpts(axislabel_opts = opts.LabelOpts(interval = 3, rotate = 45), name = "Date"))
                    html_name = os.path.join(curpath, publisher + '_' + type_name + '_topic_BarChart.html')
                    b.render(html_name)

                csv_name = os.path.join(curpath, publisher + '_' + type_name + '_topic_duration_result.csv')
                df.to_csv(csv_name, index = False, encoding = 'utf_8_sig')

    except Exception as e:
        print('Error: ', e)
        traceback.print_exc()
