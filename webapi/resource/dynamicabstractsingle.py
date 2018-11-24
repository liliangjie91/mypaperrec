#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by xw on 2016/6/29 


from __init__ import *

parser = reqparse.RequestParser(bundle_errors=True)
parser.add_argument('query', required=True)
parser.add_argument('fulltext', required=True, help='The article\'s fulltext required.')
parser.add_argument('mark', type=str, default='true')

article_fields = {
    'query': fields.String,
    'abstract': fields.String,
}


class DynamicAbstractSingle(Resource):
    @marshal_with(article_fields)
    def post(self):
        args = parser.parse_args()
        query = args['query']
        fulltext = args['fulltext']
        mark = args['mark'].lower()
        need_mark = True
        if mark != 'true':
            need_mark = False
        if len(fulltext) < 15:
            abort(404, message="The fulltext is too short! Please contain at least 2 sentences.")
        abstract, marked_query = mod.get_abstract4qa(query, fulltext, need_mark)
        data = {'query': marked_query, 'abstract': abstract}
        return data
