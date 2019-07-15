#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by lljzhiwang on 2018/12/7 
from gensim.models.doc2vec import Doc2Vec
from gensim.models import keyedvectors
import util_common as util
import numpy as np
import os,sys,pickle
import util_path as path

from Logginger import init_logger
logger=init_logger('MLPrepare',logging_path=path.logpath)

def get_samplevec_gensimmodel(vecpath1, vecpath2, samplefile, prefix, respath='./', stopcnt=100, progress_per=10000):
    #通过样本文件获取对应的向量表示 uid+fn==> [uvec+fnvec]
    data,labels,realexamp=[],[],[]
    logger.info('loading vecfile : %s' % vecpath1)
    # muser=Doc2Vec.load(usermodel)
    v_user = load_vec(vecpath1)
    logger.info('loading vecfile : %s' % vecpath2)
    v_file = load_vec(vecpath2)
    samples=util.load2list(samplefile)
    for cnt,exam in enumerate(samples):
        if cnt%progress_per==0:
            print("getting example vecs : %d" %cnt)
        if stopcnt and stopcnt==cnt:
            break
        exam=exam.strip().split()
        label0=exam[1]
        uid='*dt_' + exam[0].split("+")[0]
        fn='*dt_' + exam[0].split("+")[1]
        if uid in v_user and fn in v_file:
            uvec=list(v_user[uid])
            fvec=list(v_file[fn])
            sampvec=uvec+fvec #拼接
            realexamp.append(exam[0])
            data.append(sampvec)
            labels.append(label0)
    del v_file
    del v_user
    np.savetxt('%s/exampvecs_%s.txt' %(respath,prefix),np.array(data))
    util.list2txt(realexamp,'%s/realexamples_%s.txt' %(respath,prefix))

def get_vec_gensimmodel(vecpath1,samplefile, prefix, respath='./', stopcnt=100, progress_per=10000):
    #通过样本文件获取对应的向量表示 uid+fn==> [uvec+fnvec]
    resdata={}
    logger.info('loading vecfile : %s' % vecpath1)
    v_user = load_vec(vecpath1)
    samples=util.load2list(samplefile)
    for cnt,exam in enumerate(samples):
        if cnt%progress_per==0:
            print("getting example vecs : %d" %cnt)
        # if stopcnt and stopcnt==cnt:
        #     break
        examid=exam.strip()
        uid='*dt_' + examid
        if uid in v_user:
            uvec=list(v_user[uid])
            resdata[examid]=uvec
    with open(respath+'/'+prefix+'.pkl','wb') as f:
        pickle.dump(resdata,f)


def load_vec(vecfilepath,norm=True):
    vect=keyedvectors.Word2VecKeyedVectors.load_word2vec_format(vecfilepath)
    if norm:
        vect.init_sims() #做向量归一化即生成vectors_norm
    return vect

def get_kwsfromfn_bycode(dic_code_fns,fn_kws,respath=None):
    '''
    根据子栏目代吗-fn文件和fn-关键词文件，获取子栏目代码-关键词文件
    :param dic_code_fns: 
    :type dic_code_fns:dict 
    :param fn_kws: 
    :type fn_kws: dict
    :return: 
    :rtype: 
    '''
    res={}
    for k in dic_code_fns.keys():
        tmpkws=[]
        tmpfns=dic_code_fns[k]
        for fn in tmpfns:
            if fn_kws.has_key(fn):
                tmpkws.extend(fn_kws[fn])
        res[k]=tmpkws
    if respath:
        util.savejson(respath,res)
    return res

def get_w_v_all(vecfilepath):
    vect=load_vec(vecfilepath)
    vect.init_sims()
    words=vect.index2word
    vecs=vect.vectors_norm
    # words 和 vecs 顺序是一样的，即index相同
    return words,vecs

def get_w_v_bycode(vecfilepath,dic_code_kws,respath):
    '''
    
    :param vecfilepath: 
    :type vecfilepath: str
    :param dic_code_kws: 
    :type dic_code_kws: dict
    :return: 
    :rtype: 
    '''
    vect = load_vec(vecfilepath)
    vect.init_sims()
    for k in dic_code_kws.keys():
        print("for code %s" %k)
        if '_' in k:
            basepath = respath + '/' + k.split('_')[0]
        else:
            basepath = respath + '/others'
        if not os.path.exists(basepath):
            os.mkdir(basepath)
        resfileword=basepath+'/words_'+k+'.txt'
        resfilevec=basepath+'/vecs_'+k+'.txt'
        if os.path.exists(resfileword) and os.path.exists(resfilevec):
            print("file %s already exists,skip code %s..." %(resfileword,k))
            continue
        curkws=dic_code_kws[k]
        if len(curkws)>100:
            words=[]
            vecs=[]
            curkws_uniq=list(set(curkws))   #去重
            for w in curkws_uniq:
                if w in vect:
                    words.append(w)
                    vec_norm=vect.vectors_norm[vect.vocab[w].index]
                    vecs.append(vec_norm)
            if words:
                print("saving data for code %s get res %d" %(k,len(words)))
                util.list2txt(words,resfileword)
                np.savetxt(resfilevec,np.array(vecs))
    print("get words & vecs by code done!")




if __name__ == '__main__':
    uservecmodel=path.path_model + '/d2v_udownhighq5wposi_d300w5minc3iter30_dmns/d2v_udownhighq5wposi_d300w5minc3iter30_dmns.dv'
    fnvecmodel=path.path_model + '/d2v_highq5w_l1t1_d300w5minc3iter30_dmns/d2v_highq5w_l1t1_d300w5minc3iter30_dmns.dv'
    userlist=path.path_datahighq5w+'/realexam_users.txt'
    fnslist=path.path_datahighq5w+'/realexam_fns.txt'
    get_vec_gensimmodel(uservecmodel,userlist,prefix='realvec_user',respath=path.path_datahighq5w)
    get_vec_gensimmodel(fnvecmodel, fnslist, prefix='realvec_fn', respath=path.path_datahighq5w)


