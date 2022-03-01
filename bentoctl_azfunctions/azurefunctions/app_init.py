import logging
import os
import sys

from bentoml import load
from bentoml._internal.configuration.containers import DeploymentContainer
import azure.functions as func


bento_service = load("./")
logging.info("Loaded bento_service: %s", bento_service)
# Disable /metrics endpoint since promethues is not configured for use
DeploymentContainer.api_server_config.metrics.enabled.set(False)

def main(req: func.HttpRequest, context: func.Context) -> str:
    return func.AsgiMiddleware(bento_service.asgi_app).handle(req, context)
