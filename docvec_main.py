#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by lljzhiwang on 2018/12/6

import psutil
import time,Path,sys,os,codecs,logging
import util_common as util
from gensim.models.doc2vec import Doc2Vec,TaggedDocument

BIANMA= 'utf8'
datapath= r'./data'
# bianma='gb18030'
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s')
logging.root.setLevel(level=logging.INFO)
logger.info("running %s" % ' '.join(sys.argv))
testwl=['zgjq200914010','1011143537.nh','DYPJ200924005','2010261634.nh','1014310786.nh','1012347178.nh',
        '1012258129.nh','ddyi201218094','fxsy201508029']

class MyDocuments(object):
    '''
    根据分好词的文件生成句子序列，用于word2vec训练
    dirname:分好词的文件路径，可以是单个文件路径也可以是文件夹地址，文件以txt结尾
    start:从一行的第几个元素开始算词。因为有的文件每行第一个元素是用户id，则start=1用于略过id，
    '''
    def __init__(self, dirname, start=0):
        self.dirname = dirname
        self.start=start

    def __iter__(self):
        cnt = -1
        if os.path.isfile(self.dirname):
            with codecs.open(self.dirname, 'rU', 'utf8', errors='ignore') as f:
                for line in f:
                    l=line.strip().split()
                    if self.start:
                        if len(l)>self.start+1: #word must more than 1
                            yield TaggedDocument(l[self.start:],l[:self.start])
                    else:
                        if len(l)>1:
                            cnt+=1
                            yield TaggedDocument(l,[cnt])
        else:
            for fname in os.listdir(self.dirname):
                if 'l1t1.txt' in fname:
                    # logger.info("now precessing file %s" %fname)
                    with codecs.open(os.path.join(self.dirname, fname), 'rU', 'utf8', errors='ignore') as f:
                        for line in f:
                            l = line.strip().split()
                            if self.start:
                                if len(l) > self.start+1:
                                    yield TaggedDocument(l[self.start:],l[:self.start])
                            else:
                                if len(l) > 1:
                                    cnt += 1
                                    yield TaggedDocument(l, [cnt])

def train_gensim(modelname,indatapath,size=200,window=5,minc=2,iter=5,sg=0,hs=0,neg=5,trainwv=1,annoy=False):
    modelfolder= datapath + r'/model/%s' % modelname
    if not os.path.exists(modelfolder):
        os.mkdir(modelfolder)
    modelpath="%s/%s.model" %(modelfolder,modelname)
    wvecname = "%s/%s.wv" % (modelfolder, modelname)
    dvecname = "%s/%s.dv" % (modelfolder, modelname)
    if os.path.exists(modelpath):
        logger.info("model %s has already exists!!!")
        return
    word2vec_start_time = time.time()

    print("开始训练gensim模型:当前时间 : %s" %time.asctime(time.localtime(time.time())))
    model = Doc2Vec(MyDocuments(indatapath,start=1),size=size,iter=iter,window=window,min_count=minc,
                    dm=1-sg,hs=hs,negative=neg,workers=20,dbow_words=trainwv)  # workers=multiprocessing.cpu_count()
    print("gensim训练完毕 %.2f secs" % (time.time() - word2vec_start_time))

    model.save(modelpath)  #保存整个模型以及训练过程的数据（其实会生成3个文件model,syn0,syn1 or syn1neg）
    model.wv.save_word2vec_format(wvecname, binary=False)
    model.docvecs.save(dvecname)
    print model
    # KeyedVectors.load_word2vec_format(vecname)
    # print_mostsimi(model, testwl)

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
            result = model.docvecs.most_similar(w,topn=top,indexer=annoyindex)
            for e in result:
                print("%s : %.3f" %(e[0],e[1]))
            print("**********************************************")
            result = model.most_similar([model.docvecs[w]], topn=top, indexer=annoyindex)
            for e in result:
                print("%s : %.3f" % (e[0], e[1]))
        except KeyError, e:
            print("word %s is not in the model!" %w)
    print("--------------time cost %.3f secs/word " %((time.time()-t)/float(len(wordlist))))

def test_model(d2vmodel, testwl=testwl, topn=10, evalut=False):
    model = Doc2Vec.load(d2vmodel) if type(d2vmodel) is str else d2vmodel
    print_mostsimi(model, testwl, top=topn)
    if evalut:
        ina = raw_input("model score 1-9 : ")
        f = open(datapath + r'/model/gensim/modelscore.txt', 'a')
        f.write("size=%d window=%d mincount=%d iter=%d sg=%d hs=%d ns=%d score=%s\n"
                %(model.vector_size, model.window, model.min_count, model.iter, model.sg, model.hs, model.negative, ina))
        f.close()

def run_single_train(argslist, mnameprefix='model', justgetname=False):
    (size, win, minc, iter, sg, hs, neg) = argslist
    segdatapath = datapath + r'/data_seg/sumery_highq5w'
    modeltype = 'dbow' if sg else 'dm'
    opttypehs = 'hs' if hs else ''
    opttypens = 'ns' if neg else ''
    modelname = 'd2v_%s_d%dw%dminc%diter%d_%s%s%s'% (mnameprefix, size, win, minc, iter, modeltype, opttypehs, opttypens)
    if not justgetname:
        logger.info("Starting train model : %s" %modelname)
        train_gensim(modelname, indatapath=segdatapath, size=size, window=win,
                     minc=minc, iter=iter, sg=sg, hs=hs, neg=neg)
    return modelname

def run_train(mnameprefix='model',justgetname=False):
    #        dim,win,min,itr,sg,hs,neg
    argls = [[300, 5, 1, 50, 0, 0, 10]]
    mnames=[]
    for argl in argls:
        modelname = run_single_train(argl, mnameprefix=mnameprefix ,justgetname=justgetname)
        mnames.append(modelname)
    return  mnames

if __name__ == '__main__':
    names=run_train(mnameprefix='highq5w_l1t1')
    for mname in names:
        modelpath="%s/%s/%s.model" %(Path.path_model,mname,mname)
        test_model(modelpath)


