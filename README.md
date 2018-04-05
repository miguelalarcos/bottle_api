This is what you can do with this library:

```python
from bottle import run, route, get, post, put, debug, response, request, default_app
from core import api_get, api_get_one, api_post, api_put, ArgumentError

people_resource = {
    'collection': 'people',
    'schema': {"name": {"type": "string", "required": True}, "age": {"type": "integer"}}     
}

@get('/person/<id>')
@api_get_one(people_resource)
def get_person(id):
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
    pass

@put('/person/<id>')
@api_put(people_resource)
def put_person(id, payload):
    pass

application = default_app()
if __name__ == '__main__':
    debug(True)
    run(reloader=True)
```