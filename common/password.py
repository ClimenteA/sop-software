import hashlib


def encrypt(value: str):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def valid(hash: str, value: str):
    return hash == encrypt(value)
