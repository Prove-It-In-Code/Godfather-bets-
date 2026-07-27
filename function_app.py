from __future__ import annotations

import azure.functions as func

from backend.app import app as flask_app

function_app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


@function_app.route(route="{*route}", methods=["GET", "POST", "OPTIONS"])
def http_entry(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    return func.WsgiMiddleware(flask_app).handle(req, context)
