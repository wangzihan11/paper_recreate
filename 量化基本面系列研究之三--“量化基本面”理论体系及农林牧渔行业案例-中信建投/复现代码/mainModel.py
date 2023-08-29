import sys
sys.path.append(r"C:\Users\wzh\Desktop\reportResearch")
from GetData import getData
from statistics import quantiles
from dealFactors import Factor
import pandas as pd
from dealData import dealX
from prettytable import PrettyTable
import matplotlib.pyplot as plt
from untils import fixFactorContent,handleOutliers,plotInsert,plotManyLines,lessXticks

# 平滑处理x缺省值
def loadBunchFactors(filePos,deal=False):
    temFactors = []
    dataLoader = getData()
    temdeal = dealX()
    colums,monthes,values = dataLoader.getmonthlydatas(filePos)
    for (index,oneValue) in enumerate(values):
        temM,temV = fixFactorContent(monthes,oneValue)
        temV = handleOutliers(temV)
        if deal == True:
            temM,temV = temdeal.do_value2Rate(temM,temV)
            temM,temV = temdeal.do_TTM(temM,temV)
        temFactors.append(
            Factor(colums[index+1],temM,temV)
        )
    return temFactors

def showFactors(factors):
    table = PrettyTable()
    table.field_names = ["name","startM","endM"]
    for oneFactor in factors:
        table.add_row([
            oneFactor.name,oneFactor.monthes[0],oneFactor.monthes[-1]
        ])
    print(table)
        
def parepareXFactors():
    XFactors = []
    # 首先准备  自变量
    XFactors.extend(loadBunchFactors("dataSource\中国_CPI_食品细分_环比 - 副本.xlsx"))
    XFactors.extend(loadBunchFactors("dataSource\猪_自变量.xlsx",deal=True))
    XFactors.extend(loadBunchFactors("dataSource\鸡_自变量 - 副本.xlsx",deal=True))
    XFactors.extend(loadBunchFactors("dataSource\饲料_月.xlsx"))
    XFactors.extend(loadBunchFactors("dataSource\进出口 - 副本.xlsx"))
    XFactors.extend(loadBunchFactors("dataSource\产量 - 副本.xlsx"))
    XFactors.extend(loadBunchFactors("dataSource\中国_宏观变量) - 副本.xlsx"))
    # XFactors.extend(loadBunchFactors("dataSource\其他变量+产量相关.xlsx"))
    # XFactors.extend(loadBunchFactors("dataSource\其他变量+宏观变量.xlsx"))
    # XFactors.extend(loadBunchFactors("dataSource\其他变量+中国_进口数量.xlsx"))
    return XFactors
    #接着准备 因变量
    

    #进行回归拟合
    
def parepareYFactor(bound=True):
    dataLoader = getData()
    # monthes,values = dataLoader.getProfit(bound=bound)
    monthes,values  = dataLoader.getBoundProfit()
    profitTMMFactor = Factor("netprofit_TTM",monthes,values)
    return profitTMMFactor

def doPredictionAndShow(XFactors:list,Ydo:Factor,Yreal:Factor,K=1,preMothes=""):
    commenM = Ydo.getCommentMonthes(XFactors)
    params = Ydo.doMutiRgression(XFactors)

    canDoMonthes = XFactors[0].getCommentMonthes(XFactors)

    preMonthes = [i for i in Yreal.monthes if i in canDoMonthes]
    print("comment+=================")
    print(canDoMonthes,preMonthes)
    
    predictY = []
    a,params = params[0],params[1:]
    for oneMonth in preMonthes:
        predictY.append(sum(
            [XFactors[i].month2Value[oneMonth]*params[i] for i in range(len(params))]
        )+a)
    #展示预测值
    realY = [Yreal.month2Value[i] for i in preMonthes]
    plotPredictModel(preMonthes,[predictY,realY],
        "月份","netprofit_TTM",["拟合","真实"],K=K,gapMoth=commenM[-1])

# def dopredict


# def predictValues(params,a,preMonthes,reaMonthes,realY,XFactors):
#     # 预测这
#     predictY = []
#     for oneMonth in preMonthes:
#         predictY.append(sum(
#             [XFactors[i].month2Value[oneMonth]*params[i] for i in range(len(params))]
#         )+a)
    #展示真实值
    # dealResult(preMonthes,realY,predictY,commenM[-1])


    # plotInsert(Ydo.,Y2Pre.monthes,Ydo.values)

def plotPredictModel(x,ys,xlabel,ylabel,legend,title="",K=1,gapMoth=""):
    plt.rcParams['font.sans-serif'] = ['simhei']###解决中文乱码
    plt.rcParams['axes.unicode_minus']=False
    temx = [i+1 for i in range(len(x)) ]
    for oney in ys:
        plt.plot(temx, oney, marker='o', markersize=3) 
        
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend(legend)
    # plt.legend(legend,loc = (1 , 0)) 
    if gapMoth != "":
        nowGap = x.index(gapMoth)
        plt.vlines([nowGap],-0.3,0.3,colors='red',linestyles='dashed')
    x = lessXticks(x,K)
    plt.xticks(temx,x,rotation=90)
    plt.title(title)
    plt.show()
    pass

def plotPredictModel2(xpre,ypre,xreal,yreal,xlabel,ylabel,legend,title="",K=1,gapMoth="",differ=6):
    print("==============start show")
    # print(xreal)
    # print(xpre)
    plt.rcParams['font.sans-serif'] = ['simhei']###解决中文乱码
    plt.rcParams['axes.unicode_minus']=False
    temx = [i for i in range(len(xpre)) ]
    plt.plot(temx, ypre, marker='o', markersize=3)
    # temxReal = [xpre.index(i) for i in xreal if i in xpre]
    # temY = [ yreal[i] for i in temxReal] 
    plt.plot([ i for i in range(len(xreal[differ:]))],yreal[differ:], marker='*', markersize=3)
    # for oney in ys:
    #     plt.plot(temx, oney, marker='o', markersize=3) 
        
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend(legend)
    # plt.legend(legend,loc = (1 , 0)) 
    if gapMoth != "":
        nowGap = xpre.index(gapMoth)
        plt.vlines([nowGap],-0.2,0.3,colors='red',linestyles='dashed')
    xpre = lessXticks(xpre,K)
    plt.xticks(temx,xpre,rotation=90)
    plt.title(title)
    plt.show()
    pass
def findMildeIndex(x,xs:list):
    for(index,content) in enumerate(xs):
        if x <= content:
            return index
    return len(xs)

def dealResult(monthes,realY,dealY,gapMonth,gap=3,gapName=["衰退","平稳","景气"]):
    # temX = realY
    # temX.extend(dealY)
    # temX = [i for i in realY if i !="space"]
    temX = [i for i in dealY if i !="space"]
    # print(realY,dealY)
    # print(realY,dealY)
    # temIndex = monthes.index(gapMonth)
    df = pd.DataFrame()
    temQ  = quantiles(temX, n=gap, method='inclusive')
    print(temQ)
    outTable = PrettyTable()
    outTable.field_names = ['月份',"真实","预测"]
    index = 0
    for (real,deal) in zip(realY,dealY):
        if monthes[index]==gapMonth:
            outTable.add_row(['','',""])
            df["gap"] = ["___","接下来","预测值"]
        if real == "space":
            df[index] = [monthes[index],"",gapName[findMildeIndex(deal,temQ)]]
            outTable.add_row([
                monthes[index],"",gapName[findMildeIndex(deal,temQ)]
            ])
        else:
            print("real deal is================")
            print(real,deal)
            df[index] = [monthes[index],gapName[findMildeIndex(real,temQ)],gapName[findMildeIndex(deal,temQ)]]
            outTable.add_row([
                monthes[index],gapName[findMildeIndex(real,temQ)],gapName[findMildeIndex(deal,temQ)]
            ])
        index += 1
    
    df = df.T
    df.columns = ["月份","真实","预测"]
    df = df.T
    df.to_csv("res.csv",index=False,encoding='utf_8_sig')
    print(outTable)

def allKindModel(start,have,predict=20231231,K=1):
    dataloader = getData()
    XFactors = parepareXFactors()
    XFactors = [i.geneFactorValueRight(6) for i in XFactors]
    print(XFactors[0].monthes)
    # XFactors = [i for i in XFactors if not i.name.startswith("(停止)")]
    # for i in XFactors:
        # i.predictRightMonthes()
    showFactors(XFactors)
    print(XFactors[0].getCommentMonthes(XFactors))
    for onFactor in XFactors:
        if "2023-01" not in onFactor.monthes:
            print(onFactor.name) 
    
    # YdoFactor = parepareYFactor()
    monthes,values = dataloader.getBoundProfit(start,have)
    # print(monthes)
    # print("预测")
    YdoFactor = Factor("预测",monthes,values)

    monthes,values = dataloader.getBoundProfit(start,predict)
    # print(monthes)
    # print("真实")
    # Yreal = parepareYFactor(bound=False)
    Yreal = Factor("真实",monthes,values)
    showFactors([YdoFactor,Yreal])
    # print(YdoFactor.getCommentMonthes([Yreal]))
    # print(XFactors[0].getCommentMonthes(XFactors))
    # for i in XFactors:
    #     if '2014-01' not in i.monthes:
    #         print(i.name)
    doPredictionAndShow(XFactors,YdoFactor,Yreal,K=K)

def doooooooPredict():
    differ=6
    dataloader = getData()
    XFactors = parepareXFactors()
    
    # XFactors = [i.geneFactorValueRight(6) for i in XFactors]
    # print(XFactors[0].monthes)
    # XFactors = [i for i in XFactors if not i.name.startswith("(停止)")]
    XFactors[-1].predictRightMonthes(K=1)
    showFactors(XFactors)
    
    monthes,values = dataloader.getBoundProfit()
    Yreal = Factor("真实",monthes,values)
    realMonthes = Yreal.getCommentMonthes(XFactors)
    values =[ Yreal.month2Value[i] for i in realMonthes]
    for i in XFactors:
        i.predictRightMonthes(K=differ)
    showFactors(XFactors)
    params = Yreal.doMutiRgression(XFactors)
    a,params = params[0],params[1:]
    commenMonthes = XFactors[0].getCommentMonthes(XFactors)
    preValues = []
    for oneMonth in commenMonthes:
        preValues.append(
            sum([XFactors[i].month2Value[oneMonth]*params[i] for i in range(len(params))])+a
        )
    print(realMonthes,commenMonthes)
    plotPredictModel2(commenMonthes,preValues,realMonthes,
                      values,"月份","netprofit_TTM",["拟合","真实"],K=3,gapMoth=monthes[-1],differ=differ)
    realY = []
    for i in commenMonthes:
        if i in Yreal.monthes:
            realY.append(Yreal.month2Value[i])
        else:
            realY.append("space")
    # realY = [Yreal.month2Value[i] for i in commenMonthes  if i in Yreal.monthes]
    dealResult(commenMonthes,realY,preValues,Yreal.monthes[-1])

def doooooooPredictChecken(differ=3):
    differ=differ
    dataloader = getData()
    XFactors = []
    # 首先准备  自变量
    XFactors.extend(loadBunchFactors("dataSource\中国_CPI_食品细分_环比 - 副本.xlsx"))
    XFactors = XFactors[:-1]
    XFactors.extend(loadBunchFactors("dataSource\鸡_自变量 copy.xlsx",deal=True))
    XFactors = [i.genePartFactor('2010-01','2023-03') for i in XFactors]
    monthes,values = dataloader.getBoundProfit(filePos="dataSource\肉鸡养殖行业.csv")
    showFactors(XFactors)
    print("dopre",monthes)
    Yreal = Factor("真实",monthes,values)
    realMonthes = Yreal.getCommentMonthes(XFactors)
    print("真实的月份",realMonthes)
    values =[ Yreal.month2Value[i] for i in realMonthes]
    print(len(realMonthes),len(values))
    print(realMonthes[-1],values[-1])
    for i in XFactors:
        i.predictRightMonthes(K=differ)
    params = Yreal.doMutiRgression(XFactors)
    a,params = params[0],params[1:]
    commenMonthes = XFactors[0].getCommentMonthes(XFactors)
    preValues = []
    for oneMonth in commenMonthes:
        preValues.append(
            sum([XFactors[i].month2Value[oneMonth]*params[i] for i in range(len(params))])+a
        )
    plotPredictModel2(commenMonthes,preValues,realMonthes,
                      values,"月份","chicken_netprofit_TTM",["拟合","真实"],K=3,gapMoth=monthes[-1],
                      differ=differ)
    realY = []
    for i in commenMonthes:
        if i in Yreal.monthes:
            realY.append(Yreal.month2Value[i])
        else:
            realY.append("space")
    # realY = [Yreal.month2Value[i] for i in commenMonthes  if i in Yreal.monthes]
    dealResult(commenMonthes,realY,preValues,Yreal.monthes[-1])

if  __name__ == "__main__":
    # allKindModel(20101231,20161231,20171231)
    # allKindModel(20101231,20181231,20191231)
    # allKindModel(20101231,20211231,20231231)
    # allKindModel(20101231,20211231,20231231,K=3)
    # doooooooPredict()
    doooooooPredictChecken(differ=3)
    # for i in range(5):
    #     doooooooPredictChecken(differ=i+1)
    
   
    # allKindModel(20151231,20211231)
    # allKindModel(20101231,20171231,20201231)
    # allKindModel(20101231,20151231,20171231)


    




    # YdoFactor.doMutiRgression(XFactors)
    