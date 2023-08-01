from cryptography.fernet import Fernet

from settings import ENCRYPTION_KEY


def encrypt(message: str) -> str:
    return Fernet(ENCRYPTION_KEY.encode()).encrypt(message.encode()).decode()


def decrypt(message: str) -> str:
    return Fernet(ENCRYPTION_KEY.encode()).decrypt(message.encode()).decode()
