#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by lljzhiwang on 2018/11/5 

import os
import psutil
import codecs
import logging
import sys
import IOTools
import time
import util_common as util
from gensim.models import Word2Vec,KeyedVectors
from gensim.similarities.index import AnnoyIndexer

BIANMA= 'utf8'
datapath= r'./data'
# bianma='gb18030'
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s')
logging.root.setLevel(level=logging.INFO)
logger.info("running %s" % ' '.join(sys.argv))
testwl=[u'中国',u'一带一路',u'广东省',u'计算机',u'经济',u'微信']

class MySentences(object):
    def __init__(self, dirname, start=0):
        self.dirname = dirname
        self.start=start

    def __iter__(self):
        if os.path.isfile(self.dirname):
            with codecs.open(self.dirname, 'rU', 'utf8', errors='ignore') as f:
                for line in f:
                    l=line.strip().split()
                    if self.start:
                        if len(l)>self.start+1: #word must more than 1
                            yield l[self.start:]
                    else:
                        if len(l)>1:
                            yield l
        else:
            for fname in os.listdir(self.dirname):
                if '.txt' in fname:
                    logger.info("now precessing file %s" %fname)
                    with codecs.open(os.path.join(self.dirname, fname), 'rU', 'utf8', errors='ignore') as f:
                        for line in f:
                            l = line.strip().split()
                            if self.start:
                                if len(l) > self.start+1:
                                    yield l[self.start:]
                            else:
                                if len(l) > 1:
                                    yield l

def train_gensim(modelname,indatapath,size=200,window=5,minc=2,iter=5,sg=0,hs=0,neg=5,annoy=False):
    modelfolder= datapath + r'/model/%s' % modelname
    if not os.path.exists(modelfolder):
        os.mkdir(modelfolder)
    modelpath="%s/%s.model" %(modelfolder,modelname)
    vecname = "%s/%s.vector" % (modelfolder, modelname)
    annoypath="%s/%s.annoy" %(modelfolder,modelname)
    if os.path.exists(modelpath):
        logger.info("model %s has already exists!!!")
        return
    word2vec_start_time = time.time()
    print("开始训练gensim模型:当前时间 : %s" %time.asctime(time.localtime(time.time())))
    model = Word2Vec(MySentences(indatapath,start=1), size=size, iter=iter, window=window, min_count=minc,
                     sg=sg,hs=hs,negative=neg,workers=20)  # workers=multiprocessing.cpu_count()
    print("gensim训练完毕 %.2f secs" % (time.time() - word2vec_start_time))
    model.save(modelpath)  #保存整个模型以及训练过程的数据（其实会生成3个文件model,syn0,syn1 or syn1neg）
    model.wv.save_word2vec_format(vecname, binary=False)
    # KeyedVectors.load_word2vec_format(vecname)
    # print_mostsimi(model, testwl)
    if annoy:
        aindex=load_annoy(annoypath, model)
        print_mostsimi(model, testwl, aindex)

def print_relationsimi(model,l,top=10):
    '''
    l = [a,b,c,d]
    a-b=c-d ==>  a+d-b=c
    man - woman = king - queen  ==>  queen + man - women = king
    so in 金庸 shuld be 杨过 - 小龙女 = 郭靖 - 黄蓉 ==> 黄蓉(d) + 杨过(a) - 小龙女(b) = 郭靖
    :param model: 
    :param l:
    :type l:list
    :return: 
    '''
    if len(l) != 4:
        print("input l length is not 4!")
        return
    a,b,c,d = l[0],l[1],l[2],l[3]
    print("------------for word : %s + ( %s - %s ) . the answer should be like %s" %(d,a,b,c))
    try:
        result = model.most_similar([a,d],[b],topn=top)
        for e in result:
            print("%s : %.3f" % (e[0], e[1]))
    except KeyError, e:
        print("some word is not in the model!")

def print_mostsimi(model, wordlist, annoyindex=None,top=10):
    '''
    获取模型的mostsimilar结果
    :param model: 
    :type model:Word2Vec 
    :param wordlist: 
    :type wordlist: list
    :param annoyindex: 
    :type annoyindex: AnnoyIndexer
    :return: 
    :rtype: 
    '''
    t = time.time()
    for w in wordlist:
        print("------------for word : %s" %w)
        try:
            result = model.most_similar(w,topn=top,indexer=annoyindex)
            for e in result:
                print("%s : %.3f" %(e[0],e[1]))
        except KeyError, e:
            print("word %s is not in the model!" %w)
    print("--------------time cost %.3f secs/word " %((time.time()-t)/float(len(wordlist))))

def load_annoy(annoypath, model):
    '''

    :param annoypath: 
    :type annoypath: 
    :param model: 
    :type model: Word2Vec
    :return: 
    :rtype: AnnoyIndexer
    '''
    if not os.path.exists(annoypath):
        print("开始构建annoy索引:当前时间 : " + time.asctime(time.localtime(time.time())))
        starttime12 = time.time()
        aindex = AnnoyIndexer(model, 200)
        print("构建索引完毕 %.2f secs" % (time.time() - starttime12))
        # 保存annoy索引
        print("开始保存annoy索引")
        starttime13 = time.time()
        aindex.save(annoypath)
        print("保存索引完毕 %.2f secs" % (time.time() - starttime13))
    else:
        aindex = AnnoyIndexer()
        aindex.load(annoypath)
    return aindex

def load_annoyindex(modelpath, annoypath):

    model=Word2Vec.load(modelpath)
    psvm=psutil.virtual_memory()
    memto=psvm.total >> 20
    pcent=psvm.percent
    print("before del syn1 syn0 mem useage : %.2f MB" %(memto*pcent/100.0))
    model.init_sims(replace=True)
    psvm = psutil.virtual_memory()
    memto = psvm.total >> 20
    pcent = psvm.percent
    print("after del syn1 syn0 mem useage : %.2f MB" % (memto * pcent / 100.0))

    print_mostsimi(model, testwl)
    aindex=load_annoy(annoypath, model)
    print_mostsimi(model, testwl, aindex)

def test_model(w2vmodel,testwl=testwl,topn=10,evalut=False):
    model = Word2Vec.load(w2vmodel) if type(w2vmodel) is str else w2vmodel
    print_mostsimi(model, testwl, top=topn)
    if evalut:
        ina = raw_input("model score 1-9 : ")
        f = open(datapath + r'/model/gensim/modelscore.txt', 'a')
        f.write("size=%d window=%d mincount=%d iter=%d sg=%d hs=%d ns=%d score=%s\n"
                %(model.vector_size, model.window, model.min_count, model.iter, model.sg, model.hs, model.negative, ina))
        f.close()

def run_single_train(argslist, mnameprefix='model', justgetname=False):
    (size, win, minc, iter, sg, hs, neg) = argslist
    segdatapath = datapath + r'/data_seg'
    modeltype = 'sg' if sg else 'cbow'
    opttypehs = 'hs' if hs else ''
    opttypens = 'ns' if neg else ''
    modelname = '%sd%dw%dminc%diter%d_%s%s%s_w2v'% (mnameprefix, size, win, minc, iter, modeltype, opttypehs, opttypens)
    if not justgetname:
        logger.info("Starting train model : %s" %modelname)
        train_gensim(modelname, indatapath=segdatapath, size=size, window=win,
                     minc=minc, iter=iter, sg=sg, hs=hs, neg=neg)
    return modelname

def run_train(mnameprefix='model'):
    #        dim,win,min,itr,sg,hs,neg
    argls = [[200, 5, 1, 5, 1, 0, 5]]
    for argl in argls:
        modelname = run_single_train(argl, mnameprefix=mnameprefix ,justgetname=False)


if __name__ == '__main__':
    run_train(mnameprefix="test_")


