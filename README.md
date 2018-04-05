This is what you can do with this library:

```python
from bottle import run, route, get, post, put, debug, response, request, default_app
from core import api_get, api_get_one, api_post, api_put, api_post_sub, api_put_sub, ArgumentError

people_resource = {
    'collection': 'people',
    'schema': {"name": {"type": "string", "required": True}, "age": {"type": "integer"}}     
}

comments_resource = {
    'collection': 'people',
    'path': 'comments',
    'schema': {'text': {'type': 'string'}}
}

@get('/person/<id>')
@api_get_one(people_resource)
def get_person(id): # this function is never called
    pass

@get('/people')
@api_get(people_resource)
def get_people(name=None, **kwargs):
    if name is None:
        raise ArgumentError()
    return {'name': {'$regex':'^'+name}}, 5, 0

@post('/people')
@api_post(people_resource, role='admin')
def post_people(payload):
    payload['mr_name'] = 'Mr. ' + payload['name']
    return payload

@put('/person/<id>')
@api_put(people_resource)
def put_person(id, payload):
    pass

@post('/person/<id>/comments')
@api_post_sub(comments_resource)
def post_comment(id, payload):
    pass

@put('/person/<id1>/comment/<id2>')
@api_put_sub(comments_resource)
def put_comment(id1, id2, payload):
    pass

application = default_app()
if __name__ == '__main__':
    debug(True)
    run(reloader=True)
```
