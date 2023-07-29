# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 15:03:53 2023

@author: fksx2

# 用于获取数据，这些数据可能是从外部爬到，也可以是文件读入
"""
#==========================依赖项====================================
import sys
import pandas as pd
# import seaborn as sns
# import cx_Oracle
sys.path.append("C:/Users/fksx2/reportResearch/")
from untils import connect_database,plotTWodiffer,plotManyLines,plotInsert,fixFactorContent,getDealNegativeNumberK
from collections import defaultdict
from dealData import dealX,dealY

#==========================类的设计====================================
class getData:
    # 是方法的整合而不是复用
    def __init__(self):
        pass
    def getProfit(self,industyName="农林牧渔",bound=True):#获取因变量#每个季度行业净利润
        temDeal = dealY()
        # date2Profits,chapterAP = defaultdict(list),[]
        # conn = connect_database()
        # sql = f'''
        #  select b.s_info_windcode,e.S_INFO_COMPNAME,c.industriesalias,
        #      c.industriesname,c.industriescode,m.REPORT_PERIOD,
        #      m.S_FA_EBT_TTM,b.entry_dt,b.remove_dt
        #  from gfwind.AShareIndustriesClassCITICS b, gfwind.AShareIndustriesCode c ,
        #      gfwind.AShareDescription e ,gfwind.AShareTTMHis  m
        #  where substr(b.citics_ind_code, 1, 4) = substr(c.IndustriesCode, 1, 4)
        #      and e.S_INFO_WINDCODE = b.S_INFO_WINDCODE and b.cur_sign = '1'
        #      and c.used = '1' and c.levelnum = '2' and c.industriesname='农林牧渔'
        #      and e.S_INFO_WINDCODE = m.S_INFO_WINDCODE order by b.s_info_windcode ,m.REPORT_PERIOD desc
        # '''
        # df = pd.read_sql(sql,conn)
        # df.to_csv("净利润TMM+季度.csv")

        df= pd.read_csv("dataSource\净利润TMM+季度.csv")
        #形成核心变量
        date2Company2Profit = defaultdict(dict)
        if bound == True:
            for row in df.itertuples():
                if row.REPORT_PERIOD >= 20101000 and row.REPORT_PERIOD<20201131:
                    date2Company2Profit[row.REPORT_PERIOD]\
                        [row.S_INFO_COMPNAME] = row.S_FA_EBT_TTM
        else:
            for row in df.itertuples():
                if row.REPORT_PERIOD >= 20090630 and row.REPORT_PERIOD<20231231:
                    date2Company2Profit[row.REPORT_PERIOD]\
                        [row.S_INFO_COMPNAME] = row.S_FA_EBT_TTM
        print("dealPre======================")
        _,valuePre = temDeal.quarterFix(date2Company2Profit,nextStep=1)
        #引入处理函数
        print("start Remove==============")
        temDeal = dealY()
        removes = temDeal.removeOutliers(date2Company2Profit)#等待手工剔除数据
        # removes = []
        print(removes)
        print(list(date2Company2Profit.keys()))
        for onComOd  in removes:
            if onComOd[0] in list(date2Company2Profit.keys()):
                del date2Company2Profit[onComOd[0]][onComOd[1]] 
                # date2Company2Profit[onComOd[0]].pop(onComOd[1])
                # date2Company2Profit[onComOd[0]][onComOd[1]] = 0

        '''测试remove'''
       
        quaters,afterRemove = temDeal.quarterFix(date2Company2Profit,nextStep=1)
            # try:
            #     print(onComOd,date2Company2Profit[onComOd[0]][onComOd[1]])
            #     date2Company2Profit[onComOd[0]][onComOd[1]] = 0.01
            # except:
            #     continue
        print("after Remove==============")
        print(list(date2Company2Profit.keys()))
        
        quaters,values = temDeal.quarterFix(date2Company2Profit)
        quaters2,values2 = temDeal.quarterFix(date2Company2Profit,nextStep=1)
        
        plotManyLines(quaters,[valuePre,values],"日期","净利润环比增速",["剔除异常前","剔除异常前后"])
        plotManyLines(quaters,[values2,values],"日期","净利润环比增速",["修正前","修正后"])
        monthes,mValues = temDeal.quarter2Month(quaters,values)
        quaters = [f"{oneQuarter[:4]}-{oneQuarter[4:6]}" for oneQuarter in quaters]
        # plotInsert(monthes,quaters,mValues,values)
        # print(monthes)
        return monthes,mValues
    
    def getBoundProfit(self,start=20101000,end=20231231,filePos="dataSource\净利润TMM+季度.csv"):
        temDeal = dealY()
        temDealX = dealX()
        df= pd.read_csv(filePos)
        date2Company2Profit = defaultdict(dict)
        for row in df.itertuples():
            if row.REPORT_PERIOD >= start and row.REPORT_PERIOD<=end:
                date2Company2Profit[row.REPORT_PERIOD]\
                    [row.S_INFO_COMPNAME] = row.S_FA_EBT_TTM
        temDate,pf1 = temDeal.getProFitSelf(date2Company2Profit)
        addN = getDealNegativeNumberK(pf1)
        # addN = 0
        _,valueRemovePre = temDeal.quarterFix(date2Company2Profit,nextStep=1,dealK=addN)
        #引入处理函数
        temDeal = dealY()
        removes = temDeal.removeOutliers(date2Company2Profit)#等待手工剔除数据
        for onComOd  in removes:
            if onComOd[0] in list(date2Company2Profit.keys()):
                # date2Company2Profit[onComOd[0]][onComOd[1]] = 0
                if onComOd[1] in date2Company2Profit[onComOd[0]]:
                    del date2Company2Profit[onComOd[0]][onComOd[1]] 
            else:
                continue
        # for oneDate in date2Company2Profit:
        #     if "江西正邦科技股份有限公司" in date2Company2Profit[oneDate]:
        #         print("===================")
        #         date2Company2Profit[oneDate]["江西正邦科技股份有限公司"] = 0
        
        print("after Remove==============")
        temDate,pf2 = temDeal.getProFitSelf(date2Company2Profit)
        # plotManyLines(temDate,[pf1,pf2],"日期","净利润",["剔除异常前","剔除异常后"])
        quaters,valueAfterRemoves = temDeal.quarterFix(date2Company2Profit,nextStep=1,dealK=addN)
        # plotManyLines(quaters,[valueRemovePre,valueAfterRemoves],"日期","净利润环比增速",["剔除异常前","剔除异常后"])

        # print(list(date2Company2Profit.keys()))
        # 计算增长率
        # addN=0
        quaters ,values = temDeal.quarterFix(date2Company2Profit,nextStep=1,dealK=addN)
        # quaters ,values = temDeal.quarterFix(date2Company2Profit,nextStep=4,dealK=addN)
        monthes,mValues = temDeal.quarter2Month(quaters,values)
        quaters = [f"{oneQuarter[:4]}-{oneQuarter[4:6]}" for oneQuarter in quaters]
        # plotInsert(monthes,quaters,mValues,values)
        # 进行ttm修正
        mValuesFixed = mValues
        # monthes,mValuesFixed = temDealX.do_TTM(monthes,mValues)
        # plotManyLines(monthes,[mValues,mValuesFixed],"日期","净利润环比增速",["修正前","修正后"])
        # quaters,values = temDeal.quarterFix(date2Company2Profit,nextStep=4)
        # quaters2,values2 = temDeal.quarterFix(date2Company2Profit,nextStep=1)

        # for (index,oneQ) in enumerate(quaters):
        #     if str(oneQ).startswith('202206'):
        #         values[index] = (values[index-1]+values[index+1])/2
        #     print("============")
        # plotManyLines(quaters,[valuePre,values],"日期","净利润环比增速",["剔除异常前","剔除异常前后"])
        # plotManyLines(quaters,[values2,values],"日期","净利润环比增速",["修正前","修正后"])
        # print("to Month=================")
        
        
        # print("dealValue===============")
        # quaters = [f"{oneQuarter[:4]}-{oneQuarter[4:6]}" for oneQuarter in quaters]
        # plotInsert(monthes,quaters,mValues,values)
        # print(monthes)
        # print("return ================")
        return monthes,mValuesFixed


    def getfoodCPITTM(self):
        # monthCpi = pd.read_excel("中国_CPI_食品_环比+月份.xlsx")
        # monthCpi = pd.read_excel("dataSource\中国_CPI_食品_环比+研报部分.xlsx")
        monthCpi = pd.read_excel("dataSource\中国_CPI_食_环比.xlsx")
        monthCpi.columns = ["date","cpi"]
        monthes ,values = [],[]
        for row in monthCpi.itertuples():
            date = str(row.date)
            monthes.append(f"{date[:4]}-{str(date[5:7])}")
            values.append(row.cpi*0.1)
        temDeal = dealX()
        monthes,values = fixFactorContent(monthes,values)
        # print(values)
        # values = [i+100 for i in values]
        # monthes,values = temDeal.do_value2Rate(monthes,values)
        monthes,values = temDeal.do_TTM(monthes,values) 
        # middle = monthCpi
        # middle = middle[3:]
        # chapterRes = []
        # for row in middle.itertuples():
        #     if str(row.date)[5:7] in ["03","06","09","12"]:
        #         chapterRes.append([str(row.date)[:10].replace("-",""),row.cpi])
        # chapterCpi = pd.DataFrame(chapterRes,columns = ["date","cpi"])
        # print(chapterCpi)
        # return monthCpi,chapterCpi
        return monthes,values
    
    def getmonthlydatas(self,dataPos):
        monthes,values = [],[]
        monthData = pd.read_excel(dataPos)
        colums = monthData.columns
        values = [[] for _ in range(len(colums)-1)]
        for _,row in monthData.iterrows():
            monthes.append(str(row[colums[0]])[:7])
            for (index,oneCol) in enumerate(colums[1:]):
                values[index].append(row[oneCol])
        return colums,monthes,values

        # for row in monthData.itertuples():

    def getGrossProfit(self,bound=True):
        df= pd.read_csv("dataSource\饲料毛利润+季度.csv")
        # print(df)
        date2Company2Profit = defaultdict(dict)
        date2Comapny2revenue = defaultdict(dict)
        for row in df.itertuples():
            # print(row)
            if bound == True:
                if row.REPORT_PERIOD >= 20090630 and row.REPORT_PERIOD<20161231:
                    date2Company2Profit[row.REPORT_PERIOD]\
                        [row.S_INFO_COMPNAME] = abs(row.S_FA_GROSSMARGIN_TTM)
                    date2Comapny2revenue[row.REPORT_PERIOD]\
                        [row.S_INFO_COMPNAME] = abs(row.S_FA_GR_TTM)
            else:
                date2Company2Profit[row.REPORT_PERIOD]\
                        [row.S_INFO_COMPNAME] = abs(row.S_FA_GROSSMARGIN_TTM)
                date2Comapny2revenue[row.REPORT_PERIOD]\
                    [row.S_INFO_COMPNAME] = abs(row.S_FA_GR_TTM)
        values = []
        quarters = sorted(list(date2Company2Profit.keys()))
        for oneQ in quarters:
            temGross = sum(
                [ date2Company2Profit[oneQ][i] for i in date2Company2Profit[oneQ]]
            )
            temAll = sum(
                [ date2Comapny2revenue[oneQ][i] for i in date2Comapny2revenue[oneQ]]
            )
            values.append(temGross/temAll)
        temDeal = dealY()
        # print(quarters,values)
        monthes,values = temDeal.quarter2Month(quarters,values)
        # plotManyLines(monthes,[values],"日期","净利润",["当月"])
        return monthes,values

        #返回 monthes,values
            
        
        
#==========================测试函数====================================
def testgetData():
    getMs = getData()
    getMs.getProfit()
    # getMs.getCPI()
    # monthCpi,chapterCpi = getMs.getCPI()
    # print(chapterAP,chapterCpi)
    # x = [str(i)  for i  in chapterAP["date"].to_list()]
    # plotTWodiffer(x,chapterAP["upRate"].to_list(),
    #             [i*0.01 for i in chapterCpi["cpi"].to_list()],"日期","净利润增长","食品cpi")
if __name__ == "__main__":
    print("sad")
    testgetData()