from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy.orm import Session

from app.config import settings
from app.db_tables import AIProviderSettings


def _cipher() -> Fernet:
    if not settings.ai_settings_encryption_key:
        raise RuntimeError("AI_SETTINGS_ENCRYPTION_KEY is not configured.")
    try:
        return Fernet(settings.ai_settings_encryption_key.encode("ascii"))
    except (ValueError, UnicodeEncodeError) as exc:
        raise RuntimeError("AI_SETTINGS_ENCRYPTION_KEY is invalid.") from exc


def get_ai_runtime_settings(db: Session | None = None) -> dict:
    row = db.query(AIProviderSettings).filter_by(id=1).first() if db else None
    api_key = settings.open_api_key
    if row and row.encrypted_api_key:
        try:
            api_key = _cipher().decrypt(row.encrypted_api_key.encode("ascii")).decode("utf-8")
        except (InvalidToken, UnicodeDecodeError) as exc:
            raise RuntimeError("The stored AI API key could not be decrypted.") from exc
    return {
        "provider": "openai",
        "model": row.model if row else (settings.openapi_model or "gpt-6-luna"),
        "is_enabled": row.is_enabled if row else True,
        "api_key": api_key,
        "has_api_key": bool(api_key),
        "api_key_source": "admin" if row and row.encrypted_api_key else "environment",
    }


def encrypt_api_key(api_key: str) -> str:
    return _cipher().encrypt(api_key.encode("utf-8")).decode("ascii")
