#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by xw on 2016/5/31

from flask import Flask
from flask_restful import reqparse, abort, Api, Resource

# app = Flask(__name__)
# api = Api(app)

TODOS = {
    'todo1': {'task': 'build an API'},
    'todo2': {'task': 'aaaaaaa'},
    'todo3': {'task': 'profit!'},
}


def abort_if_todo_doesnt_exist(todo_id):
    if todo_id not in TODOS:
        abort(404, message="Todo {} doesn't exist".format(todo_id))


parser = reqparse.RequestParser()
parser.add_argument('task')


# To do
# shows a single to do item and lets you delete a to do item
class Todo(Resource):
    def get(self, todo_id):
        abort_if_todo_doesnt_exist(todo_id)
        return TODOS[todo_id]

    def delete(self, todo_id):
        abort_if_todo_doesnt_exist(todo_id)
        del TODOS[todo_id]
        return '', 204

    def put(self, todo_id):
        args = parser.parse_args()
        task = {'task': args['task']}
        TODOS[todo_id] = task
        return task, 201


# TodoList
# shows a list of all todos, and lets you POST to add new tasks
class TodoList(Resource):
    def get(self):
        return TODOS

    def post(self):
        args = parser.parse_args()
        todo_id = int(max(TODOS.keys()).lstrip('todo')) + 1
        todo_id = 'todo%i' % todo_id
        TODOS[todo_id] = {'task': args['task']}
        return TODOS[todo_id], 201


# test
class Test(Resource):
    def get(self):
        return {'test': 'test'}


        # if __name__ == '__main__':
        #     app.run(debug=True)
