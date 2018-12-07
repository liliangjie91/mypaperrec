#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by lljzhiwang on 2018/12/7 
from gensim.models.doc2vec import Doc2Vec
import util_common as util
import numpy as np
import os,sys,Path,time


def get_feature_gensimmodel(usermodel,filemodel,samplefile):
    data=[]
    label=[]
    print('loading d2v model : %s' %usermodel)
    muser=Doc2Vec.load(usermodel)
    print('loading d2v model : %s' % filemodel)
    mfile=Doc2Vec.load(filemodel)
    sample00=util.load2list(samplefile)
    cnt=0
    for l in sample00:
        if cnt%10000==0:
            print(cnt)
        cnt+=1
        if cnt==10000:
            break
        l=l.strip().split()
        label0=l[1]
        uid=l[0].split("+")[0]
        fn=l[0].split("+")[1]
        if uid in muser.docvecs and fn in mfile.docvecs:
            uvec=list(muser.docvecs[uid])
            fvec=list(mfile.docvecs[fn])
            sampvec=uvec+fvec
            data.append(sampvec)
            label.append(label0)
    del mfile
    del muser
    np.savetxt('./data_10000_neg.txt',np.array(data))
    # util.list2txt(label,'./lable.txt')

if __name__ == '__main__':
    get_feature_gensimmodel(Path.path_model+'/d2v_udownhighq5wposi_d300w5minc3iter30_dmns/d2v_udownhighq5wposi_d300w5minc3iter30_dmns.model',
                            Path.path_model+'/d2v_highq5w_l1t1_d300w5minc3iter30_dmns/d2v_highq5w_l1t1_d300w5minc3iter30_dmns.model',
                            Path.path_datahighq5w+'/sample_highq5w_neg.txt')

