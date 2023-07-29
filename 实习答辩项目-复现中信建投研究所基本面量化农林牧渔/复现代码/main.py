'''
    主函数，主要展示逻辑过程
    getData-> dealData->dealFactors
'''
from GetData import getData
from dealData import dealX
from dealFactors import Factor
from untils import plotManyLines,showBunchRegressonResult,fixFactorContent,handleOutliers
from prettytable import PrettyTable

def profitTMM_and_cpi_related(start=20101000,end=20231231):
    dataLoader = getData()
    # monthes,values = dataLoader.getProfit(bound=bound)
    monthes,values = dataLoader.getBoundProfit(start,end)
    
    profitTMM = Factor("netprofit_TTM",monthes,values)
    monthes,values = dataLoader.getfoodCPITTM()
    print(monthes)
    foodCPI = Factor("食品CPI",monthes,values)
    profitTMM.calCorrelationCoefficient(foodCPI,plot=True,K=3)

def profitTMM_and_cpi_regression(start=20101000,end=20231231):
    dataLoader = getData()
    monthes,values = dataLoader.getBoundProfit(start,end)
    profitTMM = Factor("净利润TTM",monthes,values)
    monthes,values = dataLoader.getfoodCPITTM()
    temDeal = dealX()
    # monthes,values = temDeal.do_value2Rate(monthes,values)
    # monthes,values = temDeal.do_TTM(monthes,values)
    foodCPI = Factor("食品CPI",monthes,values)
    profitTMM.calCorrelationCoefficient(foodCPI,plot=True)
    profitTMM.doRegression(foodCPI,reverse=True,plot=True)





def synthesis_food_cpi():
    dataLoader = getData()
    # 组转食品cpi
    # monthes,foodMonthCpi = dataLoader.getfoodCPITTM()
    # FoodCPI = Factor("食品CPI",monthes,foodMonthCpi)
    # 组装其他值
    Factors = []
    colums,monthes,values = dataLoader.getmonthlydatas("dataSource\中国_CPI_食品细分_环比.xlsx")
    monthes = monthes[180:]
    values = [i[180:] for i in values]
    for (index,oneValue) in enumerate(values):
        Factors.append(
            Factor(colums[index+1],monthes,oneValue)
        )
    # plotManyLines(monthes,values,"日期","cpi",colums[1:]) #简单观察
    #进行一个权重回归
    # def (self,factors):
    print(Factors[0].getCommentMonthes(Factors))
    res = Factors[0].dealMultiRegreWeight(Factors[1:],plot=True)
    print(res)


def eatFoodPoints_and_foodCpi_related_regresion():
    files = ["dataSource\食用农产品价格指数_月_平均值.xlsx"]#文件对应cpi中的一列
    dataLoader,CpiFactors = getData(),[]
    # 组装 foodCpi 细分
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

    # 组装 eatPoint 部分
    EatfoodFactors = []
    colums,monthes,values = dataLoader.\
        getmonthlydatas("dataSource\食用农产品价格指数_月_平均值.xlsx")
    for (index,oneValue) in enumerate(values):
        temM,temV = temDealX.do_TTM(monthes,oneValue)
        EatfoodFactors.append(
            Factor(f"{colums[index+1]}_TTM",temM,temV)
            # Factor(colums[index+1],monthes,oneValue)
        )
    
    print(len(CpiFactors),len(EatfoodFactors))
    for index in range(len(CpiFactors)):
        #依次进行组合
        EatfoodFactors[index].calCorrelationCoefficient(CpiFactors[index],3,plot=True)
        EatfoodFactors[index].doRegression(CpiFactors[index],plot=True)

    # 对于每一个细则中的部分进行展示
    # for (index,file) in enumerate(files):
    #     colums,monthes,values = dataLoader.getmonthlydatas(file)
    #     for (colIndex,oneCol) in enumerate(colums[1:]):
    #         #当前这一列命名
    #         temFactor = Factor(oneCol,monthes,values[colIndex])
    #         #计算相关和回归
    #         temFactor.calCorrelationCoefficient(CpiFactors[index],3)
    #         temFactor.doRegression(CpiFactors[index])


def profitTMM_and_realFactors(filePos ="dataSource\猪_自变量.xlsx",start=20101000,end=20231231):
    dataLoader = getData()
    # monthes,values = dataLoader.getProfit(bound=bound)
    monthes,values = dataLoader.getBoundProfit(start,end)
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
    # showPig = [1,0,1,3,1]
    #进行同期和跨期的回2测
    for (index,oneFactor) in enumerate(pigFactors):
       
        # oneFactor.doRegression(profitTMMFactor,plot=True)
        res = oneFactor.doBunchValueRight(18,profitTMMFactor,plot=False)
        showBunchRegressonResult(res)
        profitTMMFactor.calCorrelationCoefficient(oneFactor,plot=True,K=3)
        # showPerfetMonthChange(oneFactor,profitTMMFactor,showPig[index])
        
        
    
'''profitTMM_and_realFactors()->展示跨期表现好的'''
def showPerfetMonthChange(changeF:Factor,oldF,monthV):
    newF = changeF.geneFactorValueRight(monthV)
    oldF.calCorrelationCoefficient(newF,plot=True,K=3)

def feed_and_raw_material(bound=True):
    dataLoader = getData()
    colums,monthes,values = dataLoader.getmonthlydatas("dataSource\饲料_月.xlsx")
    if bound == True:
        monthes = monthes[:95]
        values = [i[:95] for i in values]
    #分解数据
    cornM,cornV = fixFactorContent(monthes,values[3])
    soybeanM,soybeanV = fixFactorContent(monthes,values[2])
    chickenFeedM,chickenFeedV = fixFactorContent(monthes,values[0])
    pigFeedM,pigFeedV = fixFactorContent(monthes,values[1])
    #合成因子
    cornFactor = Factor(colums[4],cornM,cornV)
    soybeanFactor = Factor(colums[3],soybeanM,soybeanV)
    chickenFeedF = Factor(colums[1],chickenFeedM,chickenFeedV)
    pigFeedF = Factor(colums[2],pigFeedM[20:],pigFeedV[20:])
    
    # 因子交互  合成、生成，测试相关性
    ## 鸡饲料
    chickenFeedF.doMutiRgression([cornFactor,soybeanFactor],K=3)
    # params = chickenFeedF.dealMultiRegreWeight([cornFactor,soybeanFactor],plot=True)
    # newgenenM = cornFactor.geneNewFactorWeight([soybeanFactor],params)
    # newgenenM.calCorrelationCoefficient(chickenFeedF,plot=True,K=3)
    ## 猪饲料
    pigFeedF.doMutiRgression([cornFactor,soybeanFactor],K=3)
    # params = pigFeedF.dealMultiRegreWeight([cornFactor,soybeanFactor],plot=True)
    # newgenenM = cornFactor.geneNewFactorWeight([soybeanFactor],params)
    # newgenenM.calCorrelationCoefficient(pigFeedF,plot=True,K=3)

def feed_gross_profit_and_price(bound=True,K=3):
    dataLoader = getData()
    monthes,values = dataLoader.getGrossProfit(bound=bound)
    GorssFactor = Factor("饲料行业毛利率",monthes,values)
    # monthes,values = dataLoader.getBoundProfit()
    # profitTMMFactor = Factor("净利润TTM环比增速",monthes,values)

    colums,monthes,values = dataLoader.getmonthlydatas("dataSource\饲料_月.xlsx")
    chickenFeedM,chickenFeedV = fixFactorContent(monthes,values[0])
    pigFeedM,pigFeedV = fixFactorContent(monthes,values[1])
    chickenFeedF = Factor(colums[1],chickenFeedM,chickenFeedV)
    pigFeedF = Factor(colums[2],pigFeedM[20:],pigFeedV[20:])

    GorssFactor.calCorrelationCoefficient(chickenFeedF,plot=True,K=K)
    # profitTMMFactor.calCorrelationCoefficient(chickenFeedF,plot=True,K=K)
    chickenFeedF.doRegression(GorssFactor,plot=True)

    GorssFactor.calCorrelationCoefficient(pigFeedF,plot=True,K=K)
    pigFeedF.doRegression(GorssFactor,plot=True)

    pass

def checkMacroFactor(start=20101231,end=20231231,filePos="dataSource/中国_宏观变量).xlsx"):
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
        profitTMMFactor.calCorrelationCoefficient(oneFactor,plot=True,K=3)
        res = oneFactor.doBunchValueRight(18,profitTMMFactor,plot=False)
        # if oneFactor.name=="中国:宏观经济景气指数:一致指数":
        #     newF = oneFactor.geneFactorValueLeft(20)
            # profitTMMFactor.calCorrelationCoefficient(newF,plot=True,K=3)
        showBunchRegressonResult(res)

if __name__ == "__main__":
    # data = getData()
    # data.getBoundProfit(20210000,20240000)
    # data.getBoundProfit()
    # profitTMM_and_cpi_related(end=20231231)
    # profitTMM_and_cpi_related()
    
    # profitTMM_and_cpi_regression()
    synthesis_food_cpi()
    # eatFoodPoints_and_foodCpi_related_regresion()
    checkMacroFactor()
    profitTMM_and_realFactors()
    # profitTMM_and_realFactors("dataSource\鸡_自变量.xlsx",start=20161000,end=20231231) 
    # profitTMM_and_realFactors("dataSource\鸡_自变量.xlsx",start=20151231,end=20231231) 
    # profitTMM_and_realFactors("dataSource\鸡_自变量.xlsx",start=20101231,end=20231231)  
   
    # feed_and_raw_material(bound=False)
    # feed_gross_profit_and_price(bound=False)
    # checkMacroFactor(end=20231030)
    
    # checkMacroFactor(end=20231030)
    # checkMacroFactor(end=20231231,filePos="dataSource\进出口.xlsx")
    # checkMacroFactor(end=20231231,filePos="dataSource\产量.xlsx")
    checkMacroFactor(end=20151230)
    checkMacroFactor(start=20151230,end=20231030)
    checkMacroFactor(end=20151231,filePos="dataSource\进出口.xlsx")
    checkMacroFactor(start=20151230,end=20231231,filePos="dataSource\进出口.xlsx")
    checkMacroFactor(end=20151231,filePos="dataSource\产量.xlsx")
    checkMacroFactor(start=20151230,end=20231231,filePos="dataSource\产量.xlsx")
    # checkMacroFactor(end=20231231)