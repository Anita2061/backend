import os
from datetime import datetime, timedelta, timezone

import jwt


def create_access_token(*, user_id: str, email: str) -> str:
    secret = os.getenv("JWT_SECRET", "dev-secret-change-me")
    exp_minutes = int(os.getenv("JWT_EXPIRES_MINUTES", "60"))
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "email": email,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=exp_minutes)).timestamp()),
    }
    return jwt.encode(payload, secret, algorithm="HS256")

