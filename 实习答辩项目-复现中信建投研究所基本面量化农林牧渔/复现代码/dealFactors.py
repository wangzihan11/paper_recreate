'''
    用于处理数据
'''
import sys
import numpy as np
import pandas as pd
sys.path.append("C:/Users/fksx2/reportResearch/")
from untils import plotTWodiffer,plotRegressionAnalysis,plotManyLines
import statsmodels.api as sm
from collections import namedtuple
from GetData import getData


class Factor:
    # 存储一个因子
    def __init__(self,name,monthes,values):
        # '2010-06'
        self.name= name
        self.monthes,self.values = monthes,values
        self.month2Value = { i:j for (i,j) in zip(monthes,values)}
    # 计算两个因子的相关系数
    def calCorrelationCoefficient(self,otherFactor,K=1,plot=False):
        commonMonthes = sorted(
            list(set(self.monthes)&set(otherFactor.monthes))
        )
        # print(commonMonthes)
        y1 = [self.month2Value[i] for i in commonMonthes]
        y2= [otherFactor.month2Value[i] for i in commonMonthes]
        pccs = np.corrcoef(y1,y2)[0][1]
        if plot == True:
            plotTWodiffer(commonMonthes,y1,y2,"月份",self.name,otherFactor.name,pccs,K)
        return pccs
    #进行线性回归
    def doRegression(self,otherFactor,reverse=False,plot=False):
        commonMonthes = sorted(
            list(set(self.monthes)&set(otherFactor.monthes))
        )
        # print(len(commonMonthes))
        # print(commonMonthes)
        if reverse == False:
            y = [self.month2Value[i] for i in commonMonthes]
            x = [otherFactor.month2Value[i] for i in commonMonthes]
            xN,yN = otherFactor.name,self.name
        else:
            x = [self.month2Value[i] for i in commonMonthes]
            y = [otherFactor.month2Value[i] for i in commonMonthes]
            xN,yN = self.name,otherFactor.name
        regx = sm.add_constant(x)
        model = sm.OLS(y,regx)
        results = model.fit()
        a,b = results.params[0],results.params[1]
        rsquared = results.rsquared
        p = results.pvalues
        trustB = results.conf_int(0.05)[1]
        title = f" 截距:{a} 回归系数:{b} R_square:{rsquared} P值:{p[1]}\n \
            下限 95.0%:{trustB[0]} 上限 95.0%:{trustB[1]} "
        # print(results.summary())
        if plot== True:
            plotRegressionAnalysis(x,y,b,a,xN,yN,title)
        return results
    # 进行多因子回归
    def doMutiRgression(self,otherFactors,K=1):
        commonMonthes = self.getCommentMonthes(otherFactors)
        print(commonMonthes)
        xs,y = [],[]
        temNames = []
        for oneFactor in otherFactors:
            xs.append([oneFactor.month2Value[i] for i in commonMonthes])
            temNames.append(oneFactor.name)
        xs = np.array(xs).T
        
        df = pd.DataFrame(xs, columns=temNames)
        df['monthes'] = commonMonthes
        # print(commonMonthes)
        # df.to_csv("temVs.csv",encoding='utf_8_sig')
        # print(xs)
        
        xs = sm.add_constant(xs)
        y = np.array([self.month2Value[i] for i in commonMonthes])
        model = sm.OLS(y,xs)
        results = model.fit()
        a,params = results.params[0],results.params[1:]
        for (index,content) in enumerate(params):
            print(otherFactors[index].name,content)
        print(sum(params))
        print(results.summary())
        # title = "~~".join([i.name for i in otherFactors])
        title = ""
        title = f"{title}\n{self.summarizeRgressionResult(results)}"
        # self.showFitResultPre(otherFactors,params,a,K=1,title=title)
        self.showFitResult(otherFactors,params,a,K=K,title=title)
        print(results.summary())
        # print(results.params)
        return results.params

    #进行权重合成
    def dealMultiRegreWeight(self,Factors,plot=False):
        commonMonthes = set(self.monthes)
        for oneFactor in Factors:
            commonMonthes = commonMonthes& set(oneFactor.monthes)
        commonMonthes = sorted(list(commonMonthes))
        xs = []
        for oneFactor in Factors:
            xs.append([oneFactor.month2Value[i] for i in commonMonthes])
        y = np.array([self.month2Value[i] for i in commonMonthes])
        xs = np.array(xs)
        xs = xs.T
        model = sm.OLS(y,xs)
        results = model.fit()

        for (index,onFactor) in enumerate(Factors):
            print(onFactor.name,results.params[index])
        print(sum(results.params))
        #做一个拟合
        xs = xs.tolist()
        y_near = []
        for onex in xs:
            y_near.append(
                sum([i*j for (i,j) in zip(onex,results.params)])
            )
        # commonMonthes,y,y_near = commonMonthes[30:-90],y[30:-90],y_near[30:-90]
        if plot == True:
            plotManyLines(commonMonthes,[y,y_near],"月份","cpi%",legend=
                ["原本","拟合"],title="拟合结果",K=5)
        print(results.params,results.pvalues,results.rsquared)
        return results.params,results.pvalues,results.rsquared
        # print(results.summary())
    #做一个错位,将本月的值后移几个月
    def geneFactorValueRight(self,K):
        if K==0:
            return self
        newMonthes,newValues = [],[]
        for (index,oneMonth) in enumerate(self.monthes[K:]):
            newMonthes.append(oneMonth)
            newValues.append(self.values[index])
        newFactor = Factor(f"{self.name}_vRight_{K}",
            newMonthes,newValues)
        return newFactor
    #成批量的后一定，同时和某个固定的要素匹配,同时收集信息
    def doBunchValueRight(self,K,aimFactor,plot=False):
        regressionResult = []
        Regression = namedtuple("Regression",'name,rightN,corr,b,p,rsquare')
        for i in range(K):
            temFactor = self.geneFactorValueRight(K-i-1)
            corr = temFactor.calCorrelationCoefficient(aimFactor,plot=plot)#相关系数
            res = temFactor.doRegression(aimFactor,plot=plot)
            b,p,rsquare = res.params[1],res.pvalues[1],res.rsquared
            regressionResult.append(Regression(
                temFactor.name,K-i-1,corr,b,p,rsquare
            ))
        # for i in range(K):
        #     temFactor = self.geneFactorValueLeft(i)
        #     corr = temFactor.calCorrelationCoefficient(aimFactor,plot=plot)#相关系数
        #     res = temFactor.doRegression(aimFactor,plot=plot)
        #     b,p,rsquare = res.params[1],res.pvalues[1],res.rsquared
        #     regressionResult.append(Regression(
        #         temFactor.name,-1*i,corr,b,p,rsquare
        #     ))
        # for i in regressionResult:
        #     print(i)
        return regressionResult
    # 两个因子组合成一个新因子,模拟拟合结果
    def geneNewFactorWeight(self,fators:list,params,a=0):
        commenMonthes = self.getCommentMonthes(fators)#获取共同的月份
        values = []
        fators.insert(0,self)   
        for oneMonth in commenMonthes:
            values.append(sum(
                [oneF.month2Value[oneMonth]*j for (oneF,j) in zip(fators,params)]
            ))
        names = "~".join([i.name for i in fators])
        return Factor(names,commenMonthes,values)
    # 工具函数-> 获取共同月份    
    def getCommentMonthes(self,factors):
        commenMonth = set(self.monthes)
        for oneFactor in factors:
            commenMonth = commenMonth&set(oneFactor.monthes)
        commenMonth = list(commenMonth)
        commenMonth.sort()
        return commenMonth
    
    def geneFactorValueLeft(self,K):
        if K==0:
            return self
        newMonthes,newValues = [],[]
        # newMonthes = self.monthes[:-1*K]
        # newValues = self.values[K:]
        # print("==============left")
        # print(len(newMonthes),len(newValues))
        for (index,oneMonth) in enumerate(self.monthes[:-1*K]):
            newMonthes.append(oneMonth)
            newValues.append(self.values[index+K])
        # print("==============left")
        # print(self.values)
        # print(newValues)
        newFactor = Factor(f"{self.name}_vLight_{K}",newMonthes,newValues)
        return newFactor
    
    def doBunchValueLight(self,K,aimFactor,plot=False):
        regressionResult = []
        Regression = namedtuple("Regression",'name,rightN,corr,b,p,rsquare')
        for i in range(K):
            temFactor = self.geneFactorValueLeft(i)
            corr = temFactor.calCorrelationCoefficient(aimFactor,plot=plot)#相关系数
            res = temFactor.doRegression(aimFactor,plot=plot)
            b,p,rsquare = res.params[1],res.pvalues[1],res.rsquared
            regressionResult.append(Regression(
                temFactor.name,-1*i,corr,b,p,rsquare
            ))
        # for i in regressionResult:
        #     print(i)
        return regressionResult
    
    def genePartFactor(self,start,end):
        newM,newV = [],[]
        for oneMonth in self.monthes:
            if oneMonth >=start and oneMonth <=end:
                newM.append(oneMonth)
                newV.append(self.month2Value[oneMonth])
        return Factor(self.name,newM,newV)

    
    #  工具函数 回归之后做预测展示
    def showFitResultPre(self,otherFactors,params,a,K=1,title=""):
        monthesHave = self.getCommentMonthes(otherFactors)
        monthesPre = otherFactors[0].getCommentMonthes(otherFactors)
        beforeY,afterY = [],[]
        for oneM in monthesPre:
            if oneM in self.month2Value:
                beforeY.append(self.month2Value[oneM])
            else:
                beforeY.append(0)
        for oneMonth in monthesPre:
            afterY.append(sum(
                [otherFactors[i].month2Value[oneMonth]*params[i] for i in range(len(params))]
            )+a)
            
        reaY = []    
        temLoader = getData()
        monthes,values = temLoader.getProfit(bound=False)
        name2V = {i:j for (i,j) in zip(monthes,values)}
        for oneMonth in monthesPre:
            try:
                reaY.append(name2V[oneMonth])
            except:
                reaY.append(0)

        plotManyLines(monthesPre,[beforeY,afterY,reaY],"月份",self.name,legend=
                ["原本","拟合","真实"],title="拟合结果",K=K)
        
        print(monthesHave,monthesPre)
        print("+++++++++++++++++")
    # 工具函数，回归之后做拟合的展示
    def showFitResult(self,otherFactors,params,a,K=1,title=""):
        print(title)
        monthes = self.getCommentMonthes(otherFactors)
        beoforY = [ self.month2Value[i] for i in monthes]
        afterY = []
        for oneMonth in monthes:
            afterY.append(sum(
                [otherFactors[i].month2Value[oneMonth]*params[i] for i in range(len(params))]
            )+a)
        # plotManyLines(monthes,[afterY],"月份",self.name,legend=
        #         ["拟合"],title="拟合结果"+title,K=K)
        plotManyLines(monthes,[beoforY,afterY],"月份",self.name,legend=
                ["原本","拟合"],title="拟合结果"+title,K=K)
        return
    # 工具函数 整合回归的信息
    def summarizeRgressionResult(self,results):
        a,b = results.params[0],results.params[1:]
        rsquared = results.rsquared
        p = results.pvalues
        trustB = results.conf_int(0.05)[1]
        title = f" 截距:{a} 回归系数:{b} R_square:{rsquared} P值:{p[1]}\n \
            下限 95.0%:{trustB[0]} 上限 95.0%:{trustB[1]} "
        return title

    def predictRightMonthes(self,K=6):
        monthes = ['2023-01','2023-02','2023-03','2023-04','2023-05',
                   '2023-06','2023-07','2023-08','2023-09','2023-10',
                   '2023-11','2023-12']
        temMonthes = self.monthes
        index = 0
        for oneM in monthes:
            if index >=K:
                break
            if oneM not in temMonthes:
                index +=1
                temMonthes.append(oneM)
            else:
                continue
        newMonthe = temMonthes[K:]
        self.monthes = newMonthe
        if len(newMonthe)!= len(self.values):
            raise Exception("长度不一致")
        self.month2Value = {}
        for (m,v) in zip(self.monthes,self.values):
            self.month2Value[m] = v

    




