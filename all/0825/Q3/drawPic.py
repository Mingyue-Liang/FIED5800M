# encoding = utf8
import os
import copy
import traceback
import pandas as pd
import pyecharts.options as opts
from pyecharts.charts import Pie, Line, Page
from pyecharts.globals import CurrentConfig
CurrentConfig.ONLINE_HOST = "./"

SENTIMENT_FILES = ['TheDailyTelegraph_sentiment_result.csv', 'TheNewYorkTimes_sentiment_result.csv', 'XinHua_sentiment_result.csv']
Q2_FILES = ['TheDailyTelegraph_national_topic_duration_result.csv', 'TheNewYorkTimes_national_topic_duration_result.csv', 'XinHua_national_topic_duration_result.csv']
sentiment_color_dic = {
    'neutral' : '#2f4554',
    'negative' : '#c23531',
    'positive' : 'orange'
}

def make_folder(folder):
    if not os.path.isdir(folder):
        os.makedirs(folder)

if __name__ == "__main__":
    try:
        curpath = os.path.dirname(__file__)
        for file in SENTIMENT_FILES:
            publisher = file.split('_')[0]
            path = os.path.join(curpath, file)
            df = pd.read_csv(path)
            print("%s : %d items" % (publisher, len(df)))

            l = Line()
            publish_date = list(df.publish_date.unique())
            publish_date.sort()
            l.add_xaxis(publish_date)

            publish_data, y = {}, {}
            for sentiment_type in sentiment_color_dic.keys():
                df_s = copy.deepcopy(df[df.sentiment_result == sentiment_type])
                df_date = df_s['publish_date'].value_counts().to_dict()
                publish_data[sentiment_type] = [df_date[d] if d in df_date else 0 for d in publish_date]
                y[sentiment_type] = []
            for i in range(len(publish_date)):
                num = 0
                for sentiment_type in sentiment_color_dic.keys():
                    num += publish_data[sentiment_type][i]
                for sentiment_type in sentiment_color_dic.keys():
                    if num > 0:
                        y[sentiment_type].append((publish_data[sentiment_type][i] / num) * 100)
                    else:
                        y[sentiment_type].append(0)
            for sentiment_type in sentiment_color_dic.keys():
                l.add_yaxis(
                    sentiment_type,
                    y[sentiment_type],
                    # color = sentiment_color_dic[sentiment_type],
                    stack = 'stack1',
                    areastyle_opts = opts.AreaStyleOpts(opacity = 1),
                    label_opts = opts.LabelOpts(is_show = False)
                )
            l.set_global_opts(
                # title_opts = opts.TitleOpts(title = "The sentiment development of %s" % folder.split('_')[0]),
                xaxis_opts = opts.AxisOpts(axislabel_opts = opts.LabelOpts(interval = 3, rotate = 45), name = "Date"),
                yaxis_opts = opts.AxisOpts(max_ = 100)
            )
            html_name = os.path.join(curpath, publisher + '_lineChart.html')
            l.render(html_name)

            for type_name in ['national', 'international']:
                data, color = [], []
                t_df = df[df['type'] == type_name]
                for k,v in sentiment_color_dic.items():
                    num = len(t_df[t_df['sentiment_result'] == k])
                    value = round((num / len(t_df)), 2) * 100
                    data.append((k , value))
                    color.append(v)
                    print("%s - %s - %s: %d items" % (publisher, type_name, k, num))
                p = Pie()
                p.add(series_name = "sentiment distribution", data_pair = data)
                p.set_series_opts(label_opts = opts.LabelOpts(formatter = "{b}: {d}%", font_size = 13, font_weight =
                    'bolder'))
                p.set_colors(color)
                p.set_global_opts(
                    legend_opts = opts.LegendOpts(orient = 'vertical', pos_right = 80, pos_top = 'middle', item_gap
                        = 20, padding = 20, textstyle_opts = opts.TextStyleOpts(font_size = 13, font_weight =
                            'bolder'))
                )
                html_name = os.path.join(curpath, publisher + '_' + type_name + '_pieChart.html')
                p.render(html_name)

            # save_folder = publisher + "_topic_duration_pic"
            # make_folder(save_folder)
            path = os.path.join(curpath, publisher + "_national_topic_duration_result.csv")
            t_df = pd.read_csv(path)
            topics = list(t_df.topic.unique())
            durations = list(t_df.duration.unique())
            page = Page(layout = Page.SimplePageLayout)
            for i in range(len(durations)):
                for j in range(len(topics)):
                    duration, topic = durations[i], topics[j]
                    dt_df = t_df[(t_df.duration == duration) & (t_df.topic == topic)]
                    cur_df = pd.concat([dt_df, df], axis = 1, join = 'inner')
                    #  if len(cur_df) == 0:
                        #  continue
                    data, color = [], []
                    for k,v in sentiment_color_dic.items():
                        num = len(cur_df[cur_df.sentiment_result == k])
                        value = round((num / len(cur_df)), 2) * 100
                        data.append((k , value))
                        color.append(v)
                        print("%s - national - %s - %s - %s : %d items" % (publisher, duration, topic, k, num))
                    p = Pie()
                    name = duration + '-' + topic
                    p.add(
                        series_name = name,
                        data_pair = data,
                        radius = ["30%", "75%"],
                        #  rosetype = "radius"
                    )
                    p.set_series_opts(label_opts = opts.LabelOpts(formatter = "{b}: {d}%", font_size = 13, font_weight =
                        'bolder'))
                    p.set_colors(color)
                    p.set_global_opts(
                        title_opts = opts.TitleOpts(title = name, padding = 20, pos_left = 'center', pos_top = -20),
                        legend_opts = opts.LegendOpts(orient = 'vertical', pos_right = 80, pos_top = 'middle', item_gap
                            = 20, padding = 20, textstyle_opts = opts.TextStyleOpts(font_size = 13, font_weight =
                                'bolder'))
                    )
                    page.add(p)
            page.render(publisher + '_national_topic_duration.html')

    except Exception as e:
        print('Error: ', e)
        traceback.print_exc()
