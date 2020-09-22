# coding = utf-8
import pandas as pd
import pyecharts.options as opts #全局配置和系列配置一定要导入的包
from pyecharts.charts import Line, Bar

if __name__ == "__main__":#从这里开始执行
    death_df = pd.read_excel('Daily cases.xlsx')
    death_df.fillna(0, inplace = True)
    # 存入df中并且处理时间数据 按时间段划分
    files = ['TheDailyTelegraph.csv', 'TheNewYorkTimes.csv', 'XinHua.csv']
    publisher_dic = {#映射
        'TheDailyTelegraph' : 'UK',
        'TheNewYorkTimes' : 'US',
        'XinHua' : 'China'
    }
    dates = []
    for file in files:#对三个file进行同样的操作
        df = pd.read_csv(file)
        publisher = file.split('.csv')[0]
        publish_date = list(df.publish_date.unique())#取去重之后的日期
        publish_date.sort()#排序
        c = Line()#折线图
        c.add_xaxis(publish_date)
        df_date = df[df.type == "international"]['publish_date'].value_counts().to_dict()#从第80行开始用
        dates.append(df_date)
        for type_name in ["national", "international"]:
            df_type_date = df[df.type == type_name]['publish_date'].value_counts().to_dict()#字典：键值对，键是日期，值是天数
            dic = {i : 0 for i in publish_date}#如果新闻量为0，则加入字典。来填补日期空缺
            for d in df_type_date:
                dic[d] = df_type_date[d]
            y = [dic[d] for d in publish_date]#构造Y轴，Y轴是列表
            c.add_yaxis(
                type_name + "_news",#图例的名字
                y,
                z = 2,#至于顶层
                is_smooth = True,#曲线是否圆滑，faulse非圆滑
                linestyle_opts = opts.LineStyleOpts(width = 2),
                markpoint_opts = opts.MarkPointOpts(data = [opts.MarkPointItem(type_ = "max", name = "最大值")],#最大值圆点配置
                    symbol_size = 40),
                label_opts = opts.LabelOpts(is_show = False)#不显示每个点的值
            )
        c.set_global_opts(#全局配置开始
            # title_opts = opts.TitleOpts(title = "The Development of COVID-19 News"),
            xaxis_opts = opts.AxisOpts(axislabel_opts = opts.LabelOpts (interval = 30), name = "Date",
                name_gap = 30),
            yaxis_opts = opts.AxisOpts(name_rotate = 90, name_location = "center", name_gap =
                30))
        c.extend_axis(yaxis = opts.AxisOpts(name_rotate = 90, name_location = "center", name_gap =
            60))#基于折线图扩展纵坐标，设置右边的纵坐标
        b = Bar()#开始画底层的柱状图
        b.add_xaxis(publish_date)
        #  for death_type in [publisher_dic[publisher], 'Global']:
        for death_type in [publisher_dic[publisher]]:#开始加daily cases柱状图
            y = []
            for day in publish_date:
                df_value = death_df[death_df['Date'] == day][death_type]#death_type是不同的国家
                if len(df_value) > 0:#57-60，把没有新闻量的日期设置为0
                    y.append(int(df_value))
                else:
                    y.append(0)
            b.add_yaxis(
                death_type + " daily cases",
                y,
                yaxis_index = 1,#放在底层
                itemstyle_opts = opts.ItemStyleOpts(color = 'orange', opacity = 0.9),#每根柱是什么样式
                markpoint_opts = opts.MarkPointOpts(data = [opts.MarkPointItem(type_ = "max", name = "最大值")],
                    symbol_size = 70),
                label_opts = opts.LabelOpts(is_show = False)
            )
        overlap = c.overlap(b)#两个图重合
        overlap.render(publisher + '.html')

    international_color_dic = {
        'UK' : '#c23531',
        'US' : '#2f4554',
        'China' : 'orange'
    }
    l = Line()
    publish_date = []
    for d in dates:#回应24、25行
        publish_date = list(set(publish_date + [ key for key in d]))
    publish_date.sort()
    l.add_xaxis(publish_date)

    for i in range(len(dates)):
        dic = dates[i]
        y = [ dic[d] if d in dic else 0 for d in publish_date]
        publisher = files[i].split('.csv')[0]
        country = publisher_dic[publisher]
        l.add_yaxis(
            country,
            y,
            z = 2,
            color = international_color_dic[country],
            linestyle_opts = opts.LineStyleOpts(width = 2),
            markpoint_opts = opts.MarkPointOpts(data = [opts.MarkPointItem(type_ = "max", name = "最大值")]),
            label_opts = opts.LabelOpts(is_show = False)
        )
    
    l.set_global_opts(
        # title_opts = opts.TitleOpts(title = "The Development of COVID-19 News"),
        xaxis_opts = opts.AxisOpts(axislabel_opts = opts.LabelOpts (interval = 30), name = "Date", name_gap = 30),
        yaxis_opts = opts.AxisOpts(name = "coverage number", name_rotate = 90, name_location = "center", name_gap = 30)
    )
    l.extend_axis(yaxis = opts.AxisOpts(name = "daily cases", name_rotate = 90, name_location = "center", name_gap = 60))
    b = Bar()
    b.add_xaxis(publish_date)
    y = []
    for day in publish_date:
        df_value = death_df[death_df['Date'] == day]['Global']#整合Excel中 Global列的死亡信息进去
        if len(df_value) > 0:
            y.append(int(df_value))
        else:
            y.append(0)
    b.add_yaxis(
        "global daily cases",
        y,
        yaxis_index = 1,
        itemstyle_opts = opts.ItemStyleOpts(color = 'grey', opacity = 0.9),
        markpoint_opts = opts.MarkPointOpts(data = [opts.MarkPointItem(type_ = "max", name = "最大值")],
            symbol_size = 70),
        label_opts = opts.LabelOpts(is_show = False)
    )
    overlap = l.overlap(b)
    overlap.render('combine.html')
