import os
import azure.functions as func  # pylint: disable=import-error, no-name-in-module

from bentoml.server.api_server import BentoAPIServer
from bentoml.saved_bundle import load_from_dir

bento_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
svc = load_from_dir(bento_path)

bento_server = BentoAPIServer(svc)


def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    return func.WsgiMiddleware(bento_server.app.wsgi_app).handle(req, context)
