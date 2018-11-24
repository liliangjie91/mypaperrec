#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by xw on 2017/1/4 

import abstract4section
from __init__ import *

parser = reqparse.RequestParser(bundle_errors=True)
parser.add_argument('text', required=True, help='Text required.')


class Abstract4Xml(Resource):
    def post(self):
        args = parser.parse_args()
        xmltext = args['text']
        abstract = abstract4section.abstract(xmltext)
        data = [{'chapter': abs[0], 'abstract': abs[1]} for abs in abstract]
        return data
