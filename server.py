#!/usr/bin/env python

# TODO: pretty up template, configurable time params

import json
import os
import socket
import time


from gevent import monkey; monkey.patch_all()
from gevent.wsgi import WSGIServer
import gevent
import web

urls = (
    '/(?P<path>.*)', 'index'
    )

render = web.template.render(
    os.path.abspath(__file__).replace('server.py', 'templates'))

class index:
    def GET(self, path):
        host = web.ctx.environ['HTTP_HOST']
        cookie = web.cookies().get('noprocrast')
        if not cookie:
            cookie = {}
        else:
            cookie = json.loads(cookie)
        allow = False
        record = cookie.get(host)
        if record:
            if record['e']:
                # Host is currently enabled, check to see if we should disable
                if record['t'] < int(time.time()):
                    # Disable for the next 3 hours
                    record['e'] = False
                    record['t'] = int(time.time()) + 10800
                else:
                    allow = True
            else:
                # Host is currently disabled, check to see if we should enable
                if record['t'] < int(time.time()):
                    # Enable for the next 15 minutes
                    record['e'] = True
                    record['t'] = int(time.time()) + 900
        else:
            allow = True
            record = {'e': True,
                      't': int(time.time()) + 900}
        cookie[host] = record
        web.setcookie('noprocrast', json.dumps(cookie), expires=31557600)
        if allow:
            ip = socket.gethostbyname(host)
            raise web.seeother('http://%s/%s' % (ip, path))
        else:
            return render.index()

if __name__ == '__main__':
    application = web.application(urls, globals()).wsgifunc()
    print 'Serving on 9099...'
    WSGIServer(('localhost', 9099), application).serve_forever()
