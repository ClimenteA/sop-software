from . import errors
from .password import encrypt


def get_lower_email(email: str):
    if email.count("@") != 1 and email.count(".") < 1 and len(email) > 3:
        raise errors.InvalidEmailException
    return email.lower()


def get_encrypted_password(password: str):
    if len(password) < 6:
        raise errors.PasswordInsecureException
    return encrypt(password)
