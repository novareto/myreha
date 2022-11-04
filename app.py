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


def create_web_app(user_sources):
    import pathlib
    from reha.app import Application, auth as jwt
    from reha.app.database import DatabaseConnection
    from roughrider.cors.policy import CORSPolicy
    from knappe.middlewares import auth
    from pymongo import MongoClient

    jwt_service = jwt.make_jwt_service('my.key')
    authentication = auth.Authentication(
        authenticator=jwt.JWTAuthenticator(
            jwt_service,
            sources=user_sources
        ),
        filters=(
            jwt.options_method_filter,
            auth.security_bypass({"/login"}),
            jwt.authentified_only
        )
    )

    app = Application(
        DatabaseConnection(MongoClient()),
        middlewares=(authentication,)
    )
    return app


@cli
def http(debug: bool = False):
    import asyncio
    import pathlib
    from aiowsgi import create_server
    import backend.browser
    from reha.ui import subscribers
    from reha.models import models
    from horseman.mapping import Mapping
    from knappe.blueprint import apply_blueprint
    from knappe.testing import DictSource

    configure_logging(debug)

    admin = create_web_app([
        DictSource({"admin": "admin"})
    ])
    apply_blueprint(backend.browser.router, admin.router)
    apply_blueprint(subscribers, admin.subscribers)
    apply_blueprint(models, admin.models)
    admin.dbconn.initialize(admin.models)

    loop = asyncio.new_event_loop()
    wsgi_server = create_server(admin, loop=loop, port=8000)

    try:
        wsgi_server.run()
    finally:
        loop.stop()


if __name__ == '__main__':
    run()
