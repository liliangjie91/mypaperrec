#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by xw on 2017/4/14 

import time

from gensim.similarities.index import AnnoyIndexer

import Path
import segmentation

from gensim.models import Word2Vec, KeyedVectors


class Word2Vector(object):
    # 加载训练好的词向量
    print ('Loading word2vec_user_search_model from %s ...' % Path.word2vec_user_search_model_path)
    t1 = time.clock()
    word2vec_user_search_model = Word2Vec.load(Path.word2vec_user_search_model_path, mmap='r')
    word2vec_user_search_model.wv.syn0norm = word2vec_user_search_model.wv.syn0
    print ('Loading word2vec_user_search_model cost %3f seconds.' % (time.clock() - t1))

    print ('Loading word2vec_user_search_model_index from %s ...' % Path.word2vec_user_search_model_index_path)
    t1 = time.clock()
    word2vec_user_search_model_index = AnnoyIndexer()
    word2vec_user_search_model_index.load(Path.word2vec_user_search_model_index_path)
    word2vec_user_search_model_index.model = word2vec_user_search_model
    print ('Loading word2vec_user_search_model_index cost %3f seconds.' % (time.clock() - t1))

    print ('Loading word2vec_model from %s ...' % Path.word2vec_model_path)
    t1 = time.clock()
    word2vec_model = Word2Vec.load(Path.word2vec_model_path, mmap='r')
    word2vec_model.wv.syn0norm = word2vec_model.wv.syn0
    print ('Loading word2vec_model cost %3f seconds.' % (time.clock() - t1))

    print ('Loading word2vec_model_index from %s ...' % Path.word2vec_model_index_path)
    t1 = time.clock()
    word2vec_model_index = AnnoyIndexer()
    word2vec_model_index.load(Path.word2vec_model_index_path)
    word2vec_model_index.model = word2vec_model
    print ('Loading word2vec_model_index cost %3f seconds.' % (time.clock() - t1))

    def __init__(self):
        """
        初始化
        """
        self.sw = segmentation.WordSegmentation()  # 分词类实例

    def most_similar_user_search(self, text, top=10):
        '''
        在用户检索词向量模型中查找与输入最相关的n个词
        :param text: 用户输入
        :type text: string
        :return: 与输入最相关的词列表
        :param top: top n个数，默认为10
        :type top: int
        :rtype: list
        '''
        if text.strip() == '':
            return []
        else:
            try:
                words = self.sw.segment(text)
                if (len(words) == 0):
                    return []
                else:
                    result = Word2Vector.word2vec_user_search_model.wv.most_similar(words, topn=top + 1,
                                                                                indexer=Word2Vector.word2vec_user_search_model_index)
                    return [(item[0], item[1]) for item in result if item[0] != text and item[0] not in words and len(item[0])>1 and len(item[0])<20]
            except KeyError, e:
                return []

    def most_similar_global(self, text, top=10):
        '''
        在词向量模型中查找与输入最相关的n个词
        :param text: 用户输入
        :type text: string
        :return: 与输入最相关的词列表
        :param top: top n个数，默认为10
        :type top: int
        :rtype: list
        '''
        if text.strip() == '':
            return []
        else:
            try:
                words = self.sw.segment(text)
                if(len(words)==0):
                    return []
                else:
                    result = Word2Vector.word2vec_model.wv.most_similar(words, topn=top + 1,indexer=Word2Vector.word2vec_model_index)
                    return [(item[0], item[1]) for item in result if item[0] != text and item[0] not in words and len(item[0])>1 and len(item[0])<20 ]
            except KeyError, e:
                return []
