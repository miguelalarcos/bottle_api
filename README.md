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

@api_get_one('/person/<id>', people_resource)
def get_person(id): # this function is never called
    pass

@api_get('/people', people_resource)
def get_people(name=None, **kwargs):
    if name is None:
        raise ArgumentError()
    return {'name': {'$regex':'^'+name}}, 5, 0

@api_post('/people', people_resource, role='admin')
def post_people(payload):
    payload['mr_name'] = 'Mr. ' + payload['name']
    return payload

@api_put('/person/<id>', people_resource)
def put_person(id, payload):
    pass

@api_post_sub('/person/<id>/comments', comments_resource)
def post_comment(id, payload):
    pass

@api_put_sub('/person/<id1>/comment/<id2>', comments_resource)
def put_comment(id1, id2, payload):
    pass

application = default_app()
if __name__ == '__main__':
    debug(True)
    run(reloader=True)

```
