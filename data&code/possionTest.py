#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import dataProcess
import xlrd
import random
import copy
import numpy as np


t = 60 #设置一个服务时间段时长t（分钟）

#对于一组数据，已知总体均值的情况下，可判断其是否符合泊松分布（泊松分布函数均值等于方差，仅有一个参数），通过抽样获得各时段中同时挂号患者人数，
#不同的同时挂号人数的权重（即概率）通过泊松分布函数求得，由概率和人数即可求得期望的同时挂号人数，从而得到期望值和观测值的方差，最后得到置信区间
#在计算观察数据分布时，以1分钟为单位，x为分钟，y值为对应这一分钟内挂号的人数。
def possionTest(data,weight):
    data_weighted = [a*b for a,b in zip(data,weight)]
    #总抽样次数为sum(data)
    mu = sum(data_weighted)/sum(data)
    print("average value：%f" % mu)           
    print("sampling result：%s" % data)
    return mu
    #print(scipy.stats.chisquare(data,data_expected))
    #oddsratio,pvalue = stats.fisher_exact(zipped_data)
    #print("oddsratio：%s,pvalue:%s" % (oddsratio,pvalue))
    
    #return stats.kstest(data,'poisson',(mu,))
    

#input:Int,Int,Int
#output:Bool
def isTimeInRange(start,end,time):
    if time>=start and time < end:
        return True
    else:
        return False
    
#unit_time为采样的单位时间，单位是分钟，chouyangcishu是做多少次抽样
#input:String,Int,Int
def fileProcess(file,unit_time,chouyangcishu):
    data = xlrd.open_workbook(file)
    table = data.sheets()[0]
    nrows = table.nrows  #获取该sheet中的有效行数
    mat = []#把读取excel中内容放入list中
    
    for col in range(1, nrows): #第0行是字段名称，跳过
        #数据表中
        row_values = table.row_values(col)


        #泊松分布只考虑现场患者的到达是否符合
        if(len(row_values[0].strip())==0 or row_values[0].strip()=="appointment"):
            continue
        
        #fuwuqishishijian为1表示服务时段是上午，2表示服务时段是下午
        fuwuqishishijian = 0
        if(len(row_values[6].strip())!=0):
            fuwustart = int(row_values[6].strip().split("-")[0].split(":")[0])
            if(fuwustart<13):
                fuwuqishishijian = 1
            else:
                fuwuqishishijian = 2
        #前面已把接诊时间row_temp[8]为空的给过滤掉，此处均不为空
        elif(len(row_values[8].strip())!=0):
            fuwustart = int(row_values[8].strip().split(" ")[1].split(":")[0])
            if(fuwustart<13):
                fuwuqishishijian = 1
            else:
                fuwuqishishijian = 2
        else:
            continue

        row_values.append(fuwuqishishijian)
        mat.append(row_values)
        if len(mat[-1][2]) != 0:            
            temp = dataProcess.datetime_get(mat[-1][2])
            temp[0] = dataProcess.dateFormat(temp[0])
            mat[-1][2] = temp[0] + " " + temp[1]
        if len(mat[-1][3]) != 0:
            temp = dataProcess.datetime_get(mat[-1][3])
            temp[0] = dataProcess.dateFormat(temp[0])
            mat[-1][3] = temp[0] + " " + temp[1]
        if len(mat[-1][8]) != 0:            
            temp = dataProcess.datetime_get(mat[-1][8])
            temp[0] = dataProcess.dateFormat(temp[0])
            mat[-1][8] = temp[0] + " " + temp[1]
    mat1 = sorted(mat, key=lambda x:(x[4], x[5], x[7], x[9], x[3]))
    guahaoqingkuang_zhuanjia_fenshi = possion_dataProcess(mat1,unit_time,chouyangcishu)
    return guahaoqingkuang_zhuanjia_fenshi

#输入可能是多个日期多个专家的患者情况，对每个专家每个服务周期分别利用泊松方法求均值    
def possion_dataProcess(mat1,unit_time,chouyangcishu):
    guahaoqingkuang_zhuanjia_fenshi = [] #按每个专家每天各时段分组记录挂号患者
    guahaodate = ""
    guahaoshijian = ""
    keshi = ""
    haoyuanming = ""
    zhuanjia = ""
    fuwushijian=0
    guahaoshijian_all = []#定义空的list，用于把guahaoshijian_all_temp初始化为空list
    #把排序后的数据，按照就诊科室、号源、专家、服务时间段、进行分组，每组中统计所有日期患者在各分时时段内的挂号数量
    for col in range(0, len(mat1)): #原excel中第一行是字段名，故list中共有nrows-1行
        vars = copy.deepcopy(mat1[col])
        #若是从guahao_time_sorted-20181119.txt文件中读入的结果记录，而不是从源数据中直接读入的，则需要处理
        if(len(mat1[col])==12):
            vars[0] = mat1[col][7]
            vars[1] = mat1[col][0]
            vars[4] = mat1[col][5]
            vars[5] = mat1[col][11]
            vars[7] = mat1[col][6]
            vars[9] = mat1[col][10]
        
        #无需判断就诊开始时间是否为空，因为现场挂号人来了就可以
        if(vars[0]=="appointment" or len(vars[3])==0 or len(vars[4])==0 or len(vars[5])==0 or len(vars[7])==0):
#        if(vars[0]=="现场" or len(vars[3])==0 or len(vars[4])==0 or len(vars[5])==0 or len(vars[7])==0):
            continue        
        if(len(mat1[col])==10):
            guahao = dataProcess.datetime_get(vars[3])
        elif(len(mat1[col])==12):
            guahao = [mat1[col][1],mat1[col][2]]
        
        if(guahaodate == "" and guahaoshijian == "" and keshi == "" and haoyuanming == "" and zhuanjia == "" and fuwushijian==0):                                    
            guahaodate = guahao[0]
            guahaoshijian = guahao[1]
            keshi = vars[4]
            haoyuanming = vars[5]
            zhuanjia = vars[7]
            fuwushijian = vars[9]
            guahaoshijian_all_temp = copy.deepcopy(guahaoshijian_all) #初始化guahaoshijian_all_temp，赋值空list
        
        elif(guahaodate !=guahao[0] or keshi != vars[4] or haoyuanming != vars[5] or zhuanjia != vars[7] or fuwushijian != vars[9]):          
            guahaoqingkuang_zhuanjia_fenshi.append([guahaodate, keshi, haoyuanming, zhuanjia, guahaoshijian_all_temp, fuwushijian])
            guahaodate = guahao[0] 
            guahaoshijian = guahao[1]
            keshi = vars[4]
            haoyuanming = vars[5]
            zhuanjia = vars[7]
            fuwushijian = vars[9]
            guahaoshijian_all_temp = copy.deepcopy(guahaoshijian_all) #初始化guahaoshijian_all_temp，赋值空list  

        guahaoshijian_all_temp.append(guahao[1])
        if(col==len(mat1)-1):
            guahaoqingkuang_zhuanjia_fenshi.append([guahaodate, keshi, haoyuanming, zhuanjia, guahaoshijian_all_temp, fuwushijian])
    
        
    #t = 60 #设置一个服务时间段时长t（分钟）
    guahao_shijianduan = dataProcess.init_shijianduan(t)  
    renshupinci = [0,0,0,0,0,0]#用于统计抽样的单位时间内，挂号患者数量，前四项统计挂号人数0~4人的情况，最后一项统计挂号人数不少于5人的情况
    caiyang_starts_all = []
    #每个时间段内采样指定次数
    for i in range(0,len(guahao_shijianduan)):
        t_start = dataProcess.time_to_second(guahao_shijianduan[i][0])
        t_end = dataProcess.time_to_second(guahao_shijianduan[i][1]) - unit_time*60
        #计算一个时间段内的所有采样点位置,采样点位置为采样的单位时间段的起始位置
        caiyang_starts = random.sample(range(t_start,t_end),chouyangcishu)
        caiyang_starts_all.append([guahao_shijianduan[i][0],guahao_shijianduan[i][1],caiyang_starts])    
    #为每一项添加一个空list，用于存放抽样统计某时间断内挂号患者数量
    for j in range(0,len(guahaoqingkuang_zhuanjia_fenshi)):
        guahaoqingkuang_zhuanjia_fenshi[j].append([])
    #判断所有挂号患者属于该时间段的人数
    for e in range(0,len(caiyang_starts_all)):       
        #计算一个时间段中所有采样单位时间内挂号人数，每个caiyang_starts_all[e][2][i]是一个采样时间
        for i in range(0,len(caiyang_starts_all[e][2])):
            #计算某日一个专家在指定采样单位时间中挂号的患者人数，每个j对应一个日期
            for j in range(0,len(guahaoqingkuang_zhuanjia_fenshi)):                
                n = 0
                renshupinci_temp = copy.deepcopy(renshupinci)
                for k in guahaoqingkuang_zhuanjia_fenshi[j][4]:
                    #判断每个挂号时间k转化为秒之后，是否在采样的时间点及其后60秒之间。
                    if isTimeInRange(caiyang_starts_all[e][2][i],caiyang_starts_all[e][2][i]+unit_time*60,dataProcess.time_to_second(k)):
                        n = n + 1
                #因为renshupinci每个索引号刚好对应采样同时挂号的人数个数，故当n>= len(renshupinci)-1，若len(renshupinci)=6，即采样中到达的挂号人数当不少于5人时，renshupinci最后一个元素加1
                if n >= len(renshupinci)-1:
                    renshupinci_temp[len(renshupinci)-1] = renshupinci_temp[len(renshupinci)-1] + 1
                else:
                    renshupinci_temp[n] = renshupinci_temp[n] + 1
                guahaoqingkuang_zhuanjia_fenshi[j][-1].append([caiyang_starts_all[e][0],caiyang_starts_all[e][1],renshupinci_temp])

    print(guahaoqingkuang_zhuanjia_fenshi)
    for i in range(0,len(guahaoqingkuang_zhuanjia_fenshi)):
        t_start = guahaoqingkuang_zhuanjia_fenshi[i][6][0][0]
        t_end = guahaoqingkuang_zhuanjia_fenshi[i][6][0][1]
        renshupinci = [guahaoqingkuang_zhuanjia_fenshi[i][6][0][2]]
        renshupinci_final = []
        for j in range(1,len(guahaoqingkuang_zhuanjia_fenshi[i][6])):
            if guahaoqingkuang_zhuanjia_fenshi[i][6][j][0] == t_start and guahaoqingkuang_zhuanjia_fenshi[i][6][j][1] == t_end:
                renshupinci.append(guahaoqingkuang_zhuanjia_fenshi[i][6][j][2])
            else:
                renshupinci_final.append([t_start,t_end,renshupinci])
                t_start = guahaoqingkuang_zhuanjia_fenshi[i][6][j][0]
                t_end = guahaoqingkuang_zhuanjia_fenshi[i][6][j][1]
                renshupinci = [guahaoqingkuang_zhuanjia_fenshi[i][6][j][2]]
        renshupinci_final.append([t_start,t_end,renshupinci])
        guahaoqingkuang_zhuanjia_fenshi[i].append(renshupinci_final)
        guahaoqingkuang_zhuanjia_fenshi[i].append([])
    
    for i in range(0,len(guahaoqingkuang_zhuanjia_fenshi)):
        for n in range(0,len(guahaoqingkuang_zhuanjia_fenshi[i][7])):
            
            list_sum = guahaoqingkuang_zhuanjia_fenshi[i][7][n][2][0]
            for j in range(1,len(guahaoqingkuang_zhuanjia_fenshi[i][7][n][2])):
                list_sum_temp = []
                for k,l in zip(list_sum,guahaoqingkuang_zhuanjia_fenshi[i][7][n][2][j]):
                    list_sum_temp.append(k+l)
                list_sum = copy.deepcopy(list_sum_temp)
            guahaoqingkuang_zhuanjia_fenshi[i][8].append([guahaoqingkuang_zhuanjia_fenshi[i][7][n][0],guahaoqingkuang_zhuanjia_fenshi[i][7][n][1],list_sum])
    #print(guahaoqingkuang_zhuanjia_fenshi)
    for i in range(0,len(guahaoqingkuang_zhuanjia_fenshi)):
        del guahaoqingkuang_zhuanjia_fenshi[i][7]
        del guahaoqingkuang_zhuanjia_fenshi[i][6]
        del guahaoqingkuang_zhuanjia_fenshi[i][4]
        
    print(guahaoqingkuang_zhuanjia_fenshi)
    return guahaoqingkuang_zhuanjia_fenshi
        

def main():
    file = "outpatientRecord.xlsx"
    caiyangdanweishichang = 1 #每次采样的时间长度
    caiyangcishu = 200 #采样次数
    guahaoqingkuang_zhuanjia_fenshi = fileProcess(file,caiyangdanweishichang,caiyangcishu)
    #各科室每个专家所有日期不同时段挂号患者数据分布评估： 
    keshi = ""
    haoyuanming = ""
    zhuanjia = ""
    fuwushijian = 0
    guahaoqingkuang_zhuanjia = []
    guahaoqingkuang_zhuanjia_temp = []
       
    
    #把guahaoqingkuang_zhuanjia_fenshi中属于同一专家不同日期的采样结果合并，得到总的各时段内的采样结果guahaoqingkuang_zhuanjia
    for e in guahaoqingkuang_zhuanjia_fenshi:
        if len(keshi)==0 or len(haoyuanming)==0 or len(zhuanjia)==0 or fuwushijian==0:
            keshi = e[1]
            haoyuanming = e[2]
            zhuanjia = e[3]        
            fuwushijian = e[4]
            guahaoqingkuang_zhuanjia_temp = e[5]
            continue
        print(e)
        if keshi!=e[1] or haoyuanming!=e[2] or zhuanjia!=e[3] or fuwushijian!=e[4]:
            guahaoqingkuang_zhuanjia.append([keshi,haoyuanming,zhuanjia,fuwushijian,guahaoqingkuang_zhuanjia_temp])
            keshi = e[1]
            haoyuanming = e[2]
            zhuanjia = e[3]
            fuwushijian = e[4]            
            guahaoqingkuang_zhuanjia_temp = e[5]                       
        else:#两个e中e[5]各项合并
            for i in range(0,len(e[5])):
                t = np.sum([e[5][i][2],guahaoqingkuang_zhuanjia_temp[i][2]],axis=0).tolist()
                guahaoqingkuang_zhuanjia_temp[i][2]= t
    guahaoqingkuang_zhuanjia.append([keshi,haoyuanming,zhuanjia,fuwushijian,guahaoqingkuang_zhuanjia_temp]) 
    

    #记录不同日期各时段内患者到达数量
    for e in guahaoqingkuang_zhuanjia:
        print("\n")
        print(e[0],e[1],e[2])

        for j in range(0,len(e[4])):        
            print(e[4][j][0] + "——" + e[4][j][1])
            #单位时间内到达患者数量
            data_weight = [i for i in range(0,len(e[4][j][2]))]
            possionTest(e[4][j][2],data_weight)  

    
if __name__=="__main__":
    main()