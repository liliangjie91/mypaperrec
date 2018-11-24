#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by xw on 2016/6/22 


from __init__ import *


parser = reqparse.RequestParser(bundle_errors=True)
parser.add_argument('q', required=True, help="Query cannot be blank!")

article_fields = {
    'filename': fields.String,
    'score': fields.Float,
    'abstract': fields.String
}


class DynamicAbstract(Resource):
    @marshal_with(article_fields)
    def get(self):
        args = parser.parse_args()
        q = args['q']
        sql = u"SELECT top 50 * FROM CJFDTOTAL where SMARTS = '" + q + u"' order by FFD"
        abstract = mod.dynamic_abstract_from_query(sql)
        json = [{'filename': line[0], 'score': line[1], 'abstract': line[2]} for line in abstract]
        # print abstract
        return json
