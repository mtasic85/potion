import os
import pickle
from urllib.parse import urlparse, parse_qsl

import asyncio

from aiohttp import web
from aiohttp import MultiDict
from aiohttp.multipart import MultipartReader

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

if os.path.exists('fernet_key'):
    with open('fernet_key', 'rb') as f:
        fernet_key = pickle.load(f)
else:
    enc_fernet_key = cryptography.fernet.Fernet.generate_key()
    fernet = cryptography.fernet.Fernet(enc_fernet_key)
    fernet_key = base64.urlsafe_b64decode(enc_fernet_key)

    with open('fernet_key', 'wb') as f:
        pickle.dump(fernet_key, f)

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
@route('GET', '/')
async def index(request):
    session = await get_session(request)
    
    if session.get('username', None):
        raise web.HTTPFound('/home')
    else:
        raise web.HTTPFound('/signin')

@route('GET', '/signin')
@template('signin.html')
async def signin(request):
    session = await get_session(request)
    
    if session.get('username', None):
        raise web.HTTPFound('/signout')

    return {}

@route('POST', '/signin')
async def signin(request):
    print('signin')
    session = await get_session(request)
    data = await request.payload.read()
    data = data.decode('utf-8')
    post_params = MultiDict(parse_qsl(data))

    username = post_params.get('username', None)
    password = post_params.get('password', None)

    if username == 'admin' and password == 'admin':
        print((username, password))
        session['username'] = username
        raise web.HTTPFound('/home')
    else:
        try:
            del session['username']
        except KeyError as e:
            pass

        raise web.HTTPFound('/signin')

@route('GET', '/home')
@template('home.html')
async def home(request):
    print('home')
    session = await get_session(request)

    if not session.get('username', None):
        raise web.HTTPFound('/signout')

    return {}

@route('GET', '/signout')
async def signout(request):
    print('signout')
    session = await get_session(request)
    
    try:
        del session['username']
    except KeyError as e:
        pass

    raise web.HTTPFound('/signin')

@route('POST', '/signout')
async def signout(request):
    print('signout')
    session = await get_session(request)
    
    try:
        del session['username']
    except KeyError as e:
        pass

    raise web.HTTPFound('/signin')

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
