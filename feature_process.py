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

if __name__ == '__main__':
    pass