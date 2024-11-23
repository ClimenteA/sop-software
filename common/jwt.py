import os
import jwt
from datetime import datetime, timedelta
from .collections import get_collection

SECRET = os.environ["SECRET"]


async def get_token_for_user_id(
    user_id: str,
    users_col: str,
    blacktoken_col: str,
    expire_days: int = 730,
):
    expire = (datetime.utcnow() + timedelta(days=expire_days)).isoformat()
    encoded_jwt = jwt.encode(
        {
            "user_id": user_id,
            "expire": expire,
            "users_col": users_col,
            "blacktoken_col": blacktoken_col,
        },
        SECRET,
    )
    return encoded_jwt


async def get_user_id_from_token(token: str | None, return_user_id: bool = True):
    try:
        if token is None:
            return None

        decoded_jwt = jwt.decode(token, SECRET, algorithms=["HS256"])
        if datetime.utcnow() >= datetime.fromisoformat(decoded_jwt["expire"]):
            return None

        users_col = get_collection(decoded_jwt["users_col"])
        user_exists = await users_col.count({"user_id": decoded_jwt["user_id"]})
        if not user_exists:
            return None

        blacktoken_col = get_collection(decoded_jwt["blacktoken_col"])
        blacklisted_token = await blacktoken_col.find_one(
            {"token": token, "expire": decoded_jwt["expire"]}
        )
        if blacklisted_token:
            return None

        if return_user_id:
            return decoded_jwt["user_id"]
        return decoded_jwt
    except Exception:
        return None


async def blacklist_token(token: str | None):
    try:
        decoded_jwt = await get_user_id_from_token(token, return_user_id=False)
        if decoded_jwt is None:
            return None
        col = get_collection(decoded_jwt["blacktoken_col"])
        await col.insert_one({"token": token, "expire": decoded_jwt["expire"]})
        await col.delete_many({"expire": {"$lt": datetime.utcnow().isoformat()}})
        return True
    except Exception:
        return None
