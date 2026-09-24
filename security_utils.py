from cryptography.fernet import Fernet, InvalidToken

def get_fernet(key: str):
    if not key:
        return None
    try:
        return Fernet(key.encode())
    except Exception:
        return None

def encrypt_value(value: str, key: str) -> str:
    if not value:
        return ""
    f = get_fernet(key)
    if not f:
        raise RuntimeError("CREDENTIAL_ENCRYPTION_KEY is missing or invalid.")
    return f.encrypt(value.encode()).decode()

def decrypt_value(value: str, key: str) -> str:
    if not value:
        return ""
    f = get_fernet(key)
    if not f:
        raise RuntimeError("CREDENTIAL_ENCRYPTION_KEY is missing or invalid.")
    try:
        return f.decrypt(value.encode()).decode()
    except InvalidToken as exc:
        raise RuntimeError("Stored credential cannot be decrypted with the current encryption key.") from exc
