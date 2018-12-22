#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by lljzhiwang on 2018/12/7 
from gensim.models.doc2vec import Doc2Vec
from gensim.models import keyedvectors
import util_common as util
import numpy as np
import os,sys,util_path,time


def get_samplevec_gensimmodel(vecpath1, vecpath2, samplefile):
    data=[]
    label=[]
    print('loading vecfile : %s' % vecpath1)
    # muser=Doc2Vec.load(usermodel)
    v_user = load_vec(vecpath1)
    print('loading vecfile : %s' % vecpath2)
    v_file = load_vec(vecpath2)
    sample00=util.load2list(samplefile)
    cnt=0
    for l in sample00:
        if cnt%10000==0:
            print(cnt)
        cnt+=1
        if cnt==1000:
            break
        l=l.strip().split()
        label0=l[1]
        uid='*dt_' + l[0].split("+")[0]
        fn='*dt_' + l[0].split("+")[1]
        if uid in v_user and fn in v_file:
            uvec=list(v_user[uid])
            fvec=list(v_file[fn])
            sampvec=uvec+fvec
            data.append(sampvec)
            label.append(label0)
    del v_file
    del v_user
    np.savetxt('./test.txt',np.array(data))
    # util.list2txt(label,'./lable.txt')

def load_vec(vecfilepath):
    return keyedvectors.Word2VecKeyedVectors.load_word2vec_format(vecfilepath)

def get_w_v(vecfilepath):
    vect=load_vec(vecfilepath)
    words=vect.index2word
    vecs=vect.vectors
    # words 和 vecs 顺序是一样的，即index相同
    return words,vecs

if __name__ == '__main__':
    get_samplevec_gensimmodel(util_path.path_model + '/d2v_udownhighq5wposi_d300w5minc3iter30_dmns/d2v_udownhighq5wposi_d300w5minc3iter30_dmns.dv',
                              util_path.path_model + '/d2v_highq5w_l1t1_d300w5minc3iter30_dmns/d2v_highq5w_l1t1_d300w5minc3iter30_dmns.dv',
                              util_path.path_datahighq5w + '/sample_highq5w_neg.txt')

