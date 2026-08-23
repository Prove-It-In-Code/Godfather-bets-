from __future__ import annotations

import azure.functions as func

from backend.app import app as flask_app

function_app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)
wsgi_middleware = func.WsgiMiddleware(flask_app)


@function_app.route(route="{*route}", methods=["GET", "POST", "OPTIONS"])
def http_entry(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    return wsgi_middleware.handle(req, context)
