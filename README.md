This is what you can do with this library:

```python
from bottle import run, route, get, post, put, debug, response, request, default_app
from core import api_get, api_get_one, api_post, api_put, api_post_sub, api_put_sub, ArgumentError, current_user

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
def get_person(id, doc):
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

#api_get_one is public, i.e. does not check if you are the owner of the doc
@api_get_one('/comments-of-person/<id>', people_resource)
def get_comments(id, doc):
    user = current_user()
    lista = [comment for comment in doc['comments'] if comment['writer'] == user or comment['respond_to'] == user]
    doc['comments'] = lista
    return doc

application = default_app()
if __name__ == '__main__':
    debug(True)
    run(reloader=True)
    run()
```

gets are public
put only does if you are the owner of the doc
post add an owner field