#!/usr/bin/env python3
import os
from app.server import AppServer
from app.logrepo import LogRepo


def main():

    dbhost = os.getenv('DB_HOST', 'localhost')
    dbport = int(os.getenv('DB_PORT', '5432'))
    dbuser = os.getenv('DB_USERNAME', 'postgres')
    dbpass = os.getenv('DB_PASSWORD', 'password')
    host = os.getenv('APP_HOST', 'localhost')
    port = int(os.getenv('APP_PORT', '8080'))

    repo = LogRepo(dbhost, dbport, dbuser, dbpass)
    server = AppServer(host, port, repo)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

    server.server_close()


if __name__ == '__main__':
    main()
