import json
from datetime import datetime, timezone
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

EXCLUDED_PREFIXES = ("/docs", "/redoc", "/openapi.json", "/auth/login", "/auth/refresh")


class ResponseEnvelopeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)

        path = request.url.path
        if path.startswith(EXCLUDED_PREFIXES):
            return response

        if response.status_code == 204:
            return response

        content_type = response.headers.get("content-type", "")
        if "application/json" not in content_type:
            return response

        body = b""
        async for chunk in response.body_iterator:
            body += chunk

        if response.status_code >= 400:
            return Response(content=body, status_code=response.status_code, headers=dict(response.headers), media_type=response.media_type)

        try:
            data = json.loads(body) if body else None
        except json.JSONDecodeError:
            return Response(content=body, status_code=response.status_code, headers=dict(response.headers), media_type=response.media_type)

        envelope = {
            "statusCode": response.status_code,
            "message": "Success",
            "data": data,
            "error": None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "path": path,
        }
        new_body = json.dumps(envelope).encode("utf-8")
        headers = dict(response.headers)
        headers["content-length"] = str(len(new_body))
        return Response(content=new_body, status_code=response.status_code, headers=headers, media_type="application/json")