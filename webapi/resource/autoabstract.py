#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by xw on 2016/5/31


from __init__ import *

parser = reqparse.RequestParser(bundle_errors=True)
parser.add_argument('title', required=True, help='The article\'s title required.')
parser.add_argument('fulltext', required=True, help='The article\'s fulltext required.')

article_fields = {
    'title': fields.String,
    'abstract': fields.String,
}


class AutoAbstract(Resource):
    # def get(self, title):
    #     args = parser.parse_args()
    #     title = args['title']
    #     return articles[title]

    @marshal_with(article_fields)
    def post(self):
        args = parser.parse_args()
        title = args['title']
        fulltext = args['fulltext']
        if len(fulltext) < 15:
            abort(404, message="The fulltext is too short! Please contain at least 2 sentences.")
        # article = {title: fulltext}
        # articles[title] = article
        abstract = mod.get_machine_abstract(title, fulltext)
        data = {'title': title, 'abstract': abstract}
        return data

        # response = make_response(dumps(data, ensure_ascii=False))
        # response.headers['content-type'] = 'application/json; charset=UTF-8'
        # response.status_code = 200
        # return response
