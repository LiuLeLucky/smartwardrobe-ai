from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode["exp"] = expire
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


if __name__ == "__main__":
    print("=" * 50)
    print("1. Password Hashing")
    print("=" * 50)
    password = "mysecretpassword"
    hashed = get_password_hash(password)
    print(f"  Original : {password}")
    print(f"  Hashed   : {hashed}")
    print(f"  Verified : {verify_password(password, hashed)}")
    print(f"  Wrong pw : {verify_password('wrongpassword', hashed)}")

    print()
    print("=" * 50)
    print("2. JWT Token")
    print("=" * 50)
    token = create_access_token({"sub": "user@example.com"})
    print(f"  Token    : {token}")

    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    print(f"  Subject  : {payload['sub']}")
    print(f"  Expires  : {datetime.fromtimestamp(payload['exp'], tz=timezone.utc)}")

    print()
    print("=" * 50)
    print("3. Custom Expiry")
    print("=" * 50)
    short_token = create_access_token({"sub": "test@example.com"}, expires_delta=timedelta(minutes=5))
    short_payload = jwt.decode(short_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    print(f"  Subject  : {short_payload['sub']}")
    print(f"  Expires  : {datetime.fromtimestamp(short_payload['exp'], tz=timezone.utc)}")
    print()
    print("All checks passed.")
