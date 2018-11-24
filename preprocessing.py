#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by lljzhiwang on 2018/11/23
import os,json,time
import util_common as util
datapath='./data/data_raw'
alllog_b09=datapath+r'/log_b_09.txt'
alllog_b18=datapath+r'/log_b_18.txt'
alllog_d09=datapath+r'/log_d_09.json'
alllog_d18=datapath+r'/log_d_18.json'
user_typeinter_18 = datapath+r'/userdb_intersec_18.txt'
user_typeinter_09 = datapath+r'/userdb_intersec_09.txt'
user_timeinter_b = datapath+r'/userb_intersec_0918.txt'
user_timeinter_d = datapath+r'/userd_intersec_0918.txt'

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
    print("getting child dic...")
    for u in keys:
        cnt += 1
        if cnt % (len(keys)/10) == 0:
            print(cnt)
        res[u] = dicin[u]
    return res

def get_intersec_log_child():

    ul=util.load2list(datapath+r'/userdb_intersec_09.txt')
    ulogb=util.load2dic(datapath+r'/log_b_09.txt',interval=500000)
    interlog = getchilddic(ulogb,ul)
    util.savejson(datapath+r'/ufn_b_typeinter_09.json',interlog)

    del ulogb
    del interlog

    ulogd = util.loadjson(datapath+r'/log_d_09.json')
    interlog = getchilddic(ulogd, ul)
    util.savejson(datapath + r'/ufn_d_typeinter_09.json', interlog)

def getdifference(logb,logd):
    print("getting diff of two dicts...")
    logdb={}
    cnt=0
    alllen=len(logb.keys())
    for i in logb.keys():
        cnt+=1
        if cnt%(alllen/10)==0:
            print cnt
        diff = list(set(logb[i]).difference(set(logd[i])))
        if diff:
            logdb[i]=diff
    print("length of diff file %d " %len(logdb))
    #util.savejson(datapath+'/ufn_typeinter_09_bddiff.json',logdb)
    return logdb

def get_intersec_log(user_interseclist, alllog_b, alllog_d,prefix):
    print("loading data...")
    uinterl=util.load2list(user_interseclist)
    blog=util.load2dic(alllog_b, '\t', interval=5000000)
    dlog=util.loadjson(alllog_d)
    userb=blog.keys()
    userd=dlog.keys()
    uintertype18=list(set(userb).intersection(set(userd)))
    if len(uintertype18)==len(uinterl):
        print("file %s is correct!" % user_interseclist)
        del uintertype18
    else:
        print("file %s is wrong!!!" % user_interseclist)
        return
    interseced_d = getchilddic(dlog,uinterl)
    del dlog
    interseced_b = getchilddic(blog,uinterl)
    del blog
    interseced_dbdiff = getdifference(interseced_b,interseced_d)
    util.savejson("%s/%s_d.json" %(datapath,prefix),interseced_d)
    util.savejson("%s/%s_b.json" %(datapath,prefix), interseced_b)
    util.savejson("%s/%s_dbdiff.json" %(datapath,prefix), interseced_dbdiff)


if __name__ == '__main__':
    # get_intersec_childlog()
    #a=util.loadjson(alllog_d18)
    get_intersec_log(user_typeinter_18,alllog_b18,alllog_d18,"ulog_typeinter18")