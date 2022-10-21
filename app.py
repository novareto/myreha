from minicli import cli, run


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


def create_web_app(users_sources):
    import pathlib
    import http_session_file
    from reha.app import Application
    from reha.app.database import DatabaseConnection
    from knappe.auth import WSGISessionAuthenticator
    from knappe.middlewares import auth
    from knappe.middlewares.session import HTTPSession
    from pymongo import MongoClient

    authentication = auth.Authentication(
        authenticator=WSGISessionAuthenticator(users_sources),
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

    app = Application(
        DatabaseConnection(MongoClient()),
        middlewares=(session, authentication)
    )
    return app


@cli
def http(debug: bool = False):
    import asyncio
    import pathlib
    from aiowsgi import create_server
    import reha.browser
    import backend.browser
    from reha.ui import subscribers
    from reha.models import models
    from horseman.mapping import Mapping
    from knappe.blueprint import apply_blueprint
    from knappe.testing import DictSource


    configure_logging(debug)


    app = create_web_app([
        DictSource({"user": "user"})
    ])
    apply_blueprint(reha.browser.router, app.router)
    apply_blueprint(subscribers, app.subscribers)
    apply_blueprint(models, app.models)
    app.dbconn.initialize(app.models)

    admin = create_web_app([
        DictSource({"admin": "admin"})
    ])
    apply_blueprint(reha.browser.router, admin.router)
    apply_blueprint(backend.browser.router, admin.router)
    apply_blueprint(subscribers, admin.subscribers)
    apply_blueprint(models, admin.models)
    app.dbconn.initialize(admin.models)

    root = Mapping({
        "/": app,
        "/admin": admin
    })

    loop = asyncio.new_event_loop()
    wsgi_server = create_server(root, loop=loop, port=8000)

    try:
        wsgi_server.run()
    finally:
        loop.stop()


if __name__ == '__main__':
    run()
