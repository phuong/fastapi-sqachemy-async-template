from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from core.context import request_context


class ContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        context_token = request_context.init()
        try:
            response = await call_next(request)
        finally:
            request_context.reset(context_token)
        return response
