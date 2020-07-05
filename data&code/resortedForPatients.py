#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import dataProcess
import pandas as pd
import copy

jiezhenshijianduan1 = {0:('08:00:00','09:00:00'),1:('09:00:00','10:00:00'),2:('10:00:00','11:00:00'),3:('11:00:00','12:00:00')}
jiezhenshijianduan2 = {0:('14:30:00','15:30:00'),1:('15:30:00','16:30:00'),2:('16:30:00','17:30:00')}
test_para = "non-test" #调度策略选择，non-test预约患者优先，test1现场患者优先，test2先到先就诊
test_date = "2019-03-06"

#input:输入的患者挂号就诊情况文件，jiezhenshuliang是的list除最后一个分时就诊时间段外其他就诊时间段内预留挂号人数的list
#output:list[list[list]],list[list],DataFrame,返回值说明见函数houzhenshijianRecompute的输入参数解释
#def resortedHouzhen(file,jiezhenshuliang1,jiezhenshuliang2):
def resortedHouzhen(file,gusuanxianchangrenshu1_temp,gusuanxianchangrenshu2_temp):
    xianchang = []
    xianchangs = []
    yuyue = []
    yuyues = []
    keshi = ""
    haoyuanming = ""
    zhuanjia = ""
    last_patients = [] #存储最后就诊患者
    #创建一个空的dataframe
    df = pd.DataFrame(columns = ["id", "guahao_date", "guahao_time", "jiuzhen_date", "jiuzhen_time","keshi", "zhuanjia","leixing", "houzhenshichang","jiuzhenshichang","fuwushiduanbiaoji","haoyuanming"]) 
    #读入的文件是按接诊时间排序后的患者队列
   
    for line in open(file,"r",encoding='utf-8'):         		 # 逐行处理大文件的高效方法
    #while line:   
    	s = line.split(",")
    	s[1] = dataProcess.dateFormat(s[1])
        #测试代码
    	if(s[3]!=test_date):
            continue

    	if keshi == "" and zhuanjia == "":
            keshi = s[5]
            zhuanjia = s[6]
            haoyuanming = s[11]
    	elif keshi!=s[5] or zhuanjia!=s[6] or haoyuanming!=s[11]:
            xianchangs.append(xianchang)
            xianchang = []
            yuyues.append(yuyue)
            yuyue = []
            keshi = s[5]
            haoyuanming = s[11]
            zhuanjia = s[6]
        #找出就诊时长为0的患者（即最后就诊患者），不把其放入现场、预约的list中
    	if s[9] == "0":
            last_patients.append(s)
            #line = f.readline()
            continue        
    	df = df.append({'id':s[0],'guahao_date':s[1], 'guahao_time':s[2], 'jiuzhen_date':s[3], 'jiuzhen_time':s[4],'keshi':s[5], 'zhuanjia':s[6],'leixing':s[7], 'houzhenshichang':s[8], 'jiuzhenshichang':s[9],'fuwushiduanbiaoji':s[10],'haoyuanming':s[11]},ignore_index=True)
    
        
    	if s[7]=="on-site":
            xianchang.append(s)
    	elif s[7]=="appointment":
            yuyue.append(s)    	
    	#line = f.readline()    
    xianchangs.append(xianchang)
    yuyues.append(yuyue)
    #此处先获取每个服务时间段最早开始服务的时间，用于后续重排序后模拟就诊的服务开始时间
    df1 = dict(list(df.groupby(['keshi','zhuanjia','jiuzhen_date','fuwushiduanbiaoji','haoyuanming'])))
    jiezhenkaishishijian = pd.DataFrame(columns = ["keshi", "zhuanjia","jiuzhen_date", "jiuzhen_time","fuwushiduanbiaoji","haoyuanming"]) 
    for e in df1:
        df1[e] = df1[e].sort_values(by=['jiuzhen_time'],ascending=True)
        jiezhenkaishishijian = jiezhenkaishishijian.append({'keshi':e[0],'zhuanjia':e[1],'jiuzhen_date':e[2],'jiuzhen_time':df1[e].iat[0,4],'fuwushiduanbiaoji':e[3],'haoyuanming':e[4]},ignore_index=True)

        
    
    for i in range(0,len(yuyues)):
        #根据多字段排序时，无法同时就有按某字段升序排，又有按某字段降序排的情况，因此做两次排序，先把同一日期同一服务周期的患者按就诊时长降序排列
        yuyues[i] = sorted(yuyues[i],key=lambda x:(x[1],x[10],int(x[9])),reverse=True)#同一挂号日期，根据服务时段排序，再按照就诊时长排序
        yuyues[i] = sorted(yuyues[i],key=lambda x:(x[1],x[10]))
    #f.close()
    jiezhenxianchanghuanzhe_zhuanjia = [] #每个元素为一个list，存储不同科室专家在不同日期的现场患者情况
    
    for e in xianchangs:
        #在该循环中每次插入患者时先判断就诊时长是否为0，为0则插入last_patients，当一个周期所有患者已插完，如果有最后就诊患者，再插入（可能预约患者是最后就诊患者）直接在最开始获取整体数据时就抽出最后就诊患者，中间过程不管，只在最最后才插入。
        #某科室某专家所有现场挂号患者按照挂号时间先后排序
        e_sorted_guahao = sorted(e,key=lambda x:(x[1],x[10],x[2]))
        yijiezhenrenshu = 0
        jiezhenshijianduan_index = 0#用于标识jiezhenshuliang这个list中第几个元素，对应第几个分时就诊时间段
        guahao_date = ""
        fuwushiduanbiaoji = 0
        jiezhenxianchanghuanzhe = []#每个元素为一个list，存储同一专家某一服务时间段（某天的上午或下午）的现场挂号患者
        jiezhenxianchanghuanzhe_temp = []#每个元素为一个list，存储同一天各分时就诊时段的所有现场挂号患者 
        jiezhenshuliang = []
        #接诊日期不为空
        for s in e_sorted_guahao:           
            if len(guahao_date) == 0 and fuwushiduanbiaoji == 0:
                guahao_date = s[1]
                fuwushiduanbiaoji = int(s[10])

            #同一日期的患者已看完（注意碰上下午还有接诊的看如何处理）的处理
            if s[1] != guahao_date or int(s[10])!=fuwushiduanbiaoji:
                jiezhenshijianduan_index = 0
                yijiezhenrenshu = 0
                guahao_date = s[1]
                fuwushiduanbiaoji = int(s[10])
                jiezhenxianchanghuanzhe.append(jiezhenxianchanghuanzhe_temp)
                jiezhenxianchanghuanzhe_temp = []
            
            #上午时段11：00之前或下午时段16:30之前的各就诊时间段已分配完毕，所有患者放入最后一个时间段
            if((fuwushiduanbiaoji==1 and jiezhenshijianduan_index >= 3) or (fuwushiduanbiaoji==2 and jiezhenshijianduan_index >= 2)):
                jiezhenxianchanghuanzhe_temp.append(s)
                yijiezhenrenshu = yijiezhenrenshu + 1
                continue
            if(fuwushiduanbiaoji==1):
                jiezhenshuliang = copy.deepcopy(gusuanxianchangrenshu1_temp)
            elif(fuwushiduanbiaoji==2):
                jiezhenshuliang = copy.deepcopy(gusuanxianchangrenshu2_temp)
            #11:00之前的当前分时时段没有名额了(不管该时段内是否仍有现场挂号患者候诊)，把当前时段所有患者的list保存，并开始下个时段
            #或者#11:00之前的当前分时时段名额还有，且当前就诊患者的挂号时间不小于该就诊时间段截止时间，放入下一个就诊时间段
            #下午16:30之前的情况同理
            tt1=dataProcess.time_to_second(s[2])
            #患者挂号时间换算成秒一定比-1大，通过tt2和tt3的值是否大于0可以判断是上午还是下午时段就诊
            tt2=-1
            tt3=-1
            if(fuwushiduanbiaoji==1):            
                tt2=dataProcess.time_to_second(jiezhenshijianduan1[jiezhenshijianduan_index][1])
            elif(fuwushiduanbiaoji==2):
                tt3=dataProcess.time_to_second(jiezhenshijianduan2[jiezhenshijianduan_index][1])
            if(yijiezhenrenshu >= jiezhenshuliang[jiezhenshijianduan_index] or ((yijiezhenrenshu < jiezhenshuliang[jiezhenshijianduan_index] and ((fuwushiduanbiaoji==1 and tt1 >= tt2) or (fuwushiduanbiaoji==2 and tt1 >= tt3)) ))):
                yijiezhenrenshu = 0#已接诊人数重新计算
                jiezhenshijianduan_index = jiezhenshijianduan_index + 1#下个时段的索引定位
                jiezhenxianchanghuanzhe.append(jiezhenxianchanghuanzhe_temp)#把当前时段所有患者的list保存
                jiezhenxianchanghuanzhe_temp = []#当前时段患者list清空重新开始下个时段的保存
                yijiezhenrenshu = yijiezhenrenshu + 1#把患者放入新的时段
                jiezhenxianchanghuanzhe_temp.append(s)                
                continue            
            #11:00之前的当前分时时段名额还有，且当前就诊患者的挂号时间在该就诊时间段内，则加入已接诊人数
            if(yijiezhenrenshu < jiezhenshuliang[jiezhenshijianduan_index]):
                if((fuwushiduanbiaoji==1 and tt1 < tt2) or (fuwushiduanbiaoji==2 and tt1 < tt3)):
                    yijiezhenrenshu = yijiezhenrenshu + 1
                    jiezhenxianchanghuanzhe_temp.append(s)

        jiezhenxianchanghuanzhe.append(jiezhenxianchanghuanzhe_temp) 
        jiezhenxianchanghuanzhe_zhuanjia.append(jiezhenxianchanghuanzhe) 
          
    return jiezhenxianchanghuanzhe_zhuanjia,yuyues,jiezhenkaishishijian,last_patients

#各分时就诊时间段内，预约患者和现场患者合并，按挂号时间排序，根据其就诊时长，模拟排队候诊，计算各患者候诊时长，与原时长进行比对，计算现场挂号患者平均候诊时长降低多少   
#input:jiezhenxianchanghuanzhe现场挂号患者在各就诊时段分配的list[list[list]],每个list元素是某科室某专家所有日期的现场挂号患者情况list,第二层list每个元素对应某天某时间段内所有患者情况list，第三层list对应按挂号时间排序的患者情况
#input：yuyues预约患者按就诊时长排序的list[list]，每个list元素是某科室某专家所有日期的预约挂号患者情况list，第二层list每个元素对应按挂号日期、就诊时长排序的患者情况
#input:jiezhenshuliang一个服务时间段内除最后一个分时就诊时间段的其他分时就诊时间段list
#input:jiezhenkaishishijian某个日期某个科室某个专家最早开始接诊时间（此处尚未区分上午、下午时间段），DataFrame包含科室、专家、开始接诊日期、开始接诊时间
def houzhenshijianRecompute(jiezhenxianchanghuanzhe,yuyues,jiezhenshuliang1,jiezhenshuliang2,jiezhenkaishishijian,last_patients):  
    
    for i in range(0,len(jiezhenxianchanghuanzhe)):
        riqi = ""
        fuwushiduanbiaoji=0
        flag = 0
        shijianduan = 0
        jiezhenshuliang = []
        for e in yuyues[i]:#yuyues和jiezhenxianchanghuanzhe等长，每个元素是一个科室某类号源的一个专家的所有日期患者，由于两个list对应元素做处理，故i可同时用作二者下标 
            if len(riqi) == 0:
                riqi = e[1]
                fuwushiduanbiaoji= int(e[10])  
                if(fuwushiduanbiaoji==1):
                    jiezhenshuliang = copy.deepcopy(jiezhenshuliang1)
                elif(fuwushiduanbiaoji==2):
                    jiezhenshuliang = copy.deepcopy(jiezhenshuliang2)  
            restart_flag = True
            while(restart_flag):
                restart_flag = False
                queuelist_len = len(jiezhenxianchanghuanzhe[i])
                for j in range(flag,queuelist_len):    
                    #同一天同一服务周期（上午或下午），判断当前就诊时段是否还有空闲号源(一个list中元素是同一天同一服务周期的同一时段，所以可取list中首个元素的挂号日期与预约患者挂号日期比对)，若没有，则循环检查下一个时间段
                    #一个服务时间段内只剩最后一个分时就诊时间段，前面都已排满，循环把所有相同日期该时间段内的预约患者加入
                    #e[1] == jiezhenxianchanghuanzhe[i][j][0][1]表示预约和现场队列均有同一服务周期内的患者等待排序                
                    #jiezhenshuliang赋值后上午长度为3的list，下午长度为2的list，不为空时shijianduan大于等于其长度，说明只剩最后一个时段（jiezhenshuliang只包含前几个时段），所有预约患者加入该时段
                    if (len(jiezhenxianchanghuanzhe[i][j])==0 or (e[1] == jiezhenxianchanghuanzhe[i][j][0][1] and e[10]==jiezhenxianchanghuanzhe[i][j][0][10])) and shijianduan >= len(jiezhenshuliang):
                        jiezhenxianchanghuanzhe[i][j].append(e)
                        riqi = e[1]
                        fuwushiduanbiaoji= int(e[10]) 
                        flag = j
                        break          
                    #日期不等有两种可能，一是预约队列中当前服务周期患者未分配完(e[1] != jiezhenxianchanghuanzhe[i][j][0][1] or e[10]!=jiezhenxianchanghuanzhe[i][j][0][10])，但当前日期已挂号患者只集中于前几个分时时段（riqi == e[1] and shijianduan < len(jiezhenshuliang)），后几个分时时段未在list中，需要创建;二是预约队列中当前日期患者已全部分配，而当前服务周期的号源仍有,说明这个服务周期内的号没有全部挂出去
                    #因此，读入下一个预约患者需要和前一个预约患者挂号日期以及当前空闲号源对应日期一起比较
                    #某天现场患者少，只有前几个时间段有患者，则后几个时间段对应list元素需插入，新增一个时间段继续插入
                    if (e[1] != jiezhenxianchanghuanzhe[i][j][0][1] or e[10]!=jiezhenxianchanghuanzhe[i][j][0][10]) and (riqi == e[1] and fuwushiduanbiaoji==int(e[10])) and shijianduan < len(jiezhenshuliang):
                        temp_list = []
                        jiezhenxianchanghuanzhe[i].insert(j,temp_list)
                        shijianduan = shijianduan + 1
                        jiezhenxianchanghuanzhe[i][j].append(e)
                        riqi = e[1]
                        fuwushiduanbiaoji= int(e[10]) 
                        flag = j
                        break                
                    #当前日期所有患者已加入，循环找出下个日期候诊队列进行检查
                    if (e[1] != jiezhenxianchanghuanzhe[i][j][0][1] or e[10]!=jiezhenxianchanghuanzhe[i][j][0][10]) and (riqi != e[1] or fuwushiduanbiaoji!=int(e[10])):
                        shijianduan = 0
                        continue
                    #当前日期的患者还有(e[1] == jiezhenxianchanghuanzhe[i][j][0][1])，且未处于服务时间段内最后一个分时就诊时段(shijianduan < len(jiezhenshuliang)，jiezhenshuliang是除了最后一个时段的其他几个时段的list)，但当前时段没有空闲号源（len(jiezhenxianchanghuanzhe[i][j]) >= jiezhenshuliang[shijianduan]），查看下一个时段
                    if (e[1] == jiezhenxianchanghuanzhe[i][j][0][1] and e[10]==jiezhenxianchanghuanzhe[i][j][0][10]) and shijianduan < len(jiezhenshuliang) and len(jiezhenxianchanghuanzhe[i][j]) >= jiezhenshuliang[shijianduan]:
                        shijianduan = shijianduan + 1
                        #jiezhenxianchanghuanzhe[i]起初包含专家不同服务周期各时段分配的现场患者list，list中最后一个服务周期的后几个时段若没有现场患者，则需要插入新的list元素，用于保存该时段内的预约患者
                        if(j==len(jiezhenxianchanghuanzhe[i])-1):
                            temp_list = []
                            jiezhenxianchanghuanzhe[i].insert(j+1,temp_list)
                            queuelist_len = len(jiezhenxianchanghuanzhe[i])
                            restart_flag = True
                            flag = j + 1
                        continue #对于list中已遍历到最后一个元素，需要插入新的空list时，continue和break效果一样，而对于非list中最后一个元素，需要continue
                    #当前日期患者还有，且当前时间段非最后一个时段并仍有空闲号源，直接加入
                    if (e[1] == jiezhenxianchanghuanzhe[i][j][0][1] and e[10]==jiezhenxianchanghuanzhe[i][j][0][10]) and shijianduan < len(jiezhenshuliang) and len(jiezhenxianchanghuanzhe[i][j]) < jiezhenshuliang[shijianduan]:
                        jiezhenxianchanghuanzhe[i][j].append(e)
                        riqi = e[1]
                        fuwushiduanbiaoji= int(e[10]) 
                        flag = j
                        break
                #print(e)


    #每个时段把预约患者排前面，后面是现场挂号的，然后根据挂号时间排序，先按照各自就诊时长计算各自新的候诊时长，根据前一患者接诊时间和就诊时长，结合下一患者的挂号时间计算其就诊时间
    for i in range(0,len(jiezhenxianchanghuanzhe)):
        #每个i对应元素中包含的患者均属于同一科室同一号源名同一专家的
        keshi = jiezhenxianchanghuanzhe[i][0][0][5]
        haoyuanming = jiezhenxianchanghuanzhe[i][0][0][11]
        zhuanjia = jiezhenxianchanghuanzhe[i][0][0][6]
            
        guahao_date = ""
        fuwushiduanbiaoji = 0
        jiezhenshijian_start = ""
        last_patient = []
        #标识是否发现了最后就诊患者，若发现则放入就诊队列最后
        last_flag = 0
        #每个j元素对应的list中仅包含同一服务周期中某个时间段内所有患者，由于存在同一周期不同时段，因此不能在j这层循环中重置开始接诊时间
        for j in range(0,len(jiezhenxianchanghuanzhe[i])): 
            
            #按挂号时间排序，再对排序结果根据挂号类型倒序排序（正序排“现场”在“预约”前面，应把预约患者放前面）
            one_jiuzhenshiduan_xianchang = [a for a in jiezhenxianchanghuanzhe[i][j] if a[7]=="on-site"]
            #现场患者根据挂号时间排序
            one_jiuzhenshiduan_xianchang = sorted(one_jiuzhenshiduan_xianchang,key=lambda x:x[2])
            one_jiuzhenshiduan_yuyue = [a for a in jiezhenxianchanghuanzhe[i][j] if a[7]=="appointment"]
            #预约患者根据就诊时长排序，由于list中所有元素都属于同一服务周期，因此排序时仅需考虑按就诊时长排
            one_jiuzhenshiduan_yuyue = sorted(one_jiuzhenshiduan_yuyue,key=lambda x:x[9],reverse=True)
            #判断若是新的服务周期，则从记录各服务时段开始时间的list中获取最早就诊开始时间
            if((len(guahao_date) == 0 and fuwushiduanbiaoji == 0) or guahao_date!=jiezhenxianchanghuanzhe[i][j][0][1] or fuwushiduanbiaoji!=int(jiezhenxianchanghuanzhe[i][j][0][10])):                        
                #若已扫描到下个服务周期，则在上个服务周期最后时段加入最后就诊患者(前一个if中第一个条件是表明处于初始扫描，第一个条件的否定即为后两个条件为真，非初始扫描中扫描到新的服务时段)
                if(not(len(guahao_date) == 0 and fuwushiduanbiaoji == 0)):
                    if(last_flag==1):
                        last_patient_temp = copy.deepcopy(last_patient[0])
                        last_patient_temp.append(jiezhenshijian_start)
                        last_patient_temp.append(dataProcess.time_to_second(last_patient_temp[4])-dataProcess.time_to_second(jiezhenshijian_start))
                        jiezhenxianchanghuanzhe[i][j-1].append(last_patient_temp)
                        last_flag = 0
                one_jiuzhenshiduan_temp = sorted(jiezhenxianchanghuanzhe[i][j],key=lambda x:x[2])
                guahao_date = one_jiuzhenshiduan_temp[0][1]
                fuwushiduanbiaoji = int(one_jiuzhenshiduan_temp[0][10])
                #最初开始扫描时，寻找该时段内的最后就诊患者
                last_patient = [a for a in last_patients if a[1]==guahao_date and int(a[10])==fuwushiduanbiaoji and a[5]==keshi and a[11]==haoyuanming and a[6]==zhuanjia]
                if(len(last_patient)>0):
                    last_flag = 1
                #list中寻找接诊开始时间所在元素对应的索引位置
                jiezhenshijian_start_index = jiezhenkaishishijian[(jiezhenkaishishijian.keshi==one_jiuzhenshiduan_temp[0][5])&(jiezhenkaishishijian.zhuanjia==one_jiuzhenshiduan_temp[0][6])&(jiezhenkaishishijian.jiuzhen_date==one_jiuzhenshiduan_temp[0][3])&(jiezhenkaishishijian.fuwushiduanbiaoji==one_jiuzhenshiduan_temp[0][10])].index.tolist()[0]  
                #dataFrame取某行某列的值（索引和列名混用）
                #jiezhenshijian_start = jiezhenkaishishijian.ix[jiezhenshijian_start_index,['jiuzhen_time']].values[0]
                jiezhenshijian_start = jiezhenkaishishijian.iloc[jiezhenshijian_start_index]['jiuzhen_time']
            one_jiuzhenshiduan = []
            #switch_test_item函数返回不同值，对应执行不同的代码片段
            test = dataProcess.switch_test_item(test_para)
            if(test == 0):                
                #预约患者优先就诊策略：先把根据就诊时长从长到短排序的预约患者加入队列，再把现场患者按挂号时间早晚排序加入队列
                #把预约患者先加入就诊list,预约患者就诊时间即从开始接诊时间算起
                for k in range(0,len(one_jiuzhenshiduan_yuyue)):
                    #为元素增加调整后接诊时间的属性
                    one_jiuzhenshiduan_yuyue[k].append(jiezhenshijian_start)
                    #计算调整后的候诊时间，单位是秒
                    yuyue_starttime = 0
                    if(fuwushiduanbiaoji==1):
                        yuyue_starttime=dataProcess.time_to_second(jiezhenshijianduan1[j][0])
                    elif(fuwushiduanbiaoji==2):
                        yuyue_starttime=dataProcess.time_to_second(jiezhenshijianduan2[j][0])
                        
                    one_jiuzhenshiduan_yuyue[k].append(dataProcess.time_to_second(jiezhenshijian_start)-yuyue_starttime)
                    #接诊某患者后，更新现在的最早开始接诊时间                 
                    jiezhenshijian_start = dataProcess.seconds2time(dataProcess.time_to_second(jiezhenshijian_start) + int(one_jiuzhenshiduan_yuyue[k][9])) 
                #把现场患者加入就诊list，若取号时间晚于起始就诊时间，则用取号时间作为起始就诊时间
                for k in range(0,len(one_jiuzhenshiduan_xianchang)):
                    #计算新的接诊开始时间并插入list,如果挂号时间比当前接诊时间晚，则以挂号时间作为当前接诊时间
                    if dataProcess.time_to_second(one_jiuzhenshiduan_xianchang[k][2]) >= dataProcess.time_to_second(jiezhenshijian_start):
                        jiezhenshijian_start = one_jiuzhenshiduan_xianchang[k][2]
                    one_jiuzhenshiduan_xianchang[k].append(jiezhenshijian_start)
                    #计算调整后的候诊时间，单位是秒
                    one_jiuzhenshiduan_xianchang[k].append(dataProcess.time_to_second(one_jiuzhenshiduan_xianchang[k][12])-dataProcess.time_to_second(one_jiuzhenshiduan_xianchang[k][2]))
                    #接诊某患者后，更新现在的最早开始接诊时间                 
                    jiezhenshijian_start = dataProcess.seconds2time(dataProcess.time_to_second(jiezhenshijian_start) + int(one_jiuzhenshiduan_xianchang[k][9]))
                    
                one_jiuzhenshiduan = copy.deepcopy(one_jiuzhenshiduan_yuyue) + copy.deepcopy(one_jiuzhenshiduan_xianchang)
            elif(test == 1):            
                #实验测试：现场挂号患者优先策略，先把现场患者按挂号时间早晚排序加入队列，再把根据就诊时长从长到短排序的预约患者加入队列，
                #把现场患者加入就诊list，若取号时间晚于起始就诊时间，则用取号时间作为起始就诊时间
                for k in range(0,len(one_jiuzhenshiduan_xianchang)):
                    #计算新的接诊开始时间并插入list,如果挂号时间比当前接诊时间晚，则以挂号时间作为当前接诊时间
                    if dataProcess.time_to_second(one_jiuzhenshiduan_xianchang[k][2]) >= dataProcess.time_to_second(jiezhenshijian_start):
                        jiezhenshijian_start = one_jiuzhenshiduan_xianchang[k][2]
                    one_jiuzhenshiduan_xianchang[k].append(jiezhenshijian_start)
                    #计算调整后的候诊时间，单位是秒
                    one_jiuzhenshiduan_xianchang[k].append(dataProcess.time_to_second(one_jiuzhenshiduan_xianchang[k][12])-dataProcess.time_to_second(one_jiuzhenshiduan_xianchang[k][2]))
                    #接诊某患者后，更新现在的最早开始接诊时间                 
                    jiezhenshijian_start = dataProcess.seconds2time(dataProcess.time_to_second(jiezhenshijian_start) + int(one_jiuzhenshiduan_xianchang[k][9]))
                    
                #把预约患者先加入就诊list,预约患者就诊时间即从开始接诊时间算起
                for k in range(0,len(one_jiuzhenshiduan_yuyue)):
                    #为元素增加调整后接诊时间的属性
                    one_jiuzhenshiduan_yuyue[k].append(jiezhenshijian_start)
                    #计算调整后的候诊时间，单位是秒
                    yuyue_starttime = 0
                    if(fuwushiduanbiaoji==1):
                        yuyue_starttime=dataProcess.time_to_second(jiezhenshijianduan1[j][0])
                    elif(fuwushiduanbiaoji==2):
                        yuyue_starttime=dataProcess.time_to_second(jiezhenshijianduan2[j][0])
                        
                    one_jiuzhenshiduan_yuyue[k].append(dataProcess.time_to_second(jiezhenshijian_start)-yuyue_starttime)
                    #接诊某患者后，更新现在的最早开始接诊时间                 
                    jiezhenshijian_start = dataProcess.seconds2time(dataProcess.time_to_second(jiezhenshijian_start) + int(one_jiuzhenshiduan_yuyue[k][9])) 
        
                one_jiuzhenshiduan = copy.deepcopy(one_jiuzhenshiduan_xianchang) + copy.deepcopy(one_jiuzhenshiduan_yuyue) 
            elif(test == 2):  
                #实验测试：先到先就诊策略，假定预约患者在预约时段开始时间全部到达，按照到达的先后顺序依次就诊，服务时段的最后一个患者保持就诊顺序不变。                   
                one_jiuzhenshiduan_temp1 = []
                yuyue_index = 0
                xianchang_index = 0
                yuyue_starttime = 0
                if(fuwushiduanbiaoji==1):
                    yuyue_starttime=dataProcess.time_to_second(jiezhenshijianduan1[j][0])
                elif(fuwushiduanbiaoji==2):
                    yuyue_starttime=dataProcess.time_to_second(jiezhenshijianduan2[j][0])
                while(len(one_jiuzhenshiduan_yuyue)-yuyue_index>0 or len(one_jiuzhenshiduan_xianchang)-xianchang_index>0):    
                    if(len(one_jiuzhenshiduan_yuyue)==0 and len(one_jiuzhenshiduan_xianchang)==0):
                        raise RuntimeError('no data!')
                    elif(yuyue_index!=len(one_jiuzhenshiduan_yuyue) and xianchang_index!=len(one_jiuzhenshiduan_xianchang)):
                        if(yuyue_starttime<dataProcess.time_to_second(one_jiuzhenshiduan_xianchang[xianchang_index][2])):
                            one_jiuzhenshiduan_yuyue[yuyue_index].append(jiezhenshijian_start)
                            one_jiuzhenshiduan_yuyue[yuyue_index].append(dataProcess.time_to_second(jiezhenshijian_start)-yuyue_starttime)
                            one_jiuzhenshiduan_temp1.append(one_jiuzhenshiduan_yuyue[yuyue_index])
                            #接诊某患者后，更新现在的最早开始接诊时间                 
                            jiezhenshijian_start = dataProcess.seconds2time(dataProcess.time_to_second(jiezhenshijian_start) + int(one_jiuzhenshiduan_yuyue[yuyue_index][9])) 
                            yuyue_index = yuyue_index + 1
                        else:
                            #计算新的接诊开始时间并插入list,如果现场挂号时间比当前接诊时间晚，则以挂号时间作为当前接诊时间
                            if dataProcess.time_to_second(one_jiuzhenshiduan_xianchang[xianchang_index][2]) >= dataProcess.time_to_second(jiezhenshijian_start):
                                jiezhenshijian_start = one_jiuzhenshiduan_xianchang[xianchang_index][2]
                            one_jiuzhenshiduan_xianchang[xianchang_index].append(jiezhenshijian_start)
                            #计算调整后的候诊时间，单位是秒
                            one_jiuzhenshiduan_xianchang[xianchang_index].append(dataProcess.time_to_second(one_jiuzhenshiduan_xianchang[xianchang_index][12])-dataProcess.time_to_second(one_jiuzhenshiduan_xianchang[xianchang_index][2]))
                            one_jiuzhenshiduan_temp1.append(one_jiuzhenshiduan_xianchang[xianchang_index])
                            #接诊某患者后，更新现在的最早开始接诊时间                 
                            jiezhenshijian_start = dataProcess.seconds2time(dataProcess.time_to_second(jiezhenshijian_start) + int(one_jiuzhenshiduan_xianchang[xianchang_index][9]))
                            xianchang_index = xianchang_index + 1
                    elif(yuyue_index!=len(one_jiuzhenshiduan_yuyue) and xianchang_index==len(one_jiuzhenshiduan_xianchang)):
                        one_jiuzhenshiduan_yuyue[yuyue_index].append(jiezhenshijian_start)
                        one_jiuzhenshiduan_yuyue[yuyue_index].append(dataProcess.time_to_second(jiezhenshijian_start)-yuyue_starttime)
                        one_jiuzhenshiduan_temp1.append(one_jiuzhenshiduan_yuyue[yuyue_index])
                        #接诊某患者后，更新现在的最早开始接诊时间                 
                        jiezhenshijian_start = dataProcess.seconds2time(dataProcess.time_to_second(jiezhenshijian_start) + int(one_jiuzhenshiduan_yuyue[yuyue_index][9])) 
                        yuyue_index = yuyue_index + 1
                    elif(yuyue_index==len(one_jiuzhenshiduan_yuyue) and xianchang_index!=len(one_jiuzhenshiduan_xianchang)):
                        if dataProcess.time_to_second(one_jiuzhenshiduan_xianchang[xianchang_index][2]) >= dataProcess.time_to_second(jiezhenshijian_start):
                            jiezhenshijian_start = one_jiuzhenshiduan_xianchang[xianchang_index][2]
                        one_jiuzhenshiduan_xianchang[xianchang_index].append(jiezhenshijian_start)
                        #计算调整后的候诊时间，单位是秒
                        one_jiuzhenshiduan_xianchang[xianchang_index].append(dataProcess.time_to_second(one_jiuzhenshiduan_xianchang[xianchang_index][12])-dataProcess.time_to_second(one_jiuzhenshiduan_xianchang[xianchang_index][2]))
                        one_jiuzhenshiduan_temp1.append(one_jiuzhenshiduan_xianchang[xianchang_index])
                        #接诊某患者后，更新现在的最早开始接诊时间                 
                        jiezhenshijian_start = dataProcess.seconds2time(dataProcess.time_to_second(jiezhenshijian_start) + int(one_jiuzhenshiduan_xianchang[xianchang_index][9]))
                        xianchang_index = xianchang_index + 1
                one_jiuzhenshiduan = copy.deepcopy(one_jiuzhenshiduan_temp1)
                
            #list只剩下最后一组，没法在下次循环判断是否需要在上个服务周期中添加最后就诊患者，因而需要把最后就诊患者加入，把最后就诊患者加入就诊队列
            if(j==len(jiezhenxianchanghuanzhe[i])-1 and last_flag==1):
                last_patient_temp = copy.deepcopy(last_patient[0])
                last_patient_temp.append(jiezhenshijian_start)
                last_patient_temp.append(dataProcess.time_to_second(last_patient_temp[4])-dataProcess.time_to_second(jiezhenshijian_start))
                one_jiuzhenshiduan.append(last_patient_temp)
                last_flag = 0
            jiezhenxianchanghuanzhe[i][j] = copy.deepcopy(one_jiuzhenshiduan)
            
    return jiezhenxianchanghuanzhe
                    
def houzhenshichangAvg(jiezhenxianchanghuanzhe):
    each_zhuanjia_yuyue = []
    each_zhuanjia_xianchang = []
    for e in jiezhenxianchanghuanzhe:
        date_temp = ""
        #houzhenshichang_sum = 0
        xianchang_houzhenshichang_before_sum = 0
        xianchang_houzhenshichang_after_sum = 0
        xianchang_count = 0
        yuyue_houzhenshichang_before_sum = 0
        yuyue_houzhenshichang_after_sum = 0
        yuyue_count = 0
        zhuanjia = ""
        keshi = ""
        haoyuanming=""
        for i in range(0,len(e)):
            if len(date_temp) == 0:
                date_temp = e[i][0][1]
                zhuanjia = e[i][0][6]
                keshi = e[i][0][5]
                haoyuanming = e[i][0][11]
            for j in range(0,len(e[i])):
                if e[i][j][7] == "on-site":
                    xianchang_count = xianchang_count + 1
                    #houzhenshichang_sum = houzhenshichang_sum + e[i][j][13]
                    xianchang_houzhenshichang_before_sum = xianchang_houzhenshichang_before_sum + int(e[i][j][8])
                    xianchang_houzhenshichang_after_sum = xianchang_houzhenshichang_after_sum + e[i][j][13]
                elif e[i][j][7] == "appointment":
                    yuyue_count = yuyue_count + 1
                    yuyue_houzhenshichang_before_sum = yuyue_houzhenshichang_before_sum + int(e[i][j][8])
                    yuyue_houzhenshichang_after_sum = yuyue_houzhenshichang_after_sum + e[i][j][13]
        each_zhuanjia_xianchang.append([keshi,zhuanjia,xianchang_count,xianchang_houzhenshichang_before_sum,xianchang_houzhenshichang_after_sum,haoyuanming])
        each_zhuanjia_yuyue.append([keshi,zhuanjia,yuyue_count,yuyue_houzhenshichang_before_sum,yuyue_houzhenshichang_after_sum,haoyuanming])

    for i in range(0,len(each_zhuanjia_xianchang)):
        pingjunhouzhenshichang_before = each_zhuanjia_xianchang[i][3]/each_zhuanjia_xianchang[i][2]
        pingjunhouzhenshichang_after = each_zhuanjia_xianchang[i][4]/each_zhuanjia_xianchang[i][2]
        pingjunhouzhenshichang = pingjunhouzhenshichang_before-pingjunhouzhenshichang_after
        print("average waiting time of walk-ins before optimization:%d" % pingjunhouzhenshichang_before)
        print("average waiting time of walk-ins after optimization:%d" % pingjunhouzhenshichang_after)
        print("average shortened waiting time of walk-ins:%d" % pingjunhouzhenshichang)
    for i in range(0,len(each_zhuanjia_yuyue)):
        pingjunhouzhenshichang_before = each_zhuanjia_yuyue[i][3]/each_zhuanjia_yuyue[i][2]
        pingjunhouzhenshichang_after = each_zhuanjia_yuyue[i][4]/each_zhuanjia_yuyue[i][2]
        pingjunhouzhenshichang = pingjunhouzhenshichang_before-pingjunhouzhenshichang_after
        print("average waiting time of scheduled outpatients before optimization:%d" % pingjunhouzhenshichang_before)
        print("average waiting time of scheduled outpatients after optimization:%d" % pingjunhouzhenshichang_after)
        print("average shortened waiting time of scheduled outpatients:%d" % pingjunhouzhenshichang)
        
        pingjunhouzhenshichang_all_before = (each_zhuanjia_yuyue[i][3]+each_zhuanjia_xianchang[i][3])/(each_zhuanjia_yuyue[i][2]+each_zhuanjia_xianchang[i][2])
        pingjunhouzhenshichang_all_after = (each_zhuanjia_yuyue[i][4]+each_zhuanjia_xianchang[i][4])/(each_zhuanjia_yuyue[i][2]+each_zhuanjia_xianchang[i][2])
        pingjunhouzhenshichang_all = pingjunhouzhenshichang_all_before-pingjunhouzhenshichang_all_after
        print("average waiting time of all patients before optimization:%d" % pingjunhouzhenshichang_all_before)
        print("average waiting time of all patients after optimization:%d" % pingjunhouzhenshichang_all_after)
        print("average shortened waiting time ofall patients:%d" % pingjunhouzhenshichang_all)
        
        
def main():
    file1 = "patients_jiezhen_time_sorted.txt"
    jiezhenshuliang1 = [3,15,16]#设置时间段“8:00—9:00”、“9:00—10:00”、“10:00—11:00”的号源数
    jiezhenshuliang2 = [2,9]
    gusuanxianchangrenshu1 = [7,13,10,2]#设置时间段“7:00—8:00”、“8:00—9:00”、“9:00—10:00”、“10:00—11:00”的现场患者达到人数
    gusuanxianchangrenshu2 = [0,0,0]
    gusuanxianchangrenshu1_temp = gusuanxianchangrenshu1[1:4]
    gusuanxianchangrenshu1_temp[0] = gusuanxianchangrenshu1_temp[0] + gusuanxianchangrenshu1[0] #前两个时段到达的人都在第一个就诊时段就诊，故把前两个时段到达的现场患者数合并
    gusuanxianchangrenshu2_temp = gusuanxianchangrenshu2[1:3]
    gusuanxianchangrenshu2_temp[0] = gusuanxianchangrenshu2_temp[0] + gusuanxianchangrenshu2[0] 
    gusuanyuyuerenshu1=[]
    gusuanyuyuerenshu2=[]
    #以下循环计算各分时时段内应分配的现场号源和预约号源数量
    for i in range(0,len(jiezhenshuliang1)):
        if(jiezhenshuliang1[i]<gusuanxianchangrenshu1_temp[i]):
            if(i<len(jiezhenshuliang1)-1):
                gusuanxianchangrenshu1_temp[i+1] = gusuanxianchangrenshu1_temp[i+1] + gusuanxianchangrenshu1_temp[i] - jiezhenshuliang1[i]
            gusuanyuyuerenshu1.append(0)
            gusuanxianchangrenshu1_temp[i] = jiezhenshuliang1[i]
        elif(jiezhenshuliang1[i]>=gusuanxianchangrenshu1_temp[i]):
            gusuanyuyuerenshu1.append(jiezhenshuliang1[i]-gusuanxianchangrenshu1_temp[i])
            
    for i in range(0,len(jiezhenshuliang2)):
        if(jiezhenshuliang2[i]<gusuanxianchangrenshu2_temp[i]):
            if(i<len(jiezhenshuliang2)-1):
                gusuanxianchangrenshu2_temp[i+1] = gusuanxianchangrenshu2_temp[i+1] + gusuanxianchangrenshu2_temp[i] - jiezhenshuliang2[i]
            gusuanyuyuerenshu2.append(0)
            gusuanxianchangrenshu2_temp[i] = jiezhenshuliang2[i]
        elif(jiezhenshuliang2[i]>=gusuanxianchangrenshu2_temp[i]):
            gusuanyuyuerenshu2.append(jiezhenshuliang2[i]-gusuanxianchangrenshu2_temp[i])
            
        

    jiezhenxianchanghuanzhe,yuyues,jiezhenkaishishijian,last_patients = resortedHouzhen(file1,gusuanxianchangrenshu1_temp,gusuanxianchangrenshu2_temp)
    #jiezhenxianchanghuanzhe字段包括一卡通号，挂号日期，挂号时间，接诊日期，接诊时间，科室，专家，类型，候诊时长，就诊时长，服务周期，号源名，调整后的接诊时间，调整后节约的候诊时长
    
    jiezhenxianchanghuanzhe = houzhenshijianRecompute(jiezhenxianchanghuanzhe,yuyues,jiezhenshuliang1,jiezhenshuliang2,jiezhenkaishishijian,last_patients)
    houzhenshichangAvg(jiezhenxianchanghuanzhe)
    
    
    
    
#    houzhenshijian1 = houzhenshichangAVG(file1)
#    houzhenshijian2 = houzhenshichangAVG(file2)
#    if len(houzhenshijian1)==len(houzhenshijian2):
#        for i in range(0,len(houzhenshijian1)):
#            print("调整前现场患者平均候诊时间：")
#            houzhenshijian1[i].append(dataProcess.seconds2time(houzhenshijian1[i][2]))
#            print(houzhenshijian1[i])
#            print("调整后现场患者平均候诊时间：")
#            houzhenshijian2[i].append(dataProcess.seconds2time(houzhenshijian2[i][2]))
#            print(houzhenshijian2[i])
#    else:
#        print("woca!!")


    
    
if __name__=="__main__":
    main()