# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 15:08:22 2023

@author: fksx2

# 一些工具函数
"""
import cx_Oracle
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import time
from collections import defaultdict,Counter,namedtuple
from prettytable import PrettyTable

plt.rcParams['font.sans-serif'] = ['simhei']###解决中文乱码
plt.rcParams['axes.unicode_minus']=False

'''解决x轴过密问题'''
def lessXticks(x,K=3):
    newX = []
    for (index,content) in enumerate(x):
        if index %K!=0:
            newX.append("")
        else:
            newX.append(content)
    return newX
'''连接数据库'''
def connect_database(db='wind'):
    if db == 'wind':
#         conn = cx_Oracle.connect('jcquery','83936666','10.88.102.160:1521/gfdwdb1')
        conn = cx_Oracle.connect('gffeintern','gffeintern123','10.88.102.82:1521/FINCHINA')
    elif db == 'ferp':
        conn = cx_Oracle.connect('ferp','ferp1234','10.88.101.121:1521/fedb')
    return conn
'''画出一个因子示意'''
def plotOne(x,y,xlabel,yName):
    plt.rcParams['font.sans-serif'] = ['simhei']###解决中文乱码
    plt.rcParams['axes.unicode_minus']=False

    fig = plt.figure()
    ax1 = fig.add_subplot()
    print(len(x),len(y))
    p1, = ax1.plot(x, y,color='red',marker='o') 
    ax1.set_ylabel(yName)
    # ax1.set_ylim(0, 25)
    ax1.legend([yName], loc="upper left")
    ax1.yaxis.label.set_color(p1.get_color())
    ax1.yaxis.label.set_fontsize(14)
    ax1.tick_params(axis='y', colors=p1.get_color(), labelsize=14)
    ax1.set_xticklabels(x,rotation=90)
    ax1.set_xlabel(xlabel)
    plt.show()

'''画出两个因子的y轴'''
def plotTWodiffer(x,y1,y2,xlabel,y1Name,y2Name,title="",K=1):
    plt.rcParams['font.sans-serif'] = ['simhei']###解决中文乱码
    plt.rcParams['axes.unicode_minus']=False

    fig = plt.figure()
    ax1 = fig.add_subplot()

    p1, = ax1.plot(x, y1,color='red',marker='o') 
    ax1.set_ylabel(y1Name)
    # ax1.set_ylim(0, 25)
    ax1.legend([y1Name], loc="upper left")
    ax1.yaxis.label.set_color(p1.get_color())
    ax1.yaxis.label.set_fontsize(14)
    ax1.tick_params(axis='y', colors=p1.get_color(), labelsize=8)
    ax1.set_title(f"相关系数{title}")

    ax2 = ax1.twinx() 
    p2, = ax2.plot(x, y2, color='blue',marker='s')
    ax2.grid(False) # turn off grid #2
    ax2.set_ylabel(y2Name)
    ax2.legend([y2Name], loc="upper center",ncol=1)
    ax2.yaxis.label.set_color(p2.get_color())
    ax2.yaxis.label.set_fontsize(14)
    ax2.tick_params(axis='y', colors=p2.get_color(), labelsize=8)
    # fig.add_subplot(ax2)
    x = lessXticks(x,K)
    ax1.set_xticklabels(x,rotation=90,fontsize=8)
    plt.xlabel(xlabel)
    
    plt.show()
    # plt.savefig(f"{y1Name}_{y2Name}.png")

'''画很多的线'''
def plotManyLines(x,ys,xlabel,ylabel,legend,title="",K=1,colors=[]):
    if len(colors)==0 or len(colors)!=len(ys):
        colors = [randomcolor() for i in range(len(ys))]
    plt.rcParams['font.sans-serif'] = ['simhei']###解决中文乱码
    plt.rcParams['axes.unicode_minus']=False
    temx = [i+1 for i in range(len(x)) ]
    for (i,oney) in enumerate(ys):
        plt.plot(temx, oney, marker='o', markersize=3,color=colors[i]) 
        
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend(legend,ncol=3)
    # plt.legend(legend,loc = (1 , 0)) 
    x = lessXticks(x,K)
    plt.xticks(temx,x,rotation=90)
    plt.title(title)
    plt.show()

import random   #定义随机生成颜色函数
def randomcolor():
    colorArr = ['1','2','3','4','5','6','7','8','9','A','B','C','D','E','F']
    color ="#"+''.join([random.choice(colorArr) for i in range(6)])
    return color

'''画两个子图'''
def plotNowDiffer(x1,ys1,ys2,legend1,legend2):
    plt.rcParams['font.sans-serif'] = ['simhei']###解决中文乱码
    plt.rcParams['axes.unicode_minus']=False
    # plt.subplot(3, 1, 1)
    # temx = [i+1 for i in range(len(x1)) ]
    # plt.plot(temx, temx, marker='o', markersize=3) 
    
    colors = [randomcolor() for i in range(max(len(ys1),len(ys2)))]
    temx = [i+1 for i in range(len(x1)) ]
    plt.subplot(3, 1, 1)
    for (index,oney) in enumerate(ys2):
        plt.plot(temx, oney, marker='o', markersize=3,color=colors[index]) 
    plt.legend(legend1,loc='upper left',ncol=3)
    # plt.legend(legend1,bbox_to_anchor=(1.05, 1), loc='upper center', borderaxespad=0)
    plt.subplot(3, 1, 2)
    for (index,oney) in enumerate(ys2):
        plt.plot(temx, oney, marker='o', markersize=3,color=colors[index]) 

    plt.subplot(3, 1, 3)
    
    for (index,oney) in enumerate(ys1):
        plt.plot(temx, oney, marker='o', markersize=3,color=colors[index]) 
    # plt.legend(legend1,ncol=4)
    plt.xticks(temx,x1,rotation=90)
    plt.ylabel("净利润占行业总利润百分比")
   

    # plt.legend(legend2)
    
    
    plt.xticks(temx,x1,rotation=90)
    plt.show()

'''格式化月份'''
def fomartMonth(month):
    month = int(month)
    if month < 10:
        return f"0{month}"
    else:
        return month

'''画回归图'''
def plotRegressionAnalysis(x,y,b,a,xlabel="",ylabel="",title=""):
    x,y = np.array(x),np.array(y)
    fig, ax = plt.subplots(figsize = (12, 6))
    ax.scatter(x, y, color='blue',marker='d')
    # ax.scatter(x, y, s=60, alpha=0.7, edgecolors="k",marker='d')
    xMin,xMax = min(x),max(x)
    xline = np.linspace(xMin, xMax, num=100)
    ax.plot(xline, a + b * xline, color="red", lw=3)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    plt.title(title)
    plt.show()

'''展示回测的结果'''
def showBunchRegressonResult(res):
    x,names = PrettyTable(),["指标名称","领先x期","相关系数","回归系数","p","rsquare"]
    x.field_names = names
    for oneres in res:
        x.add_row([
            oneres.name, oneres.rightN,round(oneres.corr,2),
            round(oneres.b,2),oneres.p,round(oneres.rsquare,2)
        ])
    print(x)
    return

'''处理零开头的变量'''
def fixFactorContent(monthes,values:list):
    for (index,value) in enumerate(values):
        if value != 0:
            break
    monthes = monthes[index:]
    values = values[index:]
    for index in range(1, len(values)):
        if values[-1*index] !=0:
            break
    values = values[:-1*index]
    monthes = monthes[:-1*index]
    return monthes,values
'''平滑一些异常值'''
def handleOutliers(values):
    average = sum( [abs(i) for i in values])/len(values)
    values =[ i+average for i in values]
    # for (index,content) in enumerate(values):
    #     if content == 0 and index!=0 and index!=(len(values)-1):
    #         values[index] = (values[index-1]+values[index+1])/2
    #     else:
    #         continue
    return values

''''''
def plotInsert(x1,x2,y1,y2):
    plt.rcParams['font.sans-serif'] = ['simhei']###解决中文乱码
    plt.rcParams['axes.unicode_minus']=False
    newX1 = [i for i in range(len(x1))]
    newX2 = [x1.index(i) for i in x2]
    plt.plot(newX1, y1, marker='o', markersize=3) 
    plt.scatter(newX2,y2,color="red")
    x1= lessXticks(x1,3)
    plt.xticks(newX1,x1,rotation=90)
    
    plt.ylabel("净利润TMM环比增速")
    plt.legend(["月度","季度"])
    
    plt.show()

'''平滑处理复数'''
def dealNegativeNumber(values):
    addN = max(values)
    minN = min(values)
    if min(values) <0:
        values = [i+addN+minN for i in addN]
    return values
def getDealNegativeNumberK(values):
    if min(values) > 0:
        return 0
    else:
        return max(values)+abs(min(values))

