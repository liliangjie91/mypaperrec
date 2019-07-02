#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by lljzhiwang on 2019/6/27 
from __future__ import division
import util_common as uc
import numpy as np
import pandas as pd
from sklearn import preprocessing
from sklearn.model_selection import train_test_split,cross_validate,GridSearchCV
from sklearn.neighbors import NearestNeighbors

def data2csv():
    fnfeatpath = './data/highq_5w/fn18_5w_features.txt'
    fnfeas = uc.load2list(fnfeatpath)
    fns, cites, cites_w, authcodes, fundcodes, jigoucodes, productcodes, dates, pages, downs, citeds, ifs = [], [], [], [], [], [], [], [], [], [], [], []
    for i in fnfeas:
        if type(i) is str:
            iss = i.split()
            if len(iss) == 14:
                fns.append(iss[0])
                cites.append(iss[1])
                cites_w.append(iss[2])
                authcodes.append(iss[3])
                fundcodes.append(iss[4])
                jigoucodes.append(iss[5])
                productcodes.append(iss[6])
                dates.append(iss[7])
                pages.append(iss[8])
                downs.append(iss[9])
                citeds.append(iss[10])
                ifs.append(iss[11])
    exs = pd.DataFrame({'fns': fns, 'cites': cites, 'cites_w': cites_w, 'authcodes': authcodes, 'fundcodes': fundcodes,
                        'jigoucodes': jigoucodes, 'productcodes': productcodes, 'dates': dates, 'pages': pages,
                        'downs': downs, 'citeds': citeds, 'ifs': ifs})
    exs.to_csv('./data/highq_5w/fn18_5w_features.csv')

def change_data_format(data):
    # 以下预处理都是基于dataframe格式进行的
    data_new = pd.DataFrame(data)
    return data_new

def nan2bivalue(dataf, columename, coverold=False):
    #对于部分有nan值太多的列，可以把是否有值作为特征
    data=pd.read_csv(dataf) if isinstance(dataf, str) else dataf
    data = data.replace('null', np.NAN)
    funds=data[columename]
    fundcode_bi = []
    for i in funds:
        if i is np.NAN:
            fundcode_bi.append(0)
        else:
            fundcode_bi.append(1)
    data['%s_bi' %columename]=fundcode_bi
    if coverold and isinstance(dataf,str): #覆盖原文件
        data.to_csv(dataf)
    return data


def nan_remove(dataf,nan_rate=0.5):
    #对于部分nan值过多的列，可以选择剔除
    data = pd.read_csv(dataf) if isinstance(dataf, str) else dataf
    all_cnt=data.shape[0] #总行数
    good_colum=[]
    for i in range(data.shape[1]):
        tmprate=np.isnan(np.array(data.iloc[:,i])).sum()/all_cnt
        if tmprate<nan_rate:
            good_colum.append(i)
    good_data=data.iloc[:,good_colum]
    return good_data



if __name__ == '__main__':
    pass