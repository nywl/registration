import pandas as pd
import numpy as np

#导入作图用的包
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['FangSong'] # 指定默认字体
matplotlib.rcParams['axes.unicode_minus'] = False # 解决保存图像是负号'-'显示为方块的问题

class GrayForecast():
    #实现能处理三种类型：一维列表、DataFrame、Series。如果处理DataFrame可能会出现不止一维的情况，
    #于是设定一个参数datacolumn，用于处理传入DataFrame不止一列数据到底用哪个的问题
    def __init__(self, data, datacolumn=None):
    
        if isinstance(data, pd.core.frame.DataFrame):
            self.data=data
            try:
                self.data.columns = ['数据']
            except:
                if not datacolumn:
                    raise Exception('您传入的dataframe不止一列')
                else:
                    self.data = pd.DataFrame(data[datacolumn])
                    self.data.columns=['数据']
        elif isinstance(data, pd.core.series.Series):
            self.data = pd.DataFrame(data, columns=['数据'])
        else:
            self.data = pd.DataFrame(data, columns=['数据'])
    
        self.forecast_list = self.data.copy()
    
        if datacolumn:
            self.datacolumn = datacolumn
        else:
            self.datacolumn = None
        #save arg:
        #        data                DataFrame    数据
        #        forecast_list       DataFrame    预测序列
        #        datacolumn          string       数据的含义
    
    #按照级比校验的步骤进行，最终返回是否成功的bool类型值
    def level_check(self):
        # 数据级比校验
        n = len(self.data)
        lambda_k = np.zeros(n-1)
        for i in range(n-1):
            lambda_k[i] = self.data.ix[i]["数据"]/self.data.ix[i+1]["数据"]
            if lambda_k[i] < np.exp(-2/(n+1)) or lambda_k[i] > np.exp(2/(n+2)):
                flag = False
        else:
            flag = True
    
        self.lambda_k = lambda_k
    
        if not flag:
            print("级比校验失败，请对X(0)做平移变换")
            return False
        else:
            print("级比校验成功，请继续")
            return True
    
    #save arg:
    #        lambda_k            1-d list
            
    #按照GM(1,1)的步骤进行一次预测并增长预测序列（forecast_list）
    #传入的参数forecast为使用forecast_list末尾数据的数量，因为灰色预测为短期预测，过多的数据反而会导致数据精准度变差
    def GM_11_build_model(self, forecast=4):
        print(self.data)
        if forecast > len(self.data):
            raise Exception('您的数据行不够')
        X_0 = np.array(self.forecast_list['数据'].tail(forecast))
    #       1-AGO
        X_1 = np.zeros(X_0.shape)
        for i in range(X_0.shape[0]):
            X_1[i] = np.sum(X_0[0:i+1])
    #       紧邻均值生成序列
        Z_1 = np.zeros(X_1.shape[0]-1)
        for i in range(1, X_1.shape[0]):
            Z_1[i-1] = -0.5*(X_1[i]+X_1[i-1])
    
        B = np.append(np.array(np.mat(Z_1).T), np.ones(Z_1.shape).reshape((Z_1.shape[0], 1)), axis=1)
        Yn = X_0[1:].reshape((X_0[1:].shape[0], 1))
    
        B = np.mat(B)
        Yn = np.mat(Yn)
        a_ = (B.T*B)**-1 * B.T * Yn
    
        a, b = np.array(a_.T)[0]
    
        X_ = np.zeros(X_0.shape[0])
        def f(k):
            return (X_0[0]-b/a)*(1-np.exp(a))*np.exp(-a*(k))
    
        self.forecast_list.loc[len(self.forecast_list)] = f(X_.shape[0])
        
    #预测函数只要调用GM_11_build_model就可以，传入的参数time为向后预测的次数，forecast_data_len为每次预测所用末尾数据的条目数
    def forecast(self, time=5, forecast_data_len=5):
        for i in range(time):
            self.GM_11_build_model(forecast=forecast_data_len)
            
    #打印当前预测序列
    def log(self):
        res = self.forecast_list.copy()
        if self.datacolumn:
            res.columns = [self.datacolumn]
        return res
    
    #初始化序列
    def reset(self):
        self.forecast_list = self.data.copy()
        
    #作图
    def plot(self):
        self.forecast_list.plot()
        if self.datacolumn:
            plt.ylabel(self.datacolumn)
            plt.legend([self.datacolumn])

def main():
    f = open("用于预测的患者达到人数.txt", encoding="utf8")
    df = pd.read_csv(f,sep=',')
    #df.tail()
    df1 = df.iloc[0:12].reset_index() #每次取要用于预测的数据子集，在预测时，直接指定forecast_data_len为子集长度，即用整个子集进行预测
    #构建灰色预测对象，进行10年预测输出结果并作图
    gf = GrayForecast(df1, '10~11')
    print(gf.forecast(time=1,forecast_data_len=len(df1)))#定义预测模型
    print(gf.log())#打印当前预测序列
    print(gf.plot())
    
if __name__=="__main__":
    main()