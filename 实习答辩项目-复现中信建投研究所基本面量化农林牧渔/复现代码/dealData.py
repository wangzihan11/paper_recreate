'''
    获取数据之后处理数据
'''
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import time
from collections import defaultdict,Counter,namedtuple
from untils import plotManyLines,fomartMonth,plotNowDiffer

'''处理因变量的方法集合'''
class dealY:
    def __init__(self):
        pass
    def removeOutliers(self,date2Company2Profit):#去掉异常值
        showComs = []
        # 计算不同季度的 总值
        date2Sum = {}
        for oneDate in date2Company2Profit:
            profits = 0
            for oneCom in date2Company2Profit[oneDate]:
                profits+= abs(date2Company2Profit[oneDate][oneCom])
            date2Sum[oneDate] = profits
        # print(date2Sum)
       
        dates = sorted(list(date2Sum.keys()))
        # plotManyLines(dates,[[date2Sum[i] for i in dates]],"季度","利润","板块获利")
        # 获得需要展示的公司
        x,ys1,com1 = self.showImportantC(date2Company2Profit,date2Sum,1)
        x,ys2 ,com2= self.showImportantC(date2Company2Profit,date2Sum,10)
        # plotNowDiffer(x,ys1,ys2,com1,[])#=================================
        # dates  =list( date2Company2Profit.keys())
        # dates.sort()
        # for oneDate in dates:
        #     comPro = []#（公司名，获利）
            
        #     for oneCompany in date2Company2Profit[oneDate]:
        #         comPro.append((oneCompany,date2Company2Profit[oneDate][oneCompany]))
        #     comPro.sort(key=lambda x:x[1],reverse=True)
        #     # print(len(comPro))
        #     #获利max
        #     for index in range(min(1,len(comPro))):
        #         showComs.append(comPro[index][0])
        #         # dateCom.append((oneDate,comPro[index][0]))
        #     # print(len(comPro))
        #     #损失max
        #     comPro.sort(key=lambda x:x[1])
        #     for index in range(min(1,len(comPro))):
        #         showComs.append(comPro[index][0])
        #         # dateCom.append((oneDate,comPro[index][0]))
        #     # print(comPro[:10])
        #     # break
        # #研究一下所有的公司
        # showComs = list(set(showComs))
        # # 获取这些公司的数据
        # x = dates
        # ys = []
        # for oneCompanyName in showComs:
        #     temYs = []
        #     for onex in x:
        #         try:
        #             temYs.append(
        #                 date2Company2Profit[onex][oneCompanyName]/date2Sum[onex]
        #             )
        #         except:
        #             # print(onex,oneCompanyName)#大部分是退市
        #             temYs.append(0)
        #     ys.append(temYs)
        #画图看看】
        # print(showComs)
        # plotManyLines(x,ys,"时间","盈利/亏损市场占比",showComs)
        #手工剔除 (dates,names)
        # return []
        # needR = [[20140331,'温氏食品集团股份有限公司'],[20140930,'獐子岛集团股份有限公司'],
                #   [20141231,'獐子岛集团股份有限公司'],[20150331,'獐子岛集团股份有限公司'],[20220331,'江西正邦科技股份有限公司'],]
        needR = [[20140331,'温氏食品集团股份有限公司'],[20140930,'獐子岛集团股份有限公司'],
                  [20141231,'獐子岛集团股份有限公司'],[20220630,'江西正邦科技股份有限公司'],[20220331,'江西正邦科技股份有限公司'],
                  [20211231,'温氏食品集团股份有限公司'],[20211231,'江西正邦科技股份有限公司'],]
                #   [20211231,'新希望六和股份有限公司'],
                #   [20211231,'天邦食品股份有限公司']]
        # companys,dates = [],[]
        # return companys,dates
        return needR
    
    def quarterFix(self,date2Company2Profit,nextStep=4,dealK=0):#修正季度利润率增长，得到增长
        quaters,values = [],[]
        self.date2Company2Profit = date2Company2Profit
        date_pairs = []
        dates = sorted(list(self.date2Company2Profit.keys()))
        # print(dates)
        '''获取每一期的对应的now date 和 pre date'''
        for index in range(len(dates)):
            if index ==0:
                continue
            preStep = min(index,nextStep)
            before,after = [],[]
            for i in range(preStep):
                before.append(dates[index-i-1])
                after.append(dates[index-i])
            date_pairs.append([dates[index],before,after])
        # if nextStep ==4:
        #     for i in date_pairs:
        #         print(i)
        #         print(len(self.dates2CompanySame(i[1],i[2])))
        # print("=======================")
        '''计算每一个data_pair的绝对值'''
        for oneQuater in date_pairs:
            # print(oneQuater)
            companys = self.dates2CompanySame(oneQuater[1],oneQuater[2])
            quaters.append(str(oneQuater[0]))
            # print(oneQuater[2],oneQuater[1])
            # print(oneQuater[0],oneQuater[1],oneQuater[2])
            after = self.sumprofits(oneQuater[2],companys)
            before = self.sumprofits(oneQuater[1],companys)
            before += dealK
            after += dealK
            # print(oneQuater[0],round((after-before)/abs(before),2),oneQuater[2],after,oneQuater[1],before)
            # print((self.sumprofits(oneQuater[2],companys),self.sumprofits(oneQuater[1],companys)))
            values.append(
                        (after-before)/abs(before)
                # (self.sumprofits(oneQuater[2],companys)/self.sumprofits(oneQuater[1],companys))-1
            )
        # plotOne(quaters[37:-30],values[37:-30],"日期","利润增长率")
        return quaters,values

    def quarter2Month(self,quarters,values):#将利润率增长进行插值 季度转为月度
        oneInfo = namedtuple('oneInfo','year,month,value,monthStr')
        print(quarters)
        quarterRate = []
        monthes,newValues = [],[]
        # 转化成month 数据格式
        for (index,oneQuarter) in enumerate(quarters):
            oneQuarter = str(oneQuarter)
            year = int(oneQuarter[:4])
            month = int(oneQuarter[4:6])
            quarterRate.append(oneInfo(year,month,values[index],oneQuarter[4:6]))
        #进行插值
        monthes.append(f"{quarterRate[0].year}-{fomartMonth(quarterRate[0].month)}")
        newValues.append(quarterRate[0].value)
        for (index,oneQuarter) in enumerate(quarterRate[1:]):
            beforeQuarter,nowQaurter = quarterRate[index],oneQuarter
            differ = (nowQaurter.value-beforeQuarter.value)/3#固定值
            for i in range(1,3):
                monthes.append(f"{oneQuarter.year}-{fomartMonth((beforeQuarter.month+i)%12)}")
                newValues.append(
                    beforeQuarter.value+differ*i
                )
            monthes.append(f"{nowQaurter.year}-{fomartMonth(nowQaurter.month)}")
            newValues.append(nowQaurter.value)
        # plotOne(monthes[111:-90],newValues[111:-90],"日期","净利润")
        return monthes,newValues
    
    # def getQuater2Monteh(date2Company2Profit):
    #     quaters,values = [],[]
    #     self.date2Company2Profit = date2Company2Profit
    #     date_pairs = []
    #     dates = sorted(list(self.date2Company2Profit.keys()))
    def getProFitSelf(self,date2Company2Profit:dict):
        monthes,values = [],[]
        dates = list(date2Company2Profit.keys())
        dates.sort()
        for oneDate in dates:
            values.append(sum(
                [ date2Company2Profit[oneDate][i] for\
                  i in date2Company2Profit[oneDate]]
            ))
            monthes.append(oneDate)
        return monthes,values


        

    ''' removeOutliers()->获取要展示的公司'''
    def showImportantC(self,date2Company2Profit,date2Sum,K):
        showComs = []
        dates  =list( date2Company2Profit.keys())
        dates.sort()
        for oneDate in dates:
            comPro = []#（公司名，获利）
            showProf = []
            for oneCompany in date2Company2Profit[oneDate]:
                comPro.append((oneCompany,date2Company2Profit[oneDate][oneCompany]))
            comPro.sort(key=lambda x:x[1],reverse=True)
            #获利max
            for index in range(min(K,len(comPro))):
                showComs.append(comPro[index][0])
                showProf.append(comPro[index][0])
            # if oneDate == 20211231:
                # print(showProf)
            #损失max
            comPro.sort(key=lambda x:x[1])
            for index in range(min(K,len(comPro))):
                showComs.append(comPro[index][0])
                showProf.append(comPro[index][0])
            # if oneDate == 20211231:
                # print(showProf)
        #研究一下所有的公司
        showComs = list(set(showComs))
        # 获取这些公司的数据
        x = dates
        ys = []
        for oneCompanyName in showComs:
            temYs = []
            for onex in x:
                try:
                    temYs.append(
                        date2Company2Profit[onex][oneCompanyName]/date2Sum[onex]
                    )
                except:
                    # print(onex,oneCompanyName)#大部分是退市
                    temYs.append(0)
            ys.append(temYs)
        # showComs.sort()
        return x,ys,showComs
    '''quaterFix()->获取共同大的公司'''
    def dates2CompanySame(self,before,after):
        dates = list(set(before)|set(after))
        companys = []
        for oneDate in dates:
            companys.extend(list(
                self.date2Company2Profit[oneDate].keys()
            ))
        sameCompanys = []
        com2Num = Counter(companys)
        for oneCompany in com2Num:
            if com2Num[oneCompany] == len(dates):
                sameCompanys.append(oneCompany)
        return sameCompanys
    '''quaterFix()->计算利润总额'''
    def sumprofits(self,dates,companyNames):
        # print(dates)
        temProfits = 0
        for oneDate in dates:
            for oneCom in companyNames:
                if not np.isnan(self.date2Company2Profit[oneDate][oneCom]):
                    temProfits += self.date2Company2Profit\
                        [oneDate][oneCom]
        return temProfits

    '''暂时不使用'''
    def monthFix(self,monthes,values):#修正月度利润率-目前不使用
        resMonth,upRates = [],[]
        month2Value = {i:j for (i,j) in zip(monthes,values)}
        for (index,oneMonth) in enumerate(monthes):
            if index < 15:
                continue
            beforeMonth = [ monthes[index-i-3] for i in range(12)]
            afterMonth = [monthes[index-i] for i in range(15)]
            resMonth.append(oneMonth)
            sum12 = sum([float(month2Value[i]) for i in beforeMonth])
            sum15 = sum([float(month2Value[i]) for i in afterMonth])
            absSum12 = sum([abs(float(month2Value[i])) for i in beforeMonth])
            upRates.append(
               (sum15-sum12)/absSum12
            )
            # print(oneMonth,beforeMonth,afterMonth)
        # plotOne(resMonth,upRates,"日期","净利润增长")
        return resMonth,upRates
    def quarter2MonthProfit(self,quarters,values):#将利润率从季度转为月度 暂时不用
        oneInfo = namedtuple('oneInfo','year,month,value')
        quaterRate,monthProfit = [],[]
        #提取月份信息
        for (index,oneQuater) in enumerate(quarters):
            oneQuater = str(oneQuater)
            year = int(oneQuater[:4])
            month = int(oneQuater[4:6])
            quaterRate.append(oneInfo(year,month,values[index]))
        monthProfit.append(quaterRate[0])
        #进行插值操作
        for (index,oneState) in enumerate(quaterRate[1:]):
            beforeQuater,nowQauter = quaterRate[index],oneState
            differ = (nowQauter.value-beforeQuater.value)/3#固定值
            for i in range(1,3):
                monthProfit.append(
                    oneInfo(nowQauter.year,(beforeQuater.month+i)%12,beforeQuater.value+differ*i)
                )
            monthProfit.append(nowQauter)
        monthes,values = [],[]
        # for oneRate in monthProfit[162:-90]:
        for oneRate in monthProfit[162:-90]:
            monthes.append(f"{oneRate.year}-{oneRate.month}")
            values.append(oneRate.value)
        # plotOne(monthes,values,"日期","净利润")
        return monthes,values

class dealX:
    def __init__(self):
        pass
    def do_TTM(self,monthes,values):#月度x的
        '''按照目前的理解简单的做平均？'''
        month2V = {i:j for (i,j) in zip(monthes,values)}
        newValues ,newMonthes= [],[]
        for i in range(len(monthes)):
            # if i<12:
            #     continue
            up = min(i,12)
            # print(monthes[i])
            newMonth = monthes[i-up:i+1]
            newValues.append(
                # sum([month2V[i] for i in newMonth])/len(newMonth)
                sum([month2V[i] for i in newMonth])/len(newMonth)
            )
            newMonthes.append(monthes[i])
        # print(values)
        # print(newValues)

        return newMonthes,newValues
    def do_value2Rate(self,monthes,values):
        newMonthes,newVal = [],[]
        # print(values)
        for (index,oneMonth) in enumerate(monthes[1:]):
            newRate = (values[index+1]-values[index])/values[index]
            newVal.append(newRate)
            newMonthes.append(oneMonth)
        return newMonthes,newVal