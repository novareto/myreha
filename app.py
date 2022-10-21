from minicli import cli, run
from pymongo import MongoClient


def configure_logging(debug=False):
    import sys
    import logging

    log_level = logging.DEBUG if debug else logging.WARNING
    stream_handler = logging.StreamHandler(stream=sys.stdout)
    stream_handler.setLevel(log_level)
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s %(levelname)s %(module)s %(funcName)s %(message)s',
        handlers=[stream_handler]
    )


def create_web_app():
    from knappe.auth import WSGISessionAuthenticator
    from knappe.middlewares import auth
    from knappe.middlewares.session import HTTPSession


    authentication = auth.Authentication(
        authenticator=WSGISessionAuthenticator([
            DictSource({"admin": "admin"})
        ]),
        filters=(
            auth.security_bypass({"/login"}),
            auth.secured(path="/login")
        )
    )

    session = HTTPSession(
        store=http_session_file.FileStore(pathlib.Path('./session'), 300),
        secret='secret',
        salt='salt',
        cookie_name='session',
        secure=False,
        TTL=300
    )


    app = Kavalkade(

        models=models.models,
        router=controllers.router,
        websockets=controllers.websockets,
    )
    return app


@cli
def http(debug: bool = False):
    import asyncio
    import pathlib
    from aiowsgi import create_server

    configure_logging(debug)

    app = create_web_app()
    loop = asyncio.new_event_loop()
    app.services.bind(loop)
    wsgi_server = create_server(app, loop=loop, port=8000)

    try:
        app.services.start()
        wsgi_server.run()
    except:
        loop.run_until_complete(app.services.stop())
    finally:
        loop.stop()


if __name__ == '__main__':
    run()
