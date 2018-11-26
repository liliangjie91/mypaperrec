#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by lljzhiwang on 2018/11/23
import os,json,time,sys
import util_common as util
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s')
logging.root.setLevel(level=logging.INFO)
logger.info("running %s" % ' '.join(sys.argv))

datapath='./data/data_raw'
goodpath='./data/good'
alllog_b09=datapath+r'/log_b_09.txt'
alllog_b18=datapath+r'/log_b_18.txt'
alllog_d09=datapath+r'/log_d_09.json'
alllog_d18=datapath+r'/log_d_18.json'
user_typeinter_18 = datapath+r'/userdb_intersec_18.txt'
user_typeinter_09 = datapath+r'/userdb_intersec_09.txt'
user_timeinter_b = datapath+r'/userb_intersec_0918.txt'
user_timeinter_d = datapath+r'/userd_intersec_0918.txt'
ulog_typeinter09_d = datapath + r'/ulog_typeinter09_d.json'
ulog_typeinter09_b = datapath + r'/ulog_typeinter09_b.json'
ulog_typeinter09_dbdiff = datapath + r'/ulog_typeinter09_dbdiff.json'
ulog_typeinter18_d = datapath + r'/ulog_typeinter18_d.json'
ulog_typeinter18_b = datapath + r'/ulog_typeinter18_b.json'
ulog_typeinter18_dbdiff = datapath + r'/ulog_typeinter18_dbdiff.json'


def get_sub_dic(dicin, keys):
    '''
    获取子字典，根据keys中的key值
    :param dicin: 
    :type dicin: dict
    :param keys: 
    :type keys: list
    :return: 
    :rtype: dict
    '''
    logger.info("getting sub dicts from input keys...")
    res = {}
    for u in keys:
        res[u] = dicin[u]
    return res

def get_dic_diff(logb, logd):
    logger.info("getting two dicts` difference...")
    logdb={}
    for i in logb.keys():
        diff = list(set(logb[i]).difference(set(logd[i])))
        if diff:
            logdb[i]=diff
    logger.info("length of diff file %d " %len(logdb))
    #util.savejson(datapath+'/ufn_typeinter_09_bddiff.json',logdb)
    return logdb

def get_intersec_log(user_interseclist, alllog_b, alllog_d,prefix):
    uinterl=util.load2list(user_interseclist)
    blog=util.load2dic(alllog_b, '\t')
    dlog=util.loadjson(alllog_d)
    userb=blog.keys()
    userd=dlog.keys()
    logger.info("caculating two logs` intersection user...")
    uintertype18=list(set(userb).intersection(set(userd)))
    if len(uintertype18)==len(uinterl):
        print("file %s is correct!" % user_interseclist)
        del uintertype18
    else:
        print("file %s is wrong!!!" % user_interseclist)
        return
    interseced_d = get_sub_dic(dlog, uinterl)
    interseced_b = get_sub_dic(blog, uinterl)
    del dlog
    del blog
    interseced_dbdiff = get_dic_diff(interseced_b, interseced_d)
    logger.info("saving ress...")
    util.savejson("%s/%s_d.json" %(datapath,prefix),interseced_d)
    util.savejson("%s/%s_b.json" %(datapath,prefix), interseced_b)
    util.savejson("%s/%s_dbdiff.json" %(datapath,prefix), interseced_dbdiff)
    logger.info("done!")

def del_once_action():
    #删除只有一次操作的用户？
    pass

def get_highquality_ulog(inpath,outpath,actmin=2,actmax=300):
    #优质用户历史，操作数>2 <300(操作太多可能是爬虫)
    oldulog = util.load2list(inpath)
    newulog = []
    for l in oldulog:
        ws=l.strip().split()[1:] #每一行第一个是id
        if actmax>len(ws)>actmin:
            newulog.append(l)
    util.list2txt(newulog,outpath)

def get_userlist(path,logpath=None):
    #获取用户id列表，返回list
    if os.path.exists(path):
        return util.load2list(path)
    else:
        ul = util.load2list(logpath,get1column=0)
        util.list2txt(ul,path)
        return ul

def get_fnlist(path,logpath):
    #获取文件名列表，返回list
    if os.path.exists(path):
        return util.load2list(path)
    else:
        ul = util.load2list(logpath,to1column=True,start=1)
        res=list(set(ul))
        util.list2txt(res,path)
        return res

def gen_samples(ulog_d, ulog_diff, prefix):
    logger.info("generate posi & neg samples for myrec...")
    dlog=util.loadjson(ulog_d)
    difflog = util.loadjson(ulog_diff)
    posisam=[]
    negsam=[]
    logger.info("gen posi samples...")
    for k in dlog.keys():
        fns=dlog[k]
        if fns:
            for fn in fns:
                posisam.append("%s+%s\t%d"%(k,fn,1))
    print(len(posisam))
    util.list2txt(posisam,'./data/good/'+prefix+'_posi.txt')
    del dlog
    del posisam
    logger.info("gen neg samples...")
    for k in difflog.keys():
        fns=difflog[k]
        if fns:
            for fn in fns:
                negsam.append("%s+%s\t%d"%(k,fn,0))
    print(len(negsam))
    util.list2txt(negsam, './data/good/' + prefix + '_neg.txt')





if __name__ == '__main__':
    # get_intersec_childlog()
    # get_intersec_log(user_typeinter_09,alllog_b09,alllog_d09,"ulog_typeinter09")
    # gen_samples(ulog_typeinter18_d,ulog_typeinter18_dbdiff,"samples_18")
    # gen_samples(ulog_typeinter09_d,ulog_typeinter09_dbdiff,"samples_09")
    get_highquality_ulog(goodpath+'/log18_posi.txt', goodpath+'/highq/log18_highq_posi.txt')