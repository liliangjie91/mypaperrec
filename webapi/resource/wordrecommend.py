#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by xw on 2017/4/14 

from word2vec4web import Word2Vector
from __init__ import *

parser = reqparse.RequestParser(bundle_errors=True)
parser.add_argument('w', required=True, help='Words required.')
parser.add_argument('top', type=int, default='10')


# parser.add_argument('withWeight', type=str, default='false')


class WordRecommend(Resource):
    def get(self):
        args = parser.parse_args()
        text = args['w']
        topK = int(args['top'])

        w2v = Word2Vector()
        data = {'contentbased': [item[0] for item in w2v.most_similar_global(text, top=topK)],
                'userbased': [item[0] for item in w2v.most_similar_user_search(text, top=topK)]}
        return data


class WordRecommendUnion(Resource):
    def get(self):
        args = parser.parse_args()
        text = args['w'].strip()
        topK = int(args['top'])
        if(len(text)>0):
            w2v = Word2Vector()
            # data = w2v.most_similar_global(text, half) + w2v.most_similar_user_search(text, top=topK - half)
            data1 = [item for item in w2v.most_similar_global(text, topK) if item[1] > 0.5]
            data2 = [item for item in w2v.most_similar_user_search(text, topK) if item[1] > 0.53]
            if(len(data1)==0 and len(data2)==0):
                return []
            else:
                data = data1 + data2
                data = sorted(data, key=lambda d: d[1], reverse=True)  # 按相似度排序
                data = [d[0].upper() for d in data]
                func = lambda x, y: x if y in x else x + [y]  # 对list去重
                newdata = reduce(func, [[], ] + data)
                return newdata[:topK]
        else:
            return []
