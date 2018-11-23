#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by lljzhiwang on 2018/11/23
import os,json,time
import util_common as util
datapath='./data/data_raw'

def getchilddic(dicin,keys):
    '''
    
    :param dicin: 
    :type dicin: dict
    :param keys: 
    :type keys: list
    :return: 
    :rtype: dict
    '''
    res = {}
    cnt = 0
    for u in keys:
        cnt += 1
        if cnt % 10000 == 0:
            print(cnt)
        res[u] = dicin[u]
    return res

def get_intersec_childlog():

    ul=util.load2list(datapath+r'/userdb_intersec_09.txt')
    ulogb=util.load2dic(datapath+r'/log_b_09.txt',interval=500000)
    interlog = getchilddic(ulogb,ul)
    util.savejson(datapath+r'/ufn_b_typeinter_09.json',interlog)

    del ulogb
    del interlog

    ulogd = util.loadjson(datapath+r'/log_d_09.json')
    interlog = getchilddic(ulogd, ul)
    util.savejson(datapath + r'/ufn_d_typeinter_09.json', interlog)

def getdifference():
    

if __name__ == '__main__':
    get_intersec_childlog()