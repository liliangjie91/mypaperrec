#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by liliangjie on 2018/11/10 
# Email llj : laiangnaduo91@gmail.com
from collections import Counter
import os,codecs
import util_common as util


def getword4file(filepath):
    '''
    
    :param filepath: 
    :return: 
    :rtype:list
    '''
    res=[]
    with codecs.open(filepath,'rU',encoding='utf8') as f:
        for line in f:
            line = line.strip()
            res.extend(line.split())
    return res

def getword4folder(path):
    '''
    
    :param path: 
    :return:
    :rtype: list
    '''
    filepaths=util.getfileinfolder(path,'2.txt')
    res=[]
    for filep in filepaths:
        if os.path.isfile(filep):
            res.extend(getword4file(filep))
    print("get totaly %d words" %len(res))
    return res

def getfiledtop(cnter,filedfile,top=50):
    '''
    按filedfile里词的词频排序
    :param cnter: counter of all words
    :type cnter: Counter
    :param filedfile: 
    :param top: 
    :return: 
    '''
    worddic={}
    inwords = util.load2list(filedfile)
    for i in inwords:
        if cnter.has_key(i):
            worddic[i]=cnter[i]
    newcnter=Counter(worddic)
    top = min(len(newcnter),top)
    topnwords=[ "%s %d" %(i,c) for (i , c) in newcnter.most_common(top)]
    respath= "%s_top%d.txt" %(os.path.splitext(filedfile)[0],top)
    util.list2txt(topnwords,respath)
    return topnwords



def main():
    basepath=r'./data'
    segpath=basepath+r'/data_seg'
    filedpath=r'./source/other_jiebadicts'
    filedfiles=util.getfileinfolder(filedpath,'s.txt')
    wordl=getword4folder(segpath)
    c = Counter(wordl)
    print("get totaly %d distinct words" %len(c))
    print('常用词频度统计结果')
    for (k, v) in c.most_common(50):
        print('%s%s %s  %d' % ('  ' * (5 - len(k)), k, '*' * int(v / 10000), v))

    for f in filedfiles:
        getfiledtop(c,f,200)


if __name__ == '__main__':
    main()