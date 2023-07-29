import pandas as pd
from dataclasses import dataclass
import cvxpy as cp
import numpy as np
from prettytable import PrettyTable
from scipy import optimize
@dataclass
class OneIndustry:
    name:str
    weight:float
    pe_ttm:float


class AdjustPositionsQuadratic:
    '''如果是线性规划，那么需要确定什么需要卖出'''
    def __init__(self,data:pd.DataFrame,sumWPe=35,peMax=40,weightMax=0.3):
        '''占净值比 行业名称 PE_TTM'''
        self.industrys = []
        for _,row in data.iterrows():
            if row["占净值比"] != 0:
                self.industrys.append(
                    OneIndustry(row["行业名称"],row["占净值比"],row["PE_TTM"])
                )
        self.sumWPe,self.peMax,self.weightMax = sumWPe,peMax,weightMax
    def findControlWeightIndustry(self):
        self.controlIndustry = []
        for oneIndustry in self.industrys:
            # print(oneIndustry.pe_ttm)
            if oneIndustry.pe_ttm > self.peMax:
                self.controlIndustry.append(oneIndustry)
            else:
                continue
        return
    def solveCXV(self):
        self.findControlWeightIndustry()
        n = len(self.industrys)
        c1 = np.array([1 for _ in range(len(self.industrys))])
        c2 = np.array([-2*i.weight for i in self.industrys])
        # 不等式
        Alist,blist = [],[]
        ## 总和约束
        Alist.append([i.pe_ttm for i in self.industrys])
        blist.append(self.sumWPe)
        ## 行业约束
        for oneIndustry in self.controlIndustry:
            temlist = [0 for _ in range(n)]
            temIndex = self.industrys.index(oneIndustry)
            temlist[temIndex] = 1
            Alist.append(temlist)
            blist.append(self.weightMax)
        # 等式
        A = np.array(Alist)
        b= np.array(blist)
        Aeq = np.array([1 for _ in range(n)])
        beq = np.array([1])
        x = cp.Variable(n,integer=False)
        obj=cp.Minimize(c1@(x**2)+c2@x)
        con=[0<=x, x<=1, A@x<=b,Aeq@x==beq]
        prob = cp.Problem(obj, con)
        prob.solve()
        # print("最优值为:",prob.value)
        # print("最优解为:",x.value)
        print("============== 使用 cvxpy ==============" )
        # print("使用 cvxpy" )
        self.showResult(x.value)
    def sloveScipy(self):
        self.findControlWeightIndustry()
        # 生成限制条件
        f = self.geneminAimFunc()
        cons,x,bounds = [],[],[]
        # 生成一般边界
        for OneIndustry in self.industrys:
            # x.append(OneIndustry.weight)
            x.append(0)
            bounds.append([0,1])
        # 生成pe边界
        for oneIndustry in self.controlIndustry:
            temIndex = self.industrys.index(oneIndustry)
            cons.append(
                {"type":'ineq',"fun":lambda x: -1*x[temIndex]+self.weightMax}
            )
        # 生成 addSum边界
        cons.append({"type":'ineq',"fun":self.geneWeightSum()})
        cons.append({"type":"eq","fun":self.geneSumOne()})
        x,cons = tuple(x),tuple(cons)
        res = optimize.minimize(f, x0=x,bounds=bounds, constraints=cons,)
        # print(res.x)
        # print(res.success)
        print("============== 使用 scipy ==============" )
        self.showResult(res.x)
    def geneminAimFunc(self):
        aimFuncStr = ""
        for index,content in enumerate(self.industrys):
            temOneIndex = -2*content.weight
            aimFuncStr += f"x[{index}]**2{temOneIndex}*x[{index}]+"
        aimFuncStr = aimFuncStr[:-1]
        # print(aimFuncStr)
        v = eval(f"lambda x:{aimFuncStr}")
        return v
    def geneSumOne(self):
        aimFuncStr = ""
        for i in range(len(self.industrys)):
            aimFuncStr += f"x[{i}]+"
        aimFuncStr = aimFuncStr[:-1]
        aimFuncStr += "-1"
        # print(aimFuncStr)
        v = eval(f"lambda x:{aimFuncStr}")
        return v
    def geneWeightSum(self):
        aimFuncStr = "-"
        for index,content in enumerate(self.industrys):
            aimFuncStr += f"{content.pe_ttm}*x[{index}]-"
        aimFuncStr = aimFuncStr[:-1]
        aimFuncStr += f"+{self.sumWPe}"
        # print(aimFuncStr)
        v = eval(f"lambda x:{aimFuncStr}")
        return v
    def showResult(self,valueX):
        change = 0
        sumWpe = 0
        table = PrettyTable()
        table.field_names = ["name","beforeW","afterW","pe_TTM"]
        for index,content in enumerate(self.industrys):
            table.add_row([
                content.name,round(content.weight,5),round(valueX[index],5),round(content.pe_ttm,5)
            ])
            sumWpe += valueX[index]*content.pe_ttm
            change += abs(content.weight-valueX[index])
        print(table)
        print("权重综合","加权pe",end="")
        print(sum(valueX),sumWpe)
        print("换手率",end="")
        print(change/2)
        
            


if __name__ == "__main__":
    df = pd.read_excel("副本线性优化demo - 副本.xlsx")
    # print(df)
    temMethods = AdjustPositionsQuadratic(df)
    temMethods.solveCXV()
    temMethods.sloveScipy()


