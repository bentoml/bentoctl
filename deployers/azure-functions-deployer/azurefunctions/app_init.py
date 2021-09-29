import os
import logging
import azure.functions as func  # pylint: disable=import-error, no-name-in-module

from bentoml.saved_bundle import load_from_dir
from bentoml.types import HTTPRequest
from flask import Flask, request, Response

bento_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
svc = load_from_dir(bento_path)


class BentoAzureServer:
    def __init__(self, bento_service, app_name=None):
        app_name = bento_service.name if app_name is None else app_name

        self.bento_service = bento_service
        self.app = Flask(app_name)
        self._setup_routes()

    def _setup_routes(self):
        # health check view function
        def ping_view_func():
            return Response(response="\n", status=200, mimetype="application/json")

        self.app.add_url_rule(
            "/ping", 'healthz', ping_view_func, methods=["GET"]
        )

        for api in self.bento_service.inference_apis:

            # pass request from Wsgi to Bentoml api service
            def passthrough_function():
                req = HTTPRequest.from_flask_request(request)
                response = api.handle_request(req)
                return response.to_flask_response()

            self.app.add_url_rule(
                "/" + api.route, api.name, passthrough_function, methods=["POST"]
            )


bento_server = BentoAzureServer(svc)


def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    logging.warning(req.headers.get('Content-Type'))
    logging.warning(req.get_body())
    return func.WsgiMiddleware(bento_server.app.wsgi_app).handle(req, context)
