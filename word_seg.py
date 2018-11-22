#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by liliangjie on 2018/11/10 
# Email llj : laiangnaduo91@gmail.com
import segmentation
import os
import codecs
import logging
import sys
import IOTools
import time
import util_common as util

bianma='utf8'
basepath=r'./data'
# bianma='gb18030'
ss = segmentation.SentenceSegmentation()
ws = segmentation.WordSegmentation()
print("add other jieba dicts")
ws.addotherdics()
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s')
logging.root.setLevel(level=logging.INFO)
logger.info("running %s" % ' '.join(sys.argv))


def segbook4file(infile,respath):
    '''
    对文章或小说做分词，要注意文章一行不一定一句。所以先把全文组合成一个str，再分句，再分词
    :param infile: 
    :param respath: 
    :return: 
    '''
    alllines=[]
    fsize = util.get_FileSize(infile)
    logger.info("doing %s  and its %.2fMB" %(infile,float(fsize)))
    with codecs.open(infile, 'rU', encoding=bianma, errors='replace') as f:
        for line in f:
            l = line.strip()
            if l:
                alllines.append(l)
    fulltext=''.join(alllines)
    if fulltext:
        wordres=seg4fulltext(fulltext,infile,fsize)
        if wordres:
            filename = os.path.split(infile)[1]
            util.list2txt(wordres, os.path.join(respath, filename))

def seg4fulltext(fulltext,infile,fsize,sent_num=10):
    wordres = []
    t1=time.time()
    sentences = ss.segment(fulltext.lower())
    logger.info("%s sentences seg done! cost %d secs , get %d sentences" % (infile, (time.time() - t1), len(sentences)))
    if sentences:
        t2 = time.time()
        cnt = 0
        tmpsents=[]
        for i, sent in enumerate(sentences, 1):
            cnt += 1
            tmpsents.append(sent)
            if i%sent_num==0:
                wordseg = ws.segment(''.join(tmpsents))
                wordseg2=[i for i in wordseg if len(i)>1]
                wordres.append(' '.join(wordseg2))
                tmpsents=[]
        if tmpsents:
            wordseg = ws.segment(''.join(tmpsents))
            wordseg2 = [i for i in wordseg if len(i) > 1]
            wordres.append(' '.join(wordseg2))
        timecha = time.time() - t2
        logger.info("%s done. there are totaly %d lines %.2f MB cost %.1f secs" % (infile, cnt, fsize, timecha))
        logger.info(" --------   %.2f MB/sec --------    %.2fMB/min" % (
            float(fsize) / float(timecha), float(fsize) * 60 / float(timecha)))
    return wordres

def seg4file(infile,respath):
    '''对单个文件分词，注意，该方法对应一行就是一句的情况'''
    res = []
    t0 = time.time()
    cnt = 0
    fsize = util.get_FileSize(infile)
    logger.info("now doing file : %s and its size is %.2f MB" % (infile, fsize))
    with codecs.open(infile, 'rU', encoding=bianma, errors='replace') as f:
        for line in f:
            cnt += 1
            if cnt % 50000 == 0: #差不多1分钟
                logger.info("doing %s line: %d" % (infile, cnt))
            line = line.strip()
            if ss.has_chinese_character(line):
                line = IOTools.str_full2half(line)  # 全角转半角
                line = IOTools.Converter('zh-hans').convert(line)  # 繁体转简体
                wordseg2 = ws.segment(line)
                wordseg=[i for i in wordseg2 if len(i)>1]
                if len(wordseg) > 3:
                    res.append(' '.join(wordseg))
    timecha = time.time() - t0
    logger.info("file %s done. there are totaly %d lines %.2f MB cost %.1f secs" % (infile, cnt, fsize, timecha))
    logger.info(" --------   %.2f MB/sec --------    %.2fMB/min" % (
    float(fsize) / float(timecha), float(fsize) * 60 / float(timecha)))
    if res:
        filename = os.path.split(infile)[1]
        util.list2txt(res, os.path.join(respath, filename))

def single_running(path,respath):
    '''
    单线程跑
    :param path: 文本分割后的路径
    :type path: 
    :param respath: 结果路径文件夹
    :type respath: 
    :return: 
    :rtype: 
    '''
    infiles = util.getfileinfolder(path, prefix='2')
    for i,f in enumerate(infiles):
        print("dong %d th file" %i)
        segbook4file(f,respath)

def parallel_running(path):
    """
    多进程并将对应结果集写入共享资源，维持执行的进程总数，当一个进程执行完毕后会添加新的进程进去(非阻塞)
    :param path: 文本分割后的路径
    :type path: unicode string
    :return: 结果集
    :rtype: list
    """
    from multiprocessing import Pool
    infiles = util.getfileinfolder(path, prefix='2')
    num_cpus = 2   # 直接利用multiprocessing.cpu_count()
    pool = Pool(num_cpus)
    pool.map(wrap, infiles)
    pool.close()
    pool.join()

def wrap(rec_path):
    """
    多进程执行的包裹函数
    :param rec_path: 单文本路径
    :type rec_path: unicode string
    :return: 以元组形式返回结果集
    :rtype: tuple
    """
    segdatapath = basepath + r'/data_seg'
    # seg4file(rec_path,segdatapath)
    segbook4file(rec_path,segdatapath)
    # return amount_and_dict

if __name__ == '__main__':
    basepath=r'./data'
    rawdatapath=basepath+r'/data_raw/jinyongquanji'
    segdatapath=basepath+r'/data_seg'
    segdatapathtmp = basepath + r'/data_seg/tmp'
    inputpath=segdatapath+r'/shendiaoxialv2.txt'
    tlbbpath = rawdatapath + r'/tianlongbabu2.txt'
    # seg4file(rawdatapath,segdatapath)
    segbook4file(tlbbpath,segdatapathtmp)
    # parallel_running(rawdatapath)
    # single_running(rawdatapath,segdatapath)