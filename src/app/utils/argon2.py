from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

def hash_password(password: str) -> str:
    ph = PasswordHasher()
    return ph.hash(password)

def verify_password(hashed_password: str, plain_password: str) -> bool:
    ph = PasswordHasher()
    try:
        ph.verify(hashed_password, plain_password)
        return True
    except VerifyMismatchError:
        return False