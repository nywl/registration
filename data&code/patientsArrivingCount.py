#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 21 22:09:37 2018

@author: pc
"""
import numpy as np
import dataProcess
import pandas as pd
import possionTest
import copy
import grayPredict

caiyangdanweishichang = 1 #每次采样的时间长度
caiyangcishu = 200 #采样次数
possion_len = 5 #统计单位时间内挂号人数（5表示挂号人数分别为0,1,2,3,4以及大于等于5的患者数量）
jiuzhenshiduan = 60 #一个分时就诊时段的长度，单位为分钟

#根据每个日期的患者在各时段的到达采样情况，利用灰度预测计算达到人数

#各分时就诊时段取号人数平均值、方差、标准差的计算（输入k个服务周期，用前k-1个周期的数据求每分钟内到达人数，计算其与第k个周期人数的差值），返回各时段起始时间、结束时间、取号人数的均值、标准差
def average_guahaorenshu(guahaorenshu_count,daodashijian):
    #计算某专家在各日期各分时时段的泊松抽样结果（由于是统计一天各时段的，对于只有上午或下午坐诊的情况，未工作时段也会计算，不过抽样结果是0个人达到）
    #该泊松采样是把钱k-1个周期的所有到达数据混合抽样的
    possion_data = possionTest.possion_dataProcess(daodashijian,caiyangdanweishichang,caiyangcishu)
    data_weight = [i for i in range(0,possion_len+1)] 
    #各时段根据泊松采样结果求到达人数
    for i in range(0,len(possion_data)):
        avg_possion = []
        for j in range(0,len(possion_data[i][5])):
            #possion_data[i][5][j][2]对应一次泊松采样中同时挂号人数为1~5的人数统计
            data_weighted = [a*b for a,b in zip(possion_data[i][5][j][2],data_weight)]
            avg_possion_temp = sum(data_weighted)/sum(possion_data[i][5][j][2])#每分钟到达人数
            avg_possion.append(avg_possion_temp)
        possion_data[i].append(avg_possion)
    
    #把同一专家不同服务周期的泊松采样数据在各分时时段的均值求均值
    possion_data_morning = [e for e in possion_data if e[4]=="1"]
    possion_data_afternoon = [e for e in possion_data if e[4]=="2"]
    avg_all_possion = [] #存储各分时时段泊松采样均值的平均值
    possion_data_morning_temp = [0.0,0.0,0.0,0,0.0]
    possion_data_afternoon_temp = [0.0,0.0,0.0,0.0]
    #k个服务周期，把前k-1个求均值，均值用来比较与最后一个周期的差值
    if(len(possion_data_morning)-1>0):
        for i in range(0,len(possion_data_morning)-1):
            possion_data_morning_temp = copy.deepcopy([a+b for a,b in zip(possion_data_morning_temp,possion_data_morning[i][6][0:5])])
            if(i==len(possion_data_morning)-2):
                possion_data_morning_temp = [a/(i+1) for a in possion_data_morning_temp]
    if(len(possion_data_afternoon)-1>0):
        for i in range(0,len(possion_data_afternoon)-1):
            possion_data_afternoon_temp = copy.deepcopy([a+b for a,b in zip(possion_data_afternoon_temp,possion_data_afternoon[i][6][5:9])])
            if(i==len(possion_data_afternoon)-2):
                possion_data_afternoon_temp = [a/(i+1) for a in possion_data_afternoon_temp]
    avg_all_possion = possion_data_morning_temp + possion_data_afternoon_temp
    #avg_all_possion是每分钟到达人数，要乘以时间长度得出每个分时时段内到达人数
    avg_all_possion_num = [i*jiuzhenshiduan for i in avg_all_possion]
    
    #抽出每天的现场到达人数，放入list[list]中，外部的list中每个元素对应服务周期中的一个服务时间段，内部list中每个元素对应不同服务周期的相同服务时段中到达的现场患者
    guahaorenshu_count_temp = []
    guahaorenshu_count_temp_all = [] #每个元素为一个list，对应存放所有服务周期中某个相同的时段内的到达人数
    for i in range(0,len(guahaorenshu_count)): 
        for j in range(0,len(guahaorenshu_count[i][1])):
            if(len(guahaorenshu_count_temp_all)<j+1):
                guahaorenshu_count_temp = []
                guahaorenshu_count_temp.append(guahaorenshu_count[i][1][j][2])
                guahaorenshu_count_temp_all.append(guahaorenshu_count_temp)
            else:
                guahaorenshu_count_temp_all[j].append(guahaorenshu_count[i][1][j][2])
    
#    #根据挂号的分时时段对患者进行分组
#    daodashijian_fenshi = []
#    for i in range(0,len(guahaorenshu_count[0][1])):
#        daodashijian_fenshi_temp = [e for e in daodashijian if dataProcess.time_to_second(e[2])>=dataProcess.time_to_second(guahaorenshu_count[0][1][i][0]) and dataProcess.time_to_second(e[2])<dataProcess.time_to_second(guahaorenshu_count[0][1][i][1])]
##        if(len(daodashijian_fenshi_temp)>0):
##            daodashijian_fenshi.append(daodashijian_fenshi_temp)
#        daodashijian_fenshi.append(daodashijian_fenshi_temp) #当某时段内没有现场挂号患者，则加入一个空的list
      
#    e_mean_possion_fenshi = []
#    #每个e对应一个分时就诊时段，包含所有日期在该时段的到达人数，当某时段内没有现场挂号患者，则对应一个空的list元素值
#    for e in daodashijian_fenshi:  
#        e_mean_possion = [] #存放一个周期内各分时就诊时段的平均到达人数
#        if(len(e)>0):
#            #各专家在各服务周期不同分时时段的泊松抽样结果
#            possion_data = possionTest.possion_dataProcess(e,caiyangdanweishichang,caiyangcishu)
#            
#            #每个循环计算一个分时就诊时段内的平均达到人数
#            for e1 in possion_data[0][5]:
#                data_weighted = [a*b for a,b in zip(e1[2],data_weight)]
#                mu = sum(data_weighted)/sum(e1[2])
#                e_mean_possion.append(mu)
#        else:
#            e_mean_possion.append(0.0)
#        #e_mean_possion是每分钟到达人数，要乘以时间长度得出每个分时时段内到达人数
#        e_mean_possion_fenshi.append((np.sum(e_mean_possion)/len(guahaorenshu_count))*jiuzhenshiduan)
        
    guahaorenshu_stat = []  
    #每个k对应一个分时时段，包含该时段内各服务周期泊松估计的到达人数     
    for k in range(0,len(guahaorenshu_count_temp_all)):
        #直接求均值、标准差
#        e_mean = np.mean(guahaorenshu_count_temp_all[k])
#        #e_var = np.var(guahaorenshu_count_temp_all[k])
#        e_std = np.std(guahaorenshu_count_temp_all[k],ddof=1) #ddof=1是求无偏标准差，分母为n-1，默认分母是n，即有偏的
#        #guahaorenshu_count包含各就诊时段的起始和结束时间，取首个list元素中guahaorenshu_count[0][1]包含的各时段的起始和结束时间
#        guahaorenshu_stat.append([guahaorenshu_count[0][1][k][0],guahaorenshu_count[0][1][k][1],e_mean,e_std])
        
        if(len(guahaorenshu_count_temp_all[k])>0):
            e_std_possion = ((guahaorenshu_count_temp_all[k][-1]-avg_all_possion_num[k])**2)**(1./2)
            guahaorenshu_stat.append([guahaorenshu_count[0][1][k][0],guahaorenshu_count[0][1][k][1],avg_all_possion_num[k],e_std_possion])
        else:
            guahaorenshu_stat.append([guahaorenshu_count[0][1][k][0],guahaorenshu_count[0][1][k][1],avg_all_possion_num[k],0.0])
        
#        #利用抽样求得的各日期平均值的平均值，结合各日期各时段实际到达人数求标准差(若某时段内无现场患者，则无法通过泊松分布估计到达人数，因而在e_mean_possion_fenshi[k]中无对应项，均值方差均设置为0)
#        if(np.sum(guahaorenshu_count_temp_all[k][0:-1])>0): #判断所有周期同一时段达到人数之和是否大于0
#            #各分时时段内各服务周期的达到人数与均值求标准差
#            e_std_possion_temp = [((i-avg_all_possion_num[k])**2)**(1./2) for i in guahaorenshu_count_temp_all[k]]        
#            #各分时时段内所有服务周期到达人数标准差的平均值
#            e_std_possion = np.mean(e_std_possion_temp)       
#            guahaorenshu_stat.append([guahaorenshu_count[0][1][k][0],guahaorenshu_count[0][1][k][1],avg_all_possion_num[k],e_std_possion])
#        else:
#            guahaorenshu_stat.append([guahaorenshu_count[0][1][k][0],guahaorenshu_count[0][1][k][1],avg_all_possion_num[k],0.0])

    return guahaorenshu_stat
    
#    guahaorenshu_count_temp = copy.deepcopy(guahaorenshu_count[0][1])
#    for i in range(1,len(guahaorenshu_count)):        
#        for j in range(0,len(guahaorenshu_count[i][1])):
#            guahaorenshu_count_temp[j][2] = guahaorenshu_count_temp[j][2] + guahaorenshu_count[i][1][j][2]
#            if(i==len(guahaorenshu_count)-1):
#                guahaorenshu_count_temp[j][2] = guahaorenshu_count_temp[j][2]/len(guahaorenshu_count)
#    return guahaorenshu_count_temp

#用于灰度预测的周期均为上午或下午，没有上下午混合的情况
def huidu_dataprocess(daodashijian_huidu_temp):
    daodarenshu_eachday = []
    for e in daodashijian_huidu_temp:
        possion_data = possionTest.possion_dataProcess(e,caiyangdanweishichang,caiyangcishu)
        data_weight = [i for i in range(0,possion_len+1)] 
        #各时段根据泊松采样结果求到达人数
        for i in range(0,len(possion_data)):
            avg_possion = []
            for j in range(0,len(possion_data[i][5])):
                #possion_data[i][5][j][2]对应一次泊松采样中同时挂号人数为1~5的人数统计
                data_weighted = [a*b for a,b in zip(possion_data[i][5][j][2],data_weight)]
                avg_possion_temp = sum(data_weighted)/sum(possion_data[i][5][j][2])#每分钟内达到人数
                avg_possion.append(avg_possion_temp)
            avg_possion_daodarenshu = [x*jiuzhenshiduan for x in avg_possion] #泊松采样估算的某日期各时段的到达人数
            daodarenshu_eachday.append(avg_possion_daodarenshu)  
    #取前k-1个服务周期计算预测值，与最后一个周期真实值进行比较  
    e_std = [] #记录各个属性列的真实值和预测值的标准差，即每个分时就诊时段单独统计预测     
    #for i in range(0,len(daodarenshu_eachday[0])): #i为列索引，取不同记录同一列
    for i in range(0,5):
        one_column_daodarenshu = [[x[i]] for x in daodarenshu_eachday] #取不同日期同一时段的到达人数形成list
        one_column_daodarenshu1 = one_column_daodarenshu[0:-1]
        daodarenshu_shiji = one_column_daodarenshu[-1]
        
        df = pd.DataFrame(data=np.array(one_column_daodarenshu1),columns=["dadaorenshu"])
        gf = grayPredict.GrayForecast(df, 'dadaorenshu')
        gf.forecast(time=1,forecast_data_len=len(df))
        daodarenshu_yuce = gf.log().iloc[-1]['dadaorenshu']
        e_std_temp = ((daodarenshu_shiji-daodarenshu_yuce)**2)**(1./2)
        e_std.append(e_std_temp)
    return e_std
    
        
        
    

    
    



#某专家所有日期各时段到达患者数量统计,计算不同步长下到达人数的泊松估计与下一次到达人数的标准差，找出相同步长下标准差之和最小的步长，作为预估到达人数所需的历史服务周期数量
def daodarenshutongji(daodashijian):
    result_data = np.array(daodashijian)
    column_keys = ["id", "guahao_date", "guahao_time", "jiuzhen_date", "jiuzhen_time","keshi", "zhuanjia","leixing","houzhenshichang","jiuzhenshichang","fuwuzhouqi","haoyuanming"]
    df = pd.DataFrame(data=result_data,columns=column_keys)
    df = df[df["leixing"]=="on-site"]
    group_keys = ["guahao_date","fuwuzhouqi"]
    df1 = dict(list(df.groupby(group_keys)))  
    guahaorenshu_count_each_zhuanjia = [] #记录每个专家每个服务周期的患者到达情况
    guahaorenshu_count_each_zhuanjia_avg = [] #记录每个专家若干服务周期的患者到达情况的平均值
    guahaorenshu_count1 = [] #记录某专家一个服务周期内(上午)各时段取号人数
    guahaorenshu_count2 = [] #记录某专家一个服务周期内(下午)各时段取号人数
    for e in df1:#统计每个服务周期内各时段取号人数
        guahaorenshu_count_oneday = dataProcess.init_shijianduan(60)
        #统计时，先判断服务周期，如果是下午，不统计上午时段的取号人数
        if(e[1]=="1"):
            guahaorenshu_count_oneday = guahaorenshu_count_oneday[0:5]
        elif(e[1]=="2"):
            guahaorenshu_count_oneday = guahaorenshu_count_oneday[5:9]
        quhaoqingkuang = df1[e]
        
        for i in range(0,len(quhaoqingkuang)):
            guahao_time = quhaoqingkuang.iloc[i]["guahao_time"]
            for j in range(0,len(guahaorenshu_count_oneday)):
                time1 = dataProcess.time_to_second(guahao_time)
                time2 = dataProcess.time_to_second(guahaorenshu_count_oneday[j][0])
                time3 = dataProcess.time_to_second(guahaorenshu_count_oneday[j][1])
                if(time1>=time2 and time1<time3):
                    guahaorenshu_count_oneday[j][2] = guahaorenshu_count_oneday[j][2] + 1
                    break
        if(e[1]=="1"):
            guahaorenshu_count1.append([e,guahaorenshu_count_oneday])
        elif(e[1]=="2"):
            guahaorenshu_count2.append([e,guahaorenshu_count_oneday])
            
    #动态规划算法求标准差最小的平均值
    
    #计算一个专家所有服务周期各时段取号人数平均值,把上午和下午的分开求平均

    guahaorenshu_min_std1 = [] #保存标准差均值最小的步长
    guahaorenshu_min_std1_all = []#保存各步长的标准差均值
    guahaorenshu_min_std2 = []
    
    guahaorenshu_min_std1_huidu = []
    guahaorenshu_min_std1_huidu_all = [] #把不同步长的标准差都保存，看标准差是否随着步长增加而降低
    
    if(len(guahaorenshu_count1)>0): 
        #至少根据四个服务周期的挂号人数来求平均值和标准差，k代表取多少个相邻日期的服务周期用于取号患者数量估计（其中前k-1个计算均值，和第k个比较计算标准差，找标准差最小的k取值）
        for k in range(4,len(guahaorenshu_count1)):#k从4开始
            guahaorenshu_min_std1_huidu_temp = [] #同一步长取不同数据的灰度预测与真实值标准差的集合
            guahaorenshu_min_std1_temp1 = []
            #对于同一步长k，不同的i对应取不同的样本值进行到达人数预测
            for i in range(0,len(guahaorenshu_count1)-k):
                guahaorenshu_count1_temp = guahaorenshu_count1[i:i+k+1] #取i+k个元素进行均值方差计算
                
                #增加调用灰度预测计算到达人数。随着步长k的增加，取最近k个周期的到达人数进行估计，
                #取最近k个周期的到达人数，用前k-1的数据预测第k次，看与实际第k次的差值
                daodashijian_huidu_temp = [] #每个元素是一个list，包含某个服务周期内的患者就诊记录                
                #取出相应步长的患者就诊记录
                for e in guahaorenshu_count1_temp:
                    daodashijian_huidu_temp1 = [m for m in daodashijian if m[1]==e[0][0] and m[10]==e[0][1]]
                    if(len(daodashijian_huidu_temp1)>0):
                        daodashijian_huidu_temp.append(daodashijian_huidu_temp1)                        
                guahaorenshu_min_std1_huidu_temp.append(huidu_dataprocess(daodashijian_huidu_temp))
                
                
                
                #对于同一步长k，不同的i对应取不同的样本值进行均值和方差估算
                daodashijian_temp = []
                for e in guahaorenshu_count1_temp:
                    daodashijian_temp1 = [m for m in daodashijian if m[1]==e[0][0] and m[10]==e[0][1]]
                    if(len(daodashijian_temp1)>0):
                        daodashijian_temp = daodashijian_temp + daodashijian_temp1
                guahaorenshu_min_std1_temp = average_guahaorenshu(guahaorenshu_count1_temp,daodashijian_temp)
                if(len(guahaorenshu_min_std1)==0):                
                    for e in guahaorenshu_min_std1_temp:                      
                        guahaorenshu_min_std1.append([e[0],e[1],k-1,e[2],e[3]])   
                         
                elif(guahaorenshu_min_std1[0][2]==k): #                     
                    #每个j对应一个时间段
                    for j in range(0,len(guahaorenshu_min_std1)):
                        #统计步长相等的采样计算的均值和方差的平均值
                        guahaorenshu_min_std1[j][3] = guahaorenshu_min_std1[j][3] + guahaorenshu_min_std1_temp[j][2]
                        guahaorenshu_min_std1[j][4] = guahaorenshu_min_std1[j][4] + guahaorenshu_min_std1_temp[j][3]
                        if(i==len(guahaorenshu_count1)-k-1):
                            guahaorenshu_min_std1[j][3] = guahaorenshu_min_std1[j][3]/(i+1)
                            guahaorenshu_min_std1[j][4] = guahaorenshu_min_std1[j][4]/(i+1)
                            
                            guahaorenshu_min_std1_all.append(guahaorenshu_min_std1[j]) 
                            
                #k不等，再计算其他步长对应的均值、方差的平均值与现有的比较大小
                elif(len(guahaorenshu_min_std1_temp1)==0):                           
                    for e in guahaorenshu_min_std1_temp:                                
                        guahaorenshu_min_std1_temp1.append([e[0],e[1],k-1,e[2],e[3]])   
                    
                else:
                    for m in range(0,len(guahaorenshu_min_std1_temp1)):
                        #guahaorenshu_min_std1_temp1[m][3] = guahaorenshu_min_std1_temp1[m][3] + guahaorenshu_min_std1_temp[j][2]
                        #guahaorenshu_min_std1_temp1[m][4] = guahaorenshu_min_std1_temp1[m][4] + guahaorenshu_min_std1_temp[j][3]
                        guahaorenshu_min_std1_temp1[m][3] = guahaorenshu_min_std1_temp1[m][3] + guahaorenshu_min_std1_temp[m][2]
                        guahaorenshu_min_std1_temp1[m][4] = guahaorenshu_min_std1_temp1[m][4] + guahaorenshu_min_std1_temp[m][3]
                        if(i==len(guahaorenshu_count1)-k-1):
                            guahaorenshu_min_std1_temp1[m][3] = guahaorenshu_min_std1_temp1[m][3]/(i+1)
                            guahaorenshu_min_std1_temp1[m][4] = guahaorenshu_min_std1_temp1[m][4]/(i+1)
                            guahaorenshu_min_std1_all.append(guahaorenshu_min_std1_temp1[m])
                            if(guahaorenshu_min_std1_temp1[m][4]<guahaorenshu_min_std1[m][4]):
                                guahaorenshu_min_std1[m][2] = k-1
                                guahaorenshu_min_std1[m][3] = guahaorenshu_min_std1_temp1[m][3]
                                guahaorenshu_min_std1[m][4] = guahaorenshu_min_std1_temp1[m][4]
            guahaorenshu_min_std1_temp1 = []  
            
            #灰度预测,同一步长不同数据计算出的各就诊时段预测值与真实值的差值求平均   
            
            guahaorenshu_min_std1_huidu_temp_array = np.array(guahaorenshu_min_std1_huidu_temp)
            std_avg = []
            std_avg = guahaorenshu_min_std1_huidu_temp_array.mean(axis=0)
            
            #比较找出各分时就诊时段标准差最小的步长
            if(len(guahaorenshu_min_std1_huidu)==0):
                for e in std_avg:
                    guahaorenshu_min_std1_huidu.append([k-1,e])
            else:
                for i in range(0,len(std_avg)):
                    if(guahaorenshu_min_std1_huidu[i][1]>std_avg[i]):
                        guahaorenshu_min_std1_huidu[i] = []
                        guahaorenshu_min_std1_huidu[i] = [k-1,std_avg[i]]
            
            guahaorenshu_min_std1_huidu_all.append(std_avg)
                
            
    if(len(guahaorenshu_count2)>0):        
        #至少根据两个服务周期的挂号人数来求平均值和标准差，k代表取多少个相邻日期的服务周期用于取号患者数量估计，至少取4个周期，前三个用于估计，第四个用于计算标准差
        for k in range(4,len(guahaorenshu_count2)):#k从1开始
            guahaorenshu_min_std2_temp2 = []
            #对于同一步长k，不同的i对应取不同的样本值进行均值和方差估算
            for i in range(0,len(guahaorenshu_count2)-k):
                guahaorenshu_count2_temp = guahaorenshu_count2[i:i+k+1] #取i+0~i+k共k+1个元素，前k个进行均值方差计算
                guahaorenshu_min_std2_temp = average_guahaorenshu(guahaorenshu_count2_temp,daodashijian)
                if(len(guahaorenshu_min_std2)==0):                
                    for e in guahaorenshu_min_std2_temp:                      
                        guahaorenshu_min_std2.append([e[0],e[1],k-1,e[2],e[3]])                        
                elif(guahaorenshu_min_std2[0][2]==k):                      
                    #每个j对应一个时间段
                    for j in range(0,len(guahaorenshu_min_std2)):
                        #统计步长相等的采样计算的均值和方差的平均值
                        guahaorenshu_min_std2[j][3] = guahaorenshu_min_std2[j][3] + guahaorenshu_min_std2_temp[j][2]
                        guahaorenshu_min_std2[j][4] = guahaorenshu_min_std2[j][4] + guahaorenshu_min_std2_temp[j][3]
                        if(i==len(guahaorenshu_count2)-k-1):
                            guahaorenshu_min_std2[j][3] = guahaorenshu_min_std2[j][3]/(i+1)
                            guahaorenshu_min_std2[j][4] = guahaorenshu_min_std2[j][4]/(i+1)
                #步长k不等，再计算其他步长对应的均值、方差的平均值与现有的比较大小
                elif(len(guahaorenshu_min_std2_temp2)==0):                           
                    for e in guahaorenshu_min_std2_temp:                                
                        guahaorenshu_min_std2_temp2.append([e[0],e[1],k-1,e[2],e[3]])    
                else:
                    for m in range(0,len(guahaorenshu_min_std2_temp2)):
                        #guahaorenshu_min_std2_temp2[m][3] = guahaorenshu_min_std2_temp2[m][3] + guahaorenshu_min_std2_temp[j][2]
                        #guahaorenshu_min_std2_temp2[m][4] = guahaorenshu_min_std2_temp2[m][4] + guahaorenshu_min_std2_temp[j][3]
                        guahaorenshu_min_std2_temp2[m][3] = guahaorenshu_min_std2_temp2[m][3] + guahaorenshu_min_std2_temp[m][2]
                        guahaorenshu_min_std2_temp2[m][4] = guahaorenshu_min_std2_temp2[m][4] + guahaorenshu_min_std2_temp[m][3]
                        if(i==len(guahaorenshu_count1)-k-1):
                            guahaorenshu_min_std2_temp2[m][3] = guahaorenshu_min_std2_temp2[m][3]/(i+1)
                            guahaorenshu_min_std2_temp2[m][4] = guahaorenshu_min_std2_temp2[m][4]/(i+1)
                            if(guahaorenshu_min_std2_temp2[m][4]<guahaorenshu_min_std2[m][4]):
                                guahaorenshu_min_std2[m][2] = k-1
                                guahaorenshu_min_std2[m][3] = guahaorenshu_min_std2_temp2[m][3]
                                guahaorenshu_min_std2[m][4] = guahaorenshu_min_std2_temp2[m][4]                                          
            guahaorenshu_min_std2_temp2 = []
    
        

    guahaorenshu_count_each_zhuanjia=[df.iloc[0]["keshi"],df.iloc[0]["haoyuanming"],df.iloc[0]["zhuanjia"],guahaorenshu_count1,guahaorenshu_count2]
    guahaorenshu_count_each_zhuanjia_avg=[df.iloc[0]["keshi"],df.iloc[0]["haoyuanming"],df.iloc[0]["zhuanjia"],guahaorenshu_min_std1,guahaorenshu_min_std2]
    return guahaorenshu_count_each_zhuanjia,guahaorenshu_count_each_zhuanjia_avg,guahaorenshu_min_std1_huidu,guahaorenshu_min_std1_huidu_all,guahaorenshu_min_std1_all

    
    
def main():
    xianchang = []
    xianchangs = []
    yuyue = []
    yuyues = []
    haoyuanming = ""
    zhuanjia = ""
    #读入的文件是按取号时间排序后的患者队列
    f = open("patients_guahao_time_sorted.txt","r",encoding='utf-8')
    line = f.readline()              		 # 调用文件的 readline()方法
    while line:   
    	s = line.split(",")
    	if haoyuanming == "" and zhuanjia == "":
            haoyuanming = s[5]
            zhuanjia = s[6]
    	elif haoyuanming!=s[5] or zhuanjia!=s[6]:
            xianchangs.append(xianchang)
            xianchang = []
            yuyues.append(yuyue)
            yuyue = []
            haoyuanming = s[5]
            zhuanjia = s[6]
        
    	if s[7]=="on-site":
            xianchang.append(s)
    	elif s[7]=="appointment":
            yuyue.append(s)    	
    	line = f.readline()    
    xianchangs.append(xianchang)
    yuyues.append(yuyue)
    f.close()
    
    
    daodarenshu = []
    daodarenshu_avg = []

    for e in xianchangs:
        daodarenshu_temp,daodarenshu_temp_avg,huiduyuce_shangwu,huiduyuce_shangwu_all,guahaorenshu_min_std1_all = daodarenshutongji(e)
        daodarenshu.append(daodarenshu_temp)
        daodarenshu_avg.append(daodarenshu_temp_avg)

    file_final=open('patientsArrivingCount.txt','w')
    file_final.write(str(daodarenshu))
    file_final.write("\n")
    file_final.write(str(daodarenshu_avg))
    file_final.write("\n")
    file_final.write(str(huiduyuce_shangwu))

    file_final.close()
    
    for e in daodarenshu_avg:
        for i in range(0,len(e[3])-1):
            print("service time slot:",e[3][i][0],"-",e[3][i][1])
            print("optimal number of service cycles used for estimation:",e[3][i][2])
            print("standard deviation:",e[3][i][3])
            
            print("optimal number of service cycles used for estimation(gray prediction):",huiduyuce_shangwu[i][0])
            print("standard deviation(gray prediction):",huiduyuce_shangwu[i][1][0])
            
    

        

    
    
if __name__=="__main__":
    main()