import pandas as pd 
from GetData import getData
from dealData import dealX
from dealFactors import Factor
from untils import plotTWodiffer
import matplotlib.pyplot as plt
def profit_and_Points(start=20101231,end=20231231):
    dataLoader = getData()
    monthes,values = dataLoader.getBoundProfit(start=start,end=end)
    profitFactor = Factor("农林牧渔净利润TTM环比增速",monthes,values)
    colums,monthes,values = dataLoader.\
        getmonthlydatas("dataSource\中信行业指数_农林牧渔_月_平均值.xlsx")
    pointFactor = Factor(colums[1],monthes,values[0])
    monthes = pointFactor.getCommentMonthes([profitFactor])
    # proFac = Factor(monthes,values)
    y1 = [pointFactor.month2Value[i] for i in monthes]
    y2 = [profitFactor.month2Value[i] for i in monthes]
    profitFactor.calCorrelationCoefficient(pointFactor,plot=True,K=3)
    # plotTWodiffer(monthes,y1,y2,
                #   "月份",pointFactor.name,profitFactor.name,K=3)
def plotprofitAndPoint(start=20101231,end=20231231):
    dataLoader = getData()
    monthes,values = dataLoader.getBoundProfit(start=start,end=end)
    profitFactor = Factor("农林牧渔净利润TTM环比增速",monthes,values)
    colums,monthes,values = dataLoader.\
        getmonthlydatas("dataSource\中信行业指数_农林牧渔_月_平均值.xlsx")
    
    pointFactor = Factor(colums[1],monthes,values[0])

    monthes = pointFactor.getCommentMonthes([profitFactor])
    print(monthes)
    monthes = [i for i in monthes if i.endswith(("12",'03','06','09'))]
    # proFac = Factor(monthes,values)
    y1 = [pointFactor.month2Value[i] for i in monthes]
    temdeal = dealX()
    y11 = y1
    # monthes,y11 = temdeal.do_value2Rate(monthes,y1)
    y2 = [profitFactor.month2Value[i] for i in monthes]
    # y1 = y1[1:]
    print(len(y11),len(y1),len(y2))
    newMonthes = monthes[1:]
    newValues = []
    colors = []
    for i in range(1,len(y11)):
        y1change = y11[i]-y1[i-1]
        y2change = y2[i]-y2[i-1]
        if y1change * y2change >=0:
            newValues.append(1)
            colors.append('pink')
        else:
            newValues.append(-1)
            colors.append("blue")
    plt.rcParams['font.sans-serif'] = ['simhei']###解决中文乱码
    plt.rcParams['axes.unicode_minus']=False

    temx = [i for i in range(len(newMonthes))]
    fig = plt.figure()
    ax2 = fig.add_subplot()

    Acolors = {'同向变化':'pink', '反向变化':'blue'}         
    labels = list(Acolors.keys())
    handles = [plt.Rectangle((0,0),1,1, color=Acolors[label]) for label in labels]
    ax2.legend(handles, labels)

    
    p2 = ax2.bar(temx, newValues,color=colors)
    ax2.grid(False) # turn off grid #2
    # ax2.set_ylabel(y2Name)
    # ax2.legend([y2Name], loc="upper center",ncol=1)
    # ax2.yaxis.label.set_color(p2.get_color())
    ax2.yaxis.label.set_fontsize(14)
    # ax2.tick_params(axis='y', colors=p2.get_color(), labelsize=8)
    # fig.add_subplot(ax2)
    ax1 = ax2.twinx() 
    p1, = ax1.plot(temx, y1[1:],color='red',marker='o') 
    ax1.set_ylabel("行业指数")
    # ax1.set_ylim(0, 25)
    ax1.legend(["行业指数"], loc="upper left")
    ax1.yaxis.label.set_color(p1.get_color())
    ax1.yaxis.label.set_fontsize(14)
    ax1.tick_params(axis='y', colors=p1.get_color(), labelsize=8)
    # x = lessXticks(newValues,1)

    ax2.set_xticks(temx,newMonthes,rotation=90,fontsize=8)
    plt.xlabel("日期")
    
    plt.show()
    
def calCapCorr_profit_and_points():
    dataLoader = getData()
    gapMonthes = [20090930,20151231,20160930,20181231,20190930,20210630,20211231,20220931,20231231]
    for(index,content) in enumerate(gapMonthes[1:]):
        start,end = gapMonthes[index],content
        # print(start,end)
        monthes,values = dataLoader.getBoundProfit(start,end)
        # print(monthes)
        profitFactor = Factor("农林牧渔净利润TTM环比增速",monthes,values)
        # print(profitFactor.name)
        colums,monthes,values = dataLoader.\
            getmonthlydatas("dataSource\中信行业指数_农林牧渔_月_平均值.xlsx")
        pointFactor = Factor(colums[1],monthes,values[0])
        profitFactor.calCorrelationCoefficient(pointFactor,plot=True)
if __name__ =="__main__":
    # profit_and_Points(20151231)
    ## 这边要计算出好的结果，需要不修正，只进行remove，不进行 平滑处理
    plotprofitAndPoint()
    # profit_and_Points(20091231,20230930)
    # profit_and_Points(20091231,20210930)
    # profit_and_Points(20091231,20230930)
    # profit_and_Points(20151231,20210930)
    # profit_and_Points(20061231,20090930)
    # profit_and_Points(20121231,20150930)
    # profit_and_Points(20151231,20180930)
    # profit_and_Points(20181231,20210930)
    # profit_and_Points(20220331,20230930)
    # calCapCorr_profit_and_points()
    
