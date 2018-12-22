#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by lljzhiwang on 2018/12/20
from sklearn.cluster import KMeans, MiniBatchKMeans
from sklearn import metrics
import time,os,re
# import kbase
import numpy as np
import util_common as util
import util_path as path
import ml_prepare as mlpre
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%d %b %y %H:%M:%S',
                    filename='./logs/all.log',
                    filemode='a')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler("./logs/cluster.log")
ch = logging.StreamHandler()
formatter=logging.Formatter('%(asctime)s%(name)s%(levelname)s%(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)

def vec_cluster(vecs,respath,true_k=20):
    # 对vecs数据做聚类kmeans，返回聚类结果和ch评分
    minibatch=0 if len(vecs)<10000 else 1
    if minibatch:
        print("doing minibatchkmeans...")
        km = MiniBatchKMeans(n_clusters=true_k, init='k-means++', n_init=1,
                             init_size=1000, batch_size=1000, verbose=False)
    else:
        print("doing basic kmeans...")
        km = KMeans(n_clusters=true_k, init='k-means++', max_iter=300, n_init=1,
                    verbose=False)
    print("-------Clustering begin...")
    t1 = time.time()
    cresraw=km.fit_predict(vecs)
    np.savetxt(respath+'.np',cresraw)
    result = list(cresraw)
    print("-------Clustering train cost %s s" % (time.time() - t1))
    kmscore = metrics.calinski_harabaz_score(vecs, result)
    util.list2txt(result,respath)
    return kmscore, result

def get_cluter_center(cres,vecs,words,respath):
    # 获取聚类结果的类中心(其实是离类中心最近的那个样本)
    assert len(cres) == len(vecs)
    dic_cluser = {} #{类号：[样本id,...]}
    dic_vecs={} #{类号：[[样本vec],[...]]}
    dic_words={} #{类号：[[样本词],[...]]}
    dic_center={} #{类号：中心词}
    dic_res={} #{词：中心词}
    dic_res2={} #{中心词：[词1，词2，...]} 与dic_res相对应
    res_ccenter_fns = []  # 输出list，即每个类的类中心文件
    logger.info("getting dict of cluster_number and userlist...")
    for i,v in enumerate(cres):  # 对所有的样本，转字典：{类号：[样本id]}
        if not dic_cluser.has_key(v):
            dic_cluser[v] = [i]
            dic_vecs[v] = [vecs[i]]
            dic_words[v] = [words[i]]
        else:
            tmpli = dic_cluser[v]
            tmpli.append(i)
            dic_cluser[v] = tmpli
            tmplv = dic_vecs[v]
            tmplv.append(vecs[i])
            dic_vecs[v] = tmplv
            tmplw = dic_words[v]
            tmplw.append(words[i])
            dic_words[v] = tmplw
    logger.info("getting min dist id...")
    for j in dic_cluser.keys():  # 对所有类号，计算类中心和类中心最近id
        # logger.info("cluster num: %d" %j)
        cluster_index_list = dic_cluser[j]
        cluster_vec_mat_percenter = dic_vecs[j]
        tmpmat=np.array(cluster_vec_mat_percenter)
        centervec=np.mean(tmpmat,axis=0)
        dists=np.linalg.norm(tmpmat-centervec,axis=1)
        minindex=np.argmin(dists)
        minword=words[cluster_index_list[minindex]]
        dic_center[j]=minword
        dic_res2[minword]=dic_words[j]
    util.savejson(respath + '/dic_center2words.json', dic_res2)
    del dic_res2
    for i,w in enumerate(words):
        dic_res[w]=dic_center[cres[i]]
    util.savejson(respath+'/dic_word2center.json',dic_res)
    return dic_res

def predict_tag_by_words(words,dic_word2center):
    # 预测关键词对应的标签，给一组关键词，输出对应标签
    res=[]
    for w in words:
        if w in dic_word2center:
            res.append(dic_word2center[w])
    return list(set(res))

def predict_tag_by_filenames(fns,fn_words,dic_word2center):
    # 对一组文件名，预测其标签，先从离线的fn_kwords查询文件名对应的关键词，查不到的再查kbase
    dic_res={} #{filename:[tag1,tag2...]}
    needkbasefn=[]
    for fn in fns:
        if fn in fn_words:
            words = fn_words[fn]
            dic_res[fn] = predict_tag_by_words(words, dic_word2center)
        else:
            needkbasefn.append(fn)
    kbasekws=get_kwords_kbase(needkbasefn)
    for i,fn in enumerate(needkbasefn):
        dic_res[fn]=predict_tag_by_words(kbasekws[i],dic_word2center)
    return dic_res

def get_kwords_kbase(inputlist):
    # 根据文件名去kbase查关键词
    if type(inputlist) is list:
        fns = inputlist
    else:
        fns = util.load2list(inputlist)
    res = []  # 对应的关键词列表
    kbpk = kbase.PooledKBase(max_connections_cnt=50, mode='cur')
    for i in fns:
        fn = i.strip()
        sql01 = u"SELECT 机标关键词 from CJFDTOTAL,CDFDTOTAL,CMFDTOTAL WHERE 文件名='" + fn + u"'"
        thread_cur = kbpk.get_connection()
        ret = kbpk.cursor_execute_ksql(sql01, thread_cur, mode='all')
        if len(ret) == 0:
            res.append([])
        else:
            kws = re.split(r'[,，;；]+',ret[0][0].strip())
            res.append(kws)
    kbpk.close_connection()
    assert len(res) == len(fns)
    return res

def run01():
    #vecpath=path.path_model+'/w2v_kws1811_d300w8minc1iter5_sgns/w2v_kws1811_d300w8minc1iter5_sgns.vector'
    vecpath=path.path_model+'/w2v_kws1811_d300w5minc3iter5_cbowns/w2v_kws1811_d300w5minc3iter5_cbowns.vector'
    fn_kwords_path=path.path_dataroot + '/other/fn_kws_1811'
    clusterpath=path.path_dataroot+'/cluster'
    clusterrespath = clusterpath + '/cres/k5w.txt'
    words,vecs=mlpre.get_w_v(vecpath)
    vecl = vecs.tolist()
    del vecs
    kmscore,cres=vec_cluster(vecl,clusterrespath,true_k=50000)
    dic_word2center=get_cluter_center(cres,vecl,words,clusterpath)

if __name__ == '__main__':
    run01()
