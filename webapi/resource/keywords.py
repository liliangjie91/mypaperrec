#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by xw on 2017/1/3

import nlp
from __init__ import *

parser = reqparse.RequestParser(bundle_errors=True)
parser.add_argument('text', required=True, help='Text required.')
parser.add_argument('top', type=int, default='10')
parser.add_argument('withWeight', type=str, default='false')


class Keywords(Resource):
    def post(self):
        args = parser.parse_args()
        text = args['text']
        topK = args['top']
        withWeight = True
        if args['withWeight'].lower() != 'true':
            withWeight = False
        ba = nlp.Basis()
        keywords = ba.getkeywords(text, int(topK), withWeight)
        if withWeight is True:
            data = [{'tag': keyword[0], 'weight': keyword[1]} for keyword in keywords]
            return data
        else:
            return keywords
