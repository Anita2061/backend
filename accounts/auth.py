import os

import jwt
from jwt import InvalidTokenError
from rest_framework import status
from rest_framework.response import Response


def get_token_from_request(request) -> str | None:
    auth = request.headers.get("Authorization", "")
    if not auth:
        return None
    if not auth.lower().startswith("bearer "):
        return None
    return auth.split(" ", 1)[1].strip() or None


def decode_token(token: str) -> dict | None:
    secret = os.getenv("JWT_SECRET", "dev-secret-change-me")
    try:
        return jwt.decode(token, secret, algorithms=["HS256"])
    except InvalidTokenError:
        return None


def require_auth(view_func):
    def wrapped(request, *args, **kwargs):
        token = get_token_from_request(request)
        if not token:
            return Response({"detail": "Missing Authorization token"}, status=status.HTTP_401_UNAUTHORIZED)

        payload = decode_token(token)
        if not payload:
            return Response({"detail": "Invalid or expired token"}, status=status.HTTP_401_UNAUTHORIZED)

        request.auth_payload = payload
        return view_func(request, *args, **kwargs)

    return wrapped

