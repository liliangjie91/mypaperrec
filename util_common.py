#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by liliangjie on 2018/11/10 
# Email llj : laiangnaduo91@gmail.com
import codecs
import os,sys,json
import logging
import progressbar

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s')
logging.root.setLevel(level=logging.INFO)
logger.info("running %s" % ' '.join(sys.argv))
bianma='utf8'

def getfileinfolder(folderpath,prefix=None):
    '''
    返回文件夹内符合prefix前缀的文件名
    :param folderpath: 文件夹
    :type folderpath: str
    :param prefix: 前缀匹配模式
    :type prefix: str
    :return: 
    :rtype: list
    '''
    res=[]
    if os.path.exists(folderpath):
        for file in os.listdir(folderpath):
            file_p = os.path.join(folderpath,file)
            if os.path.isfile(file_p):
                if prefix and prefix in file_p:
                    res.append(file_p)
                if not prefix:
                    res.append(file_p)
    return res

def get_FileSize(filePath):
    '''
    获取文件大小MB
    :param filePath: 
    :return: 
    '''
    filePath = unicode(filePath,'utf8')
    fsize = os.path.getsize(filePath)
    fsize = fsize/float(1024*1024)
    return round(fsize,2)

def list2txt(l,path):
    '''
    写list成txt
    :param l: 
    :param path: 
    :return: 
    '''
    logger.info("saving list2file : %s" % path)
    if os.path.exists(path):
        logger.info("file %s exists del it.." %path)
        os.remove(path)
    with open(path,'w') as f:
        for i in l:
            f.write(i.encode('utf-8', 'ignore')+'\n')

def load2list(path,to1column=False,separator=None,get1column=-1):
    '''
    读取文本返回成list，默认一行一元素，也可按分隔符分割后每部分为一元素，也可单独获取分割后的某列元素为一元素
    :param path: 
    :type path: str
    :param to1column: 
    :type to1column:bool 
    :param separator: 
    :type separator: bool
    :param get1column: 
    :type get1column: 
    :return: 
    :rtype: list
    '''
    logger.info("loading file2list : %s" %path)
    res=[]
    if os.path.isfile(path):
        with codecs.open(path,'rU',encoding=bianma,errors='replace') as f:
            for l in f:
                if l.strip():
                    if to1column :
                        res.extend(l.split(separator))
                    elif get1column>=0:
                        res.append(l.split(separator)[get1column])
                    else:
                        res.append(l.strip())
    return res

def savejson(path,j):
    logger.info("saving file2json : %s" % path)
    with codecs.open(path,"w",encoding=bianma) as f:
        json.dump(j,f)

def loadjson(path):
    '''
    
    :param path: 
    :type path: 
    :return: 
    :rtype:dict 
    '''
    logger.info("loading jsonfile : %s" % path)
    with codecs.open(path, "rU") as f:
        res=json.load(f)
    return res


def load2dic(path, separator=None):
    '''
    把文件加载成字典。其中，文件每行第一个元素是key，后续元素组成列表做value
    :param path: 
    :param separator: 
    :return: 
    :rtype: dict
    '''
    logger.info("loading file2dic : %s" % path)
    res = {}
    if os.path.isfile(path):
        with codecs.open(path, 'rU', encoding=bianma, errors='replace') as f:
            for l in f:
                ll = l.strip().split(separator)
                if len(ll)>1:
                    res[ll[0]]=ll[1:]
    print("all lines : %d" %len(res))
    return res

def load2dic_wc(path,separator=None):
    '''
    把文件加载成字典，文件每行每个元素是key，词频是value
    :param path: 
    :param separator: 
    :return: 
    :rtype: dict
    '''
    logger.info("loading file2dic_wc : %s" % path)
    res={}
    if os.path.isfile(path):
        with codecs.open(path, 'rU', encoding=bianma, errors='replace') as f:
            for l in f:
                ll=l.strip().split(separator)
                for i in ll:
                    res[i]=res.get(i,0)+1
    print("all lines : %d" % len(res))
    return res


