import os

import asyncio

from aiohttp import web
from aiohttp_session import get_session, session_middleware
from aiohttp_session.cookie_storage import EncryptedCookieStorage

import aiohttp_jinja2
from aiohttp_jinja2 import template, render_template
import jinja2

import base64
import cryptography

#
# setup
#
enc_fernet_key = cryptography.fernet.Fernet.generate_key()
fernet = cryptography.fernet.Fernet(enc_fernet_key)
fernet_key = base64.urlsafe_b64decode(enc_fernet_key)

app = web.Application(
    middlewares=[
        session_middleware(
            EncryptedCookieStorage(fernet_key)
        )
    ]
)

aiohttp_jinja2.setup(
    app,
    loader=jinja2.FileSystemLoader(os.path.abspath('templates')),
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
@route('GET', '/signin')
@template('signin.html')
async def signin(request):
    return {}

@route('POST', '/signin')
async def signin(request):
    username = request.match_info.get('username', None)
    password = request.match_info.get('password', None)

    if username == 'admin' and password == 'admin':
        return web.HTTPFound('/home')
    else:
        return web.HTTPFound('/signin')

@route('GET', '/home')
@template('home.html')
async def home(request):
    return {}

@route('POST', '/signout')
async def signin(request):
    return {}

async def init(loop):
    srv = await loop.create_server(
        app.make_handler(),
        '0.0.0.0',
        8080,
    )

    return srv

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))

try:
    loop.run_forever()
except KeyboardInterrupt:
    loop.close()
