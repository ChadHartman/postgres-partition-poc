#!/usr/bin/env python3

'''
This module provides the application's HTTP Server.
'''

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from app.logrepo import LogRepo


class AppServer(HTTPServer):
    '''
    The application's HTTP Server
    '''

    def __init__(self, host: str, port: int, repo: LogRepo):
        super().__init__((host, port), AppRequestHandler)
        self.host: str = host
        self.port: int = port
        self.logrepo = repo

    def serve_forever(self) -> None:
        print(f'Server started http://{self.host}:{self.port}')
        self.logrepo.insertlog('Server started.')
        super().serve_forever()

    def server_close(self) -> None:
        print('Server stopped.')
        super().server_close()
        self.logrepo.insertlog('Server stopped.')


class AppRequestHandler(BaseHTTPRequestHandler):
    '''
    The application's HTTP Request handler.
    '''

    @property
    def _server(self) -> AppServer:
        # Created for typing
        return self.server

    def _httprespond(self, status: int, body: dict) -> None:
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        res = json.dumps(body, indent=2)
        self.wfile.write(bytes(res, 'utf-8'))

    def _respondnotfound(self):
        self._httprespond(404, {
            'error': f'Unknown resource "{self.path}"'
        })

    def do_GET(self) -> None:

        res = {}

        if self.path == '/logs':
            res['logs'] = [str(l) for l in self._server.logrepo.fetchlogs()]
        elif self.path == '/tables':
            res['tables'] = self._server.logrepo.fetchtables()
        else:
            self._respondnotfound()
            return

        self._httprespond(200, res)

    def do_DELETE(self) -> None:

        res = {}

        if self.path == '/tables':
            res['dropped_tables'] = self._server.logrepo.prunepartitions()
        else:
            self._respondnotfound()
            return

        self._httprespond(200, res)
