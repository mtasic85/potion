from aiohttp import web
import aiohttp_jinja2
from aiohttp_jinja2 import template, render_template
import jinja2

#
# setup
#
app = web.Application()

aiohttp_jinja2.setup(
    app,
    loader=jinja2.DictLoader({
        'template1': '<html><body><h1>{{message}}, {{name}}</h1></body></html>',
    }),
)

def route(method_type, method_route):
    def f(callback):
        def handler(request):
            return callback(request)

        app.router.add_route(method_type, method_route, handler)

    return f

#
# example
#
@route('GET', '/welcome/{name}')
async def welcome(request):
    name = request.match_info.get('name', 'Anonymous')
    text = 'Welcome, ' + name
    return web.Response(body=text.encode('utf-8'))

@route('GET', '/hi/{name}')
async def hi(request):
    name = request.match_info.get('name', 'Anonymous')
    return render_template('template1', request, {'message': 'Hi', 'name': name})

@route('GET', '/hello/{name}')
@template('template1')
async def hello(request):
    name = request.match_info.get('name', 'Anonymous')
    return {'message': 'Hello', 'name': name}

web.run_app(app)
