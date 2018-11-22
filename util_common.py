#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by liliangjie on 2018/11/10 
# Email llj : laiangnaduo91@gmail.com
import codecs
import os,sys
import logging

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
    if os.path.exists(path):
        logger.info("file %s exists del it.." %path)
        os.remove(path)
    with open(path,'w') as f:
        for i in l:
            f.write(i.encode('utf-8', 'ignore')+'\n')

def load2list(path,to1column=False,separator=None,get1column=-1):
    '''
    
    :param path: 
    :param separator: 
    :return: 
    :rtype:list
    '''
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

def load2dic(path,separator=None):
    '''
    
    :param path: 
    :param separator: 
    :return: 
    :rtype: dict
    '''
    res={}
    if os.path.isfile(path):
        with codecs.open(path, 'rU', encoding=bianma, errors='replace') as f:
            for l in f:
                ll=l.strip().split(separator)
                for i in ll:
                    res[i]=res.get(i,0)+1
    return res

