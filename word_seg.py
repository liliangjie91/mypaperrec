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

def seg4oneline(line,minwc=3,minwlen=0,convert=False):
    '''
    对一行序列/一句话分词
    :param line: 一行，一句
    :type line: str
    :param minwc: 分词结果最小词数，如果分词后结果小于minwc，则输出空
    :type minwc: int
    :param minwlen: 分词后单个词的最小长度如，'我' 长度=1 '我们' = 2 小于改长度则不计入分词结果
    :type minwlen: int
    :param convert: 是否做全角转化，简繁转换
    :type convert: bool
    :return: 
    :rtype: 
    '''
    line = line.strip().lower()
    if convert:
        line = IOTools.str_full2half(line)  # 全角转半角
        line = IOTools.Converter('zh-hans').convert(line)  # 繁体转简体
    wordseg2 = ws.segment(line)
    wordseg = [i for i in wordseg2 if len(i) > minwlen]
    if len(wordseg) > minwc:
        return wordseg
    else:
        return []

def seg4fulltext(fulltext,sent_num=1):
    '''
    对一段/篇文章做分词，分词结果为列表，每个元素为：每句话的分词结果用空格拼接的字符串
    默认原文一句为分词中的一句即sent_num=1
    (因为分句会按照。；回车等符号断句，
    但对于有些文章或小说，句子比较碎，即句子普遍都很短，
    则可以设置多句为一句用于分词，这样，一行就能包含较丰富的信息)
    :param fulltext: 全文或段落,即若干句话拼接成的一行str
    :type fulltext: str 
    :param sent_num: 原文几句为分词时的一句输入
    :type sent_num: int
    :return: 
    :rtype: list
    '''
    wordres = []
    t1=time.time()
    # 对整体全文直接做转换效率比每句做一遍高
    fulltext = IOTools.str_full2half(fulltext)  # 全角转半角
    fulltext = IOTools.Converter('zh-hans').convert(fulltext)  # 繁体转简体
    sentences = ss.segment(fulltext.lower())
    logger.info("sentences seg done! cost %d secs , get %d sentences" % ((time.time() - t1), len(sentences)))
    if sentences:
        cnt = 0
        tmpsents=[]
        for i, sent in enumerate(sentences, 1):
            cnt += 1
            tmpsents.append(sent)
            if i%sent_num==0:
                wseg=seg4oneline(''.join(tmpsents))
                if wseg:
                    wordres.append(' '.join(wseg))
                tmpsents=[]
        if tmpsents:
            wseg = seg4oneline(''.join(tmpsents))
            if wseg:
                wordres.append(' '.join(wseg))
    return wordres

def seg4file_book(infile, respath):
    '''
    对文章或小说做分词，要注意文章一行不一定一句。所以先把全文组合成一个str，再分句，再分词
    本方法原旨在处理一部系列小说，其小说格式较为奇葩
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
    del alllines
    if fulltext:
        t2 = time.time()
        wordres=seg4fulltext(fulltext)
        timecha = time.time() - t2
        logger.info("%s done. totaly  %.2f MB cost %.1f secs" % (infile, fsize, timecha))
        logger.info(" --------   %.2f MB/sec --------    %.2fMB/min" % (
            float(fsize) / float(timecha), float(fsize) * 60 / float(timecha)))
        if wordres:
            filename = os.path.split(infile)[1]
            util.list2txt(wordres, os.path.join(respath, filename))
        else:
            raise Exception("Word Seg Res is None, Please Check Your Input File!!!")

def seg4file_1line1sent(infile, respath):
    '''
    对单个文件分词，本方法不涉及到分句，默认输入的一行就是一句
    例如一行对应一段关键词，或者就简单的一行对应一个标题
    '''
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
            wseg=seg4oneline(line)
            if wseg:
                res.append(' '.join(wseg))
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
        seg4file_book(f, respath)

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
    seg4file_book(rec_path, segdatapath)
    # return amount_and_dict

if __name__ == '__main__':
    basepath=r'./data'
    rawdatapath=basepath+r'/data_raw/jinyongquanji'
    segdatapath=basepath+r'/data_seg'
    segdatapathtmp = basepath + r'/data_seg/tmp'
    inputpath=segdatapath+r'/shendiaoxialv2.txt'
    tlbbpath = rawdatapath + r'/tianlongbabu2.txt'
    # seg4file(rawdatapath,segdatapath)
    seg4file_book(tlbbpath, segdatapathtmp)
    # parallel_running(rawdatapath)
    # single_running(rawdatapath,segdatapath)