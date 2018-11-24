#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by xw on 2016/5/31 

from __init__ import *

from flask import Flask
from flask_cors import CORS
from flask_restful import Api

from webapi.resource.test import Todo
from webapi.resource.test import TodoList

from webapi.resource.test import Test

from webapi.resource.abstract4xml import Abstract4Xml
from webapi.resource.autoabstract import AutoAbstract
from webapi.resource.dynamicabstract import DynamicAbstract
from webapi.resource.dynamicabstractsingle import DynamicAbstractSingle
from webapi.resource.keywords import Keywords
from webapi.resource.wordrecommend import WordRecommend, WordRecommendUnion

app = Flask(__name__)
# 应用配置文件配置 “BUNDLE_ERRORS”
# app.config['BUNDLE_ERRORS'] = True
# cors支持
CORS(app)
api = Api(app)

from flask import make_response, current_app
from json import dumps


# 强制输出utf-8
@api.representation('application/json')
def output_json(data, code, headers=None):
    """Makes a Flask response with a JSON encoded body"""

    # If we're in debug mode, and the indent is not set, we set it to a
    # reasonable value here.  Note that this won't override any existing value
    # that was set.  We also set the "sort_keys" value.
    local_settings = {'ensure_ascii': False}
    if current_app.debug:
        local_settings.setdefault('indent', 4)
        local_settings.setdefault('sort_keys', True)

    # We also add a trailing newline to the dumped JSON if the indent value is
    # set - this makes using `curl` on the command line much nicer.
    # dumped = dumps(data, **local_settings).encode('utf-8')
    dumped = dumps(data, ensure_ascii=False).encode('utf-8')

    if 'indent' in local_settings:
        dumped += '\n'

    resp = make_response(dumped, code)
    resp.headers.extend(headers or {})
    return resp


##
## Actually setup the Api resource routing here
##
# api.add_resource(TodoList, '/api/test/todos')
api.add_resource(Todo, '/api/test/todos/<todo_id>')

api.add_resource(Test, '/api/test2')

api.add_resource(Keywords, '/api/keywords/tfidf')

api.add_resource(AutoAbstract, '/api/abstract/static/s')
api.add_resource(DynamicAbstract, '/api/abstract/dynamic/m')
api.add_resource(DynamicAbstractSingle, '/api/abstract/dynamic/s')
api.add_resource(Abstract4Xml, '/api/abstract/xml')

api.add_resource(WordRecommend, '/api/recommendations/words')
api.add_resource(WordRecommendUnion, '/api/recommendations/words/union')

if __name__ == '__main__':
    app.run(debug=False)
    #app.debug=False
    #app.run(host='0.0.0.0')