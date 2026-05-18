from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.runner import get_db_connection

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    conn = get_db_connection()
    row = conn.execute(
        "SELECT token FROM api_keys WHERE token = ?", (token,)
    ).fetchone()
    conn.close()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
    return token