#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import datetime
import time

#input:String,"日期 时分秒"
#output:[String,String],[日期,时分秒]
def datetime_get(s):
    if s.strip()!="":
        s_temp = s.split(" ")
        s_final = []
        s_final.append(s_temp[0])
        s_final.append(s_temp[1])
        return s_final
    else:
        return None

#把时分秒字符串转为秒
#input:String
#output:Int
def time_to_second(t):
    t_temp = t.split(":")
    second = int(t_temp[2])
    minute = int(t_temp[1])
    hour = int(t_temp[0])
    s = hour * 3600 + minute * 60 + second
    return s
#把秒转化为时分秒
#Input:Int
#output:String
def timeFormat(t):
    second = str(t%60)
    minute = str((int(t/60))%60)
    hour = str(int(t/3600))
    
    if len(minute) == 1:
        minute = "0" + minute
    if len(second) == 1:
        second = "0" + second
    if len(hour) == 1:
        hour = "0" + hour
    time = hour+":"+minute+":"+second
    return time
#把秒转化为时分秒
def seconds2time(sec):
    m,s = divmod(sec,60)
    h,m = divmod(m,60)
    return "%02d:%02d:%02d" % (h,m,s)
#把日期转化为等长字符串
#input:String，例如2018-11-7
#output:String，例如2018-11-07
def dateFormat(d):
    date = d.split("-")
    year = date[0]
    month = date[1]
    day = date[2]
    if len(month)==1:
        month = "0" + month
    if len(day)==1:
        day = "0" + day
    d = year + "-" + month + "-" + day
    return d

#数据中时间格式时分秒，由于时小于10时只有一位数字，造成时间长度不等（9：01：01是7位，10：01：01是8位）
#input:String,例如2018-11-7 7:19:35
#output：String,例如2018-11-07 07:19:35
def datetimeFormation(s):
    s = s.strip()
    if len(s)!=0:
        row_temps = s.split(" ")
        if len(row_temps[0]) != 10:
            row_temps[0] = dateFormat(row_temps[0])
        if len(row_temps[1]) == 7:
            row_temps[1] = "0" + row_temps[1]
        s = row_temps[0] + " " +  row_temps[1]
        return s
    else:
        return ""
    
#设置单位间隔时间t（分钟），对挂号时间段进行分割，用于数据分布估计
#该时间段既可用于挂号，也可用于接诊，因为医生可能会提前上班
#用于接诊时，返回结果需自行添加一个时段，用于下午下班后加班，暂不设定结束时间，默认为0
def init_shijianduan(t):
    t = t * 60 #输入t为分钟的整型，转为秒的整型
    #早上7点开始放号
    time_start1 =  time_to_second("07:00:00")
    time_end1 =  time_to_second("12:00:00")
    time_start2 =  time_to_second("14:30:00")
    time_end2 =  time_to_second("17:30:00")
    guahaorenshu_count_oneday = []
    while(time_start1 < time_end1):
        guahaorenshu_count_oneday.append([timeFormat(time_start1), timeFormat(time_start1+t), 0])
        time_start1 = time_start1 + t
    #中午休息时段的时间整体看作一个时间段
    guahaorenshu_count_oneday.append([timeFormat(time_start1), timeFormat(time_start2), 0])    
    while(time_start2 < time_end2):
        guahaorenshu_count_oneday.append([timeFormat(time_start2), timeFormat(time_start2+t), 0])
        time_start2 = time_start2 + t
    return guahaorenshu_count_oneday

def init_jiuzhenshijianduan(t):
    t = t * 60 #输入t为分钟的整型，转为秒的整型
    #早上7点开始放号
    time_start1 =  time_to_second("07:00:00")
    time_end1 =  time_to_second("12:00:00")
    time_start2 =  time_to_second("14:30:00")
    time_end2 =  time_to_second("17:30:00")
    guahaorenshu_count_oneday = []
    while(time_start1 < time_end1):
        guahaorenshu_count_oneday.append([timeFormat(time_start1), timeFormat(time_start1+t), 0])
        time_start1 = time_start1 + t
    #中午加班后延一个小时，下午上班提前一个小时  
    guahaorenshu_count_oneday.append([timeFormat(time_start1), timeFormat(time_start1+3600), 0]) 
    guahaorenshu_count_oneday.append([timeFormat(time_start2-3600), timeFormat(time_start2), 0]) 
    while(time_start2 < time_end2):
        guahaorenshu_count_oneday.append([timeFormat(time_start2), timeFormat(time_start2+t), 0])
        time_start2 = time_start2 + t
    return guahaorenshu_count_oneday

#计算两日期时间的间距(单位：秒)
#input：字符串类型，日期为“2019-04-15”格式，时间为“08:08:15”格式
#output：两个时间之间的长度
def timeLength(start_date,start_time,end_date,end_time):
    start1 = start_date.split("-")
    start2 = start_time.split(":")
    end1 = end_date.split("-")
    end2 = end_time.split(":")
    start3 = datetime.datetime(int(start1[0]),int(start1[1]),int(start1[2]),int(start2[0]),int(start2[1]),int(start2[2]))
    end3 = datetime.datetime(int(end1[0]),int(end1[1]),int(end1[2]),int(end2[0]),int(end2[1]),int(end2[2]))
    td = end3-start3 #格式为“10 days，5:16:48”
    return td

def timeLength_bysecond(start_date,start_time,end_date,end_time):
    td = timeLength(start_date,start_time,end_date,end_time)
    return td.days * 24 * 3600 + td.seconds  #将其转化成秒

def timeLength_byday(start_date,start_time,end_date,end_time):
    td = timeLength(start_date,start_time,end_date,end_time)
    if td.seconds > 0:
        return td.days + 1
    else:
        return td.days
    
#求给定日期增加或减少指定天数的日期
#input:给定日期和天数（可正可负），日期是字符串，天数是int
#output:最终日期，字符串类型
def date_compute(date,days):
    t = time.strptime(date, "%Y-%m-%d")
    y, m, d = t[0:3]
    Date = str(datetime.datetime(y, m, d) + datetime.timedelta(days)).split()
    return Date[0]


#实验时，可能需要用不同方法实现某些步骤进行比对，定义此函数，调用时，non-test对应非测试代码片段，testXX对应第一种不同的测试方法代码片段
def switch_test_item(item):
    switcher = {
        "non-test": 0,
        "test1":1,
        "test2":2,
        "test3":3,
        "test4":4,
    }
    return switcher.get(item,"nothing")