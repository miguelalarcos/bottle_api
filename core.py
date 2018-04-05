import os
import time
from bottle import run, route, get, post, put, debug, response, request
import datetime
from bson import json_util, objectid
import json
import jwt
from cerberus import Validator
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv(verbose=True)

db = MongoClient()['test_database']

v = Validator()

JWT_SECRET = 'secret'
JWT_ALGORITHM = 'HS256'
print(jwt.encode({'user': os.getenv('USER'), 'roles': ['user', 'admin']}, JWT_SECRET, algorithm=JWT_ALGORITHM))

# https://stackoverflow.com/questions/11875770/how-to-overcome-datetime-datetime-not-json-serializable?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
def dumps(obj):
    return json.dumps(obj, default=json_util.default)

def returns_json(f):
    def helper(*args, **kwargs):
        response.content_type = 'application/json'
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'
        ret = f(*args, **kwargs)
        return dumps(ret)
    return helper

def catching(f):
    def helper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except jwt.DecodeError:
            response.status = 500
            return {'error': 'jwt decode error'}
        except json.JSONDecodeError:
            response.status = 500
            return {'error': 'json decode error'}
        except ValidationError as e:
            response.status = 500
            return {'error': 'doc not valid: ' + str(e)}
        except ArgumentError:
            response.status = 500
            return {'error': 'argument error'}
        except RoleError:
            response.status = 500
            return {'error': 'role error'}
    return helper


def from_jwt():
    jwt_token = request.headers.get('Authorization')
    jwt_payload = jwt.decode(jwt_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    return jwt_payload.get('user'), jwt_payload.get('roles')

def current_user(): 
    jwt_token = request.headers.get('Authorization')
    jwt_payload = jwt.decode(jwt_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    return jwt_payload.get('user') 
        
def current_payload():
    payload = json.loads(request.body.read())
    return payload

class ValidationError(Exception):
    pass

class ArgumentError(Exception):
    pass

class RoleError(Exception):
    pass

def api_get(resource):
    def decorator(f):
        @returns_json
        @catching
        def helper():
            filter, limit, offset = f(**request.params)
            ret = []
            for doc in db[resource['collection']].find(filter).limit(limit).skip(offset):
                ret.append(doc)
            return ret
        return helper
    return decorator

def api_get_one(resource, role=None):
    def decorator(f):
        @returns_json
        @catching
        @has_role(role)
        def helper(id):
            user = current_user()
            response.status = 200
            ret = f(id)
            if ret:
                return ret
            else:
                return db[resource['collection']].find_one({'_id': objectid.ObjectId(id), 'owner': user})
        return helper
    return decorator

def has_role(role):
    def decorator(f):
        def helper(*args, **kwargs):
            user, roles = from_jwt()
            if role and role not in roles:
                raise RoleError()
            return f(*args, **kwargs)   
        return helper 
    return decorator

def api_post_sub(resource, role=None):
    def decorator(f):
        @returns_json
        @catching
        @has_role(role)
        def helper(id):
            user = current_user()
            payload = current_payload()
            if not v.validate(payload, resource['schema']):
                raise ValidationError(v._errors)
            ret = f(id, payload) or payload
            ret['_id'] = objectid.ObjectId()
            path = resource['path']
            db[resource['collection']].update_one({'_id': objectid.ObjectId(id), 'owner': user}, {'$push': {path: ret}})
            response.status = 200
            return ret
        return helper
    return decorator

def api_post(resource, role=None):
    def decorator(f):
        @returns_json
        @catching
        @has_role(role)
        def helper():
            payload = current_payload()
            user = current_user()

            if not v.validate(payload, resource['schema']):
                raise ValidationError(v._errors)
            payload['owner'] = user
            payload['created_at'] = time.time()
            ret = f(payload) or payload
            db[resource['collection']].insert_one(ret)
            response.status = 200
            return ret
        return helper
    return decorator

def api_put_sub(resource, role=None):
    def decorator(f):
        @returns_json
        @catching
        @has_role(role)
        def helper(id1, id2):
            user = current_user()
            payload = current_payload()
            if not v.validate(payload, resource['schema']):
                raise ValidationError(v._errors)
            ret_ = f(id1, id2, payload) or payload
            ret = {}
            path = resource['path']
            for key, value in ret_.items():
                ret[path + '.$.' + key] = value           
            db[resource['collection']].update_one({'_id': objectid.ObjectId(id1), 'owner': user, path + '._id': objectid.ObjectId(id2)}, {'$set': ret})
            response.status = 200
            return ret_
        return helper
    return decorator

def api_put(resource, role=None):
    def decorator(f):
        @returns_json
        @catching
        @has_role(role)
        def helper(id):
            payload = current_payload()
            payload.pop('user', None)
            user = current_user()

            if not v.validate(payload, resource['schema'], update=True):
                raise ValidationError(v._errors)
            payload['modified_at'] = time.time()
            ret = f(id, payload) or payload
            db[resource['collection']].update_one({'_id': objectid.ObjectId(id), 'owner': user}, {'$set': ret})
            response.status = 200
            return ret
        return helper
    return decorator

