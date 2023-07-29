'''
    进行更多的研究
'''
import numpy as np
import pandas as pd
from GetData import getData
from dealData import dealX,dealY
from dealFactors import Factor
from mainModel import showFactors
from collections import defaultdict
from untils import fixFactorContent,handleOutliers,plotManyLines,showBunchRegressonResult

def getCPIWater():
        # 组装 foodCpi 细分
    dataLoader,CpiFactors = getData(),[]
    colums,monthes,values = dataLoader.\
        getmonthlydatas("dataSource\中国_CPI_食品细分_环比.xlsx")
    # monthes = monthes[150:270]
    # values = [i[150:270] for i in values]
    monthes = monthes[150:]
    values = [i[150:] for i in values]
    temDealX = dealX()
    for (index,oneValue) in enumerate(values):
        temM,temV = temDealX.do_TTM(monthes,oneValue)
        CpiFactors.append(
            Factor(f"{colums[index+1]}_TTM",temM,temV)
            # Factor(colums[index+1],monthes,oneValue)
        )
    CpiFactors = CpiFactors[1:]
    for i in CpiFactors:
        print(i.name)
    return CpiFactors[2]
#水产品CPI的合成
def getWaterMeatCPI():
    dataloader = getData()
    detailF = []
    temDealx = dealX()
    colums,monthes,values = dataloader.getmonthlydatas\
        ("dataSource\水产品类_细分_月_平均值.xlsx")
    temM,temV = fixFactorContent(monthes,values[0])
    allWF = Factor(colums[1],temM,temV)
    for index in range(len(values)-1):
        temM,temV = monthes,values[index+1]
        temM,temV = fixFactorContent(temM,temV)
        detailF.append(Factor(colums[index+2],temM,temV))
    showFactors(detailF)
    showFactors([allWF])
    params = allWF.doMutiRgression(detailF,K=3)
    a,params = params[0],params[1:]
    monthes = detailF[0].getCommentMonthes(detailF)
    newV = []
    for oneMonth in monthes:
        if oneMonth in allWF.monthes:
            newV.append(allWF.month2Value[oneMonth])
        else:
            newV.append(sum(
                [detailF[i].month2Value[oneMonth]*params[i] for i in range(len(params))]
            )+a)
    newAW =Factor("拟合后的水产",monthes,newV)
    newAW = newAW.genePartFactor(start='2010-01',end='2023-03')
    cpi = getCPIWater()
    newAW.calCorrelationCoefficient(cpi,plot=True,K=3)
    cpi.doRegression(newAW,plot=True)
    

    

# 猪肉和鸡肉更短的时间
def profitTMM_and_realFactors(filePos ="dataSource\鸡_自变量.xlsx",bound=True):
    dataLoader = getData()
    monthes,values = dataLoader.getBoundProfit(20152131,20231231)
    # monthes,values = dataLoader.getBoundProfit(20091231,20152131)
    profitTMMFactor = Factor("净利润TTM环比增速",monthes,values)
    plotManyLines(monthes,[values],"月份","增长率",legend=["净利润TTM"])
    colums,monthes,values = dataLoader.\
        getmonthlydatas(filePos)
    pigFactors = []
    temDeal = dealX()
    for (index,oneCOl) in enumerate(colums[1:]):
        teM,temV = fixFactorContent(monthes,values[index])
        temV = handleOutliers(temV)
        teM,temV = temDeal.do_value2Rate(teM,temV)
        teM,temV = temDeal.do_TTM(teM,temV)
        pigFactors.append(
            Factor(f"{oneCOl}_TTM",teM,temV)
        )
    # showPig = [1,2,1,3,1,12]#猪
    # showPig = [10,12,6,8,1]#鸡
    # showPig = [0,0,0,0,5,9]#猪延长
    # showPig = [16,15,0,4,11]#鸡延长
    #进行同期和跨期的回2测
    for (index,oneFactor) in enumerate(pigFactors):
        oneFactor.doRegression(profitTMMFactor,plot=True)
        res = oneFactor.doBunchValueRight(12,profitTMMFactor,plot=False)
        showBunchRegressonResult(res)
        # res2 = oneFactor.doBunchValueLight(12,profitTMMFactor,plot=False)
        # showBunchRegressonResult(res2)
        oneFactor.calCorrelationCoefficient(profitTMMFactor,plot=True,K=3)
        
def getFixedProfit():
    dataloader = getData()
    monthes,values = dataloader.getBoundProfit(20200331,20231231)

#每个三级行业的百分比
def showThridIndusrtyPercent():
    df = pd.read_csv("dataSource/swCompanyReportDetail.csv")
    
    dates =sorted(list(set( df["REPORT_PERIOD"].to_list())))
    industryNames =sorted(list(set( df["INDUSTRIESNAME"].to_list())))
    # print(dates,industryNames)
    date2industry2Profit = {}
    for oneDate in dates:
        date2industry2Profit[oneDate] = {}
        for oneIndu in industryNames:
            date2industry2Profit[oneDate][oneIndu] = []
    for row in df.itertuples():
        date2industry2Profit[row.REPORT_PERIOD][row.INDUSTRIESNAME].append(
            row.S_FA_EBT_TTM
        )
    values = []
    showDates = dates[60:]
    for oneDate in showDates:
        allProfit,temV = [],[]
        for oneIndu in industryNames:
            allProfit.extend(date2industry2Profit[oneDate][oneIndu])
        allProfit = abs(sum(allProfit))
        for oneIndu in industryNames:
            temV.append(sum(date2industry2Profit[oneDate][oneIndu])/allProfit)
        values.append(temV)
    values = np.array(values)
    values = values.T
    values = values.tolist()
    print(len(showDates),len(values),len(values[0]))
    # index1,index2 = industryNames.index("肉鸡养殖"), industryNames.index("生猪养殖")
    plotManyLines(showDates,values,"日期","净利润占比",industryNames)
    index1,index2 = industryNames.index("肉鸡养殖"), industryNames.index("生猪养殖")
    newV = [values[index1],values[index2]]
    newDates = [str(i) for i in showDates]
    newDates = [f"{i[:4]}-{i[4:6]}" for i in newDates]
    plotManyLines(newDates,newV,"日期","当季净利润占农林牧渔行业总利润占比",["肉鸡养殖","生猪养殖"],colors=["orange","cornflowerblue"])
    chickenFactor = Factor("肉鸡养殖利润占农林牧渔总利润百分比",newDates,newV[0])
    pigFactor = Factor("生猪养殖利润占农林牧渔总利润百分比",newDates,newV[1])
    print(showDates)
    pigFactor.calCorrelationCoefficient(chickenFactor,plot=True,K=1)
    newPigFactor = pigFactor.genePartFactor(start='2009-12',end='2015-12')
    newPigFactor2 = pigFactor.genePartFactor(start='2015-12',end='2023-12')
    newPigFactor.calCorrelationCoefficient(chickenFactor,plot=True,K=1)
    newPigFactor2.calCorrelationCoefficient(chickenFactor,plot=True,K=1)
    return showDates,values,industryNames

def reformatPigChicken():
    df = pd.read_csv("dataSource/swCompanyReportDetail.csv")
    chicken = df.loc[df["INDUSTRIESNAME"]=="肉鸡养殖"]
    chicken.to_csv("肉鸡养殖行业.csv",index=False,encoding="utf_8_sig")
    pig = df.loc[df["INDUSTRIESNAME"]=="生猪养殖"]
    pig.to_csv("生猪养殖行业.csv",index=False,encoding="utf_8_sig")


def compareChicken_pig():
    dataloader = getData()
    monthes,values = dataloader.getBoundProfit()
    profitFactor=Factor("netProfit_ttm",monthes,values)
    monthes,values = dataloader.getBoundProfit(filePos="dataSource\生猪养殖行业.csv")
    pigIndustryFactor = Factor("生猪养殖业净利润环比增速",monthes,values)
    monthes,values = dataloader.getBoundProfit(filePos="dataSource\肉鸡养殖行业.csv")
    chickenIndustryFactor = Factor("肉鸡养殖业净利润环比增速",monthes,values)
    print(monthes)
    profitFactor.calCorrelationCoefficient(pigIndustryFactor,plot=True,K=3)
    profitFactor.calCorrelationCoefficient(chickenIndustryFactor,plot=True,K=3)
    # profitFactor1 = profitFactor.genePartFactor(start='2009-12',end='2015-12')
    # profitFactor2 = profitFactor.genePartFactor(start='2015-12',end='2023-12')
    # profitFactor.calCorrelationCoefficient(pigIndustryFactor,plot=True)
    # profitFactor.calCorrelationCoefficient(chickenIndustryFactor,plot=True)
    # profitFactor1.calCorrelationCoefficient(pigIndustryFactor,plot=True)
    # profitFactor1.calCorrelationCoefficient(chickenIndustryFactor,plot=True)
    # profitFactor2.calCorrelationCoefficient(pigIndustryFactor,plot=True)
    # profitFactor2.calCorrelationCoefficient(chickenIndustryFactor,plot=True)
    # pigIndustryFactor1 = pigIndustryFactor.genePartFactor(start='2009-12',end='2015-12')
    # pigIndustryFactor2 = pigIndustryFactor.genePartFactor(start='2015-12',end='2023-12')
    # pigIndustryFactor.calCorrelationCoefficient(chickenIndustryFactor,plot=True,K=3)
    # pigIndustryFactor1.calCorrelationCoefficient(chickenIndustryFactor,plot=True,K=3)
    # pigIndustryFactor2.calCorrelationCoefficient(chickenIndustryFactor,plot=True,K=3)

    # colums,monthes,values = dataloader.\
    #     getmonthlydatas("dataSource\鸡_自变量.xlsx")
    # pigFactors = []
    # temDeal = dealX()
    # # temDealY = deaY()
    # for (index,oneCOl) in enumerate(colums[1:]):
    #     # print(oneCOl)
    #     teM,temV = fixFactorContent(monthes,values[index])
    #     temV = handleOutliers(temV)
    #     teM,temV = temDeal.do_value2Rate(teM,temV)
    #     teM,temV = temDeal.do_TTM(teM,temV)
    #     pigFactors.append(
    #         Factor(f"{oneCOl}_TTM",teM,temV)    
        # )
    # 重新计算鸡指标
    # for (index,oneFactor) in enumerate(pigFactors):
        # oneFactor1 = oneFactor.genePartFactor(start='2010-01',end='2015-12')
        # oneFactor2 = oneFactor.genePartFactor(start='2016-01',end='2023-12')
        # chickenIndustryFactor.calCorrelationCoefficient(oneFactor1,plot=True,K=1)
        # chickenIndustryFactor.calCorrelationCoefficient(oneFactor2,plot=True,K=1)
        # res = oneFactor1.doBunchValueRight(12,chickenIndustryFactor,plot=False)
        # showBunchRegressonResult(res)
        # res = oneFactor2.doBunchValueRight(12,chickenIndustryFactor,plot=False)
        # showBunchRegressonResult(res)
        # chickenIndustryFactor.calCorrelationCoefficient(oneFactor,plot=True,K=1)
        # res = oneFactor.doBunchValueRight(12,chickenIndustryFactor,plot=False)
        # showBunchRegressonResult(res)
    # colums,monthes,values = dataloader.getmonthlydatas("dataSource\饲料_月.xlsx")
    # chickenFeedM,chickenFeedV = fixFactorContent(monthes,values[0])
    # pigFeedM,pigFeedV = fixFactorContent(monthes,values[1])
    # chickenFeedF = Factor(colums[1],chickenFeedM,chickenFeedV)
    # chickenIndustryFactor.calCorrelationCoefficient(chickenFeedF,plot=True,K=3)

    # showDates,values,industryNames = showThridIndusrtyPercent()
    # index1,index2 = industryNames.index("肉鸡养殖"), industryNames.index("生猪养殖")
    # value1,value2 = values[index1],values[index2]
    # plotManyLines(showDates,[value1,value2],"日期","净利润占比",["肉鸡养殖","生猪养殖"])


    # for oneDate in date2industry2Profit:
    #     for oneInd in date2industry2Profit[oneDate]:
    #         print(oneDate,oneInd,date2industry2Profit[oneDate][oneInd])
    #     break
def calCheckenFeed():
    dataloader = getData()
    monthes,values = dataloader.getBoundProfit(filePos="dataSource\肉鸡养殖行业.csv")
    chickenIndustryFactor = Factor("肉鸡养殖业净利润环比增速",monthes,values)
    colums,monthes,values = dataloader.\
        getmonthlydatas("dataSource\鸡_自变量.xlsx")
    pigFactors = []
    temDeal = dealX()
    # temDealY = deaY()
    for (index,oneCOl) in enumerate(colums[1:]):
        # print(oneCOl)
        teM,temV = fixFactorContent(monthes,values[index])
        temV = handleOutliers(temV)
        teM,temV = temDeal.do_value2Rate(teM,temV)
        teM,temV = temDeal.do_TTM(teM,temV)
        pigFactors.append(
            Factor(f"{oneCOl}_TTM",teM,temV)    
        )
    for (index,oneFactor) in enumerate(pigFactors):
        chickenIndustryFactor.calCorrelationCoefficient(oneFactor,plot=True,K=1)
        res = oneFactor.doBunchValueRight(12,chickenIndustryFactor,plot=False)
        showBunchRegressonResult(res)

def calPigFeed():
    dataloader = getData()
    monthes,values = dataloader.getBoundProfit(filePos="dataSource\生猪养殖行业.csv")
    pigIndustryFactor = Factor("生猪养殖业净利润环比增速",monthes,values)
    colums,monthes,values = dataloader.\
        getmonthlydatas("dataSource\猪_自变量.xlsx")
    pigFactors = []
    temDeal = dealX()
    # temDealY = deaY()
    for (index,oneCOl) in enumerate(colums[1:]):
        # print(oneCOl)
        teM,temV = fixFactorContent(monthes,values[index])
        temV = handleOutliers(temV)
        teM,temV = temDeal.do_value2Rate(teM,temV)
        teM,temV = temDeal.do_TTM(teM,temV)
        pigFactors.append(
            Factor(f"{oneCOl}_TTM",teM,temV)    
        )
    # 重新计算鸡指标
    for (index,oneFactor) in enumerate(pigFactors):
        pigIndustryFactor.calCorrelationCoefficient(oneFactor,plot=True,K=1)
        res = oneFactor.doBunchValueRight(12,pigIndustryFactor,plot=False)
        showBunchRegressonResult(res)

# 获取某个行业profit
def getBoundIndusrtyProfit(industry="肉鸡养殖",start=20101000,end=20231231):
    # print(start,end)
    temDeal = dealY()
    df= pd.read_csv("dataSource\swCompanyReportDetail.csv")
    date2Company2Profit = defaultdict(dict)
    for row in df.itertuples():
        if row.REPORT_PERIOD >= start and \
            row.REPORT_PERIOD<=end and row.INDUSTRIESNAME==industry:
            date2Company2Profit[row.REPORT_PERIOD]\
                [row.S_INFO_COMPNAME] = row.S_FA_EBT_TTM
    _,valuePre = temDeal.quarterFix(date2Company2Profit,nextStep=1)
    #引入处理函数
    temDate,pf1 = temDeal.getProFitSelf(date2Company2Profit)
    temDeal = dealY()
    removes = temDeal.removeOutliers(date2Company2Profit)#等待手工剔除数据
    for onComOd  in removes:
        if onComOd[0] in list(date2Company2Profit.keys()):
            date2Company2Profit[onComOd[0]][onComOd[1]] = 0
        else:
            continue
    quaters,Aftervalues = temDeal.quarterFix(date2Company2Profit,nextStep=1)
    plotManyLines(quaters,[valuePre,Aftervalues],"日期","净利润环比增速",["剔除异常前","剔除异常后"])
    quaters,values = temDeal.quarterFix(date2Company2Profit,nextStep=1)
    for (index,oneQ) in enumerate(quaters):
        if str(oneQ).startswith('200612'):
            values[index] = (values[index-1]+values[index+1])/2
    plotManyLines(quaters,[Aftervalues,values],"日期","净利润环比增速",["修正前","修正后"])
    monthes,mValues = temDeal.quarter2Month(quaters,values)
    quaters = [f"{oneQuarter[:4]}-{oneQuarter[4:6]}" for oneQuarter in quaters]
    return monthes,mValues


def profitTMM_and_IndustryrealFactors(\
        filePos ="dataSource\鸡_自变量.xlsx",start=20101000,end=20231231):
    dataLoader = getData()
    monthes,values = getBoundIndusrtyProfit(start=start,end=end)
    print(monthes)
    profitTMMFactor = Factor("净利润TTM环比增速",monthes,values)
    plotManyLines(monthes,[values],"月份","增长率",legend=["净利润TTM"])
    colums,monthes,values = dataLoader.\
        getmonthlydatas(filePos)
    pigFactors = []
    temDeal = dealX()
    # temDealY = deaY()
    for (index,oneCOl) in enumerate(colums[1:]):
        # print(oneCOl)
        teM,temV = fixFactorContent(monthes,values[index])
        temV = handleOutliers(temV)
        teM,temV = temDeal.do_value2Rate(teM,temV)
        teM,temV = temDeal.do_TTM(teM,temV)
        pigFactors.append(
            Factor(f"{oneCOl}_TTM",teM,temV)    
        )
    # showPig = [1,2,1,3,1,12]#猪
    # showPig = [10,12,6,8,1]#鸡
    # showPig = [0,0,0,0,5,9]#猪延长
    # showPig = [16,15,0,4,11]#鸡延长
    #进行同期和跨期的回2测
    for (index,oneFactor) in enumerate(pigFactors):
        # oneFactor.doRegression(profitTMMFactor,plot=True)
        res = oneFactor.doBunchValueRight(13,profitTMMFactor,plot=False)
        showBunchRegressonResult(res)
        oneFactor.calCorrelationCoefficient(profitTMMFactor,plot=True,K=3)
        # showPerfetMonthChange(oneFactor,profitTMMFactor,showPig[index])


def dealMacroFactors(start=20101231,end=20231231,filePos="dataSource/中国_宏观变量).xlsx"):
    dataLoader = getData()
    temDealX = dealX()
    # monthes,values = dataLoader.getProfit(bound=bound)
    monthes,values = dataLoader.getBoundProfit(start,end)
    profitTMMFactor = Factor("netprofit_TTM",monthes,values)
    macroFactor = []
    colums,monthes,values = dataLoader.getmonthlydatas(filePos)
    for (index,content) in enumerate(colums[1:]):
        temM,temV = monthes,values[index]
        temV = handleOutliers(temV)
        temM,temV = temDealX.do_TTM(temM,temV)
        temM,temV = temDealX.do_value2Rate(temM,temV)
        macroFactor.append(Factor(content,temM,temV))
    for oneFactor in macroFactor:
        oneFactor = oneFactor.genePartFactor(start='2010-01',end='2023-03')
        oneFactor1 = oneFactor.geneFactorValueLeft(11)
        res = oneFactor.doBunchValueLight(18,profitTMMFactor,plot=False)
        showBunchRegressonResult(res)
        # oneFactor.calCorrelationCoefficient(oneFactor1,plot=True)
        
        profitTMMFactor.calCorrelationCoefficient(oneFactor,plot=True,K=3)        
        profitTMMFactor.calCorrelationCoefficient(oneFactor1,plot=True,K=3)
        # profitTMMFactor.calCorrelationCoefficient(oneFactor1,plot=True,K=3)

def chickenProfit_and_cpi_regression(start=20101000,end=20231231):
    dataLoader = getData()
    monthes,values = dataLoader.getBoundProfit(filePos="dataSource\肉鸡养殖行业.csv")
    chickenIndustryFactor = Factor("肉鸡养殖业净利润环比增速",monthes,values)
    monthes,values = dataLoader.getfoodCPITTM()
    temDeal = dealX()
    # monthes,values = temDeal.do_value2Rate(monthes,values)
    # monthes,values = temDeal.do_TTM(monthes,values)
    foodCPI = Factor("食品CPI",monthes,values)
    chickenIndustryFactor.calCorrelationCoefficient(foodCPI,plot=True,K=3)
    chickenIndustryFactor.doRegression(foodCPI,reverse=True,plot=True)

if __name__ == "__main__":
    # getCPIWater()
    getWaterMeatCPI()
    # profitTMM_and_realFactors()
    # profitTMM_and_realFactors(filePos="dataSource\猪_自变量.xlsx")
    # getFixedProfit()
    # calCheckenFeed()
    # calPigFeed()
    # showThridIndusrtyPercent()
    # reformatPigChicken()
    # compareChicken_pig()
    # getBoundIndusrtyProfit()
    # profitTMM_and_IndustryrealFactors(start=20091231,end=20151231)
    # profitTMM_and_IndustryrealFactors(start=20151231,end=20231231)

    # dealMacroFactors()
    chickenProfit_and_cpi_regression()