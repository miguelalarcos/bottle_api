from bottle import run, route, get, post, put, debug, response, request, default_app
from core import api_get, api_post, api_put

people_resource = {
    'collection': 'people',
    'schema': {"name": {"type": "string", "required": True}, "age": {"type": "integer"}}     
}

@get('/person/<id>')
@api_get(people_resource)
def get_person(id):
    pass

@post('/people')
@api_post(people_resource)
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
