from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.admin.service import (
    assign_patient_to_therapist,
    get_admin_assignments,
    get_admin_safety_activity,
    get_admin_summary,
    get_admin_system_metadata,
    get_admin_users,
    get_available_therapists,
    remove_patient_assignment,
)
from app.auth.dependencies import get_current_user
from app.database import get_db
from app.db_tables import User
from app.db_tables import ModerationCategorySetting
from app.db_tables import AIProviderSettings
from app.safety.rules import MODERATION_CATEGORIES, get_moderation_category_settings
from app.ai_settings import encrypt_api_key, get_ai_runtime_settings
from app.config import settings


router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)


class AssignmentRequest(BaseModel):
    therapist_id: int


class ModerationCategoryUpdate(BaseModel):
    severity: str = Field(pattern="^(low|medium|high)$")
    is_enabled: bool


class AISettingsUpdate(BaseModel):
    model: str = Field(min_length=1, max_length=150, pattern=r"^[A-Za-z0-9._:-]+$")
    is_enabled: bool
    api_key: str | None = Field(default=None, min_length=1, max_length=500)
    clear_api_key: bool = False


def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required.",
        )

    return current_user


@router.get("/summary")
def admin_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    try:
        return get_admin_summary(db)
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Admin summary could not be loaded.",
        ) from exc


@router.get("/users")
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    try:
        users = get_admin_users(db)
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Users could not be loaded.",
        ) from exc

    return {
        "users": users,
    }


@router.get("/therapists")
def list_therapists(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    try:
        therapists = get_available_therapists(db)
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Therapists could not be loaded.",
        ) from exc

    return {
        "therapists": therapists,
    }


@router.get("/assignments")
def list_assignments(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    try:
        assignments = get_admin_assignments(db)
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Patient assignments could not be loaded.",
        ) from exc

    return {
        "assignments": assignments,
    }


@router.get("/safety")
def list_safety_activity(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    try:
        activity = get_admin_safety_activity(db)
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Safety activity could not be loaded.",
        ) from exc

    return {
        "activity": activity,
    }


@router.get("/system")
def system_metadata(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    try:
        return get_admin_system_metadata(db)
    except (SQLAlchemyError, RuntimeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="System metadata could not be loaded.",
        ) from exc


@router.get("/red-flag-rules")
def list_red_flag_rules(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    try:
        return {"rules": get_moderation_category_settings(db)}
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Safety rule storage is unavailable. Apply the "
                "moderation_category_settings SQL migration, then retry."
            ),
        ) from exc


@router.get("/ai-settings")
def get_admin_ai_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    try:
        config = get_ai_runtime_settings(db)
    except (SQLAlchemyError, RuntimeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI settings storage is unavailable. Apply the ai_provider_settings SQL migration.",
        ) from exc
    return {
        "provider": config["provider"],
        "model": config["model"],
        "is_enabled": config["is_enabled"],
        "api_key_configured": config["has_api_key"],
        "api_key_source": config["api_key_source"],
        "api_key_editable": bool(settings.ai_settings_encryption_key),
    }


@router.put("/ai-settings")
def update_admin_ai_settings(
    payload: AISettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    if payload.api_key and not settings.ai_settings_encryption_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Set AI_SETTINGS_ENCRYPTION_KEY on the backend before storing an admin API key.",
        )
    if payload.api_key and payload.clear_api_key:
        raise HTTPException(status_code=422, detail="Choose a new API key or clear the override, not both.")
    try:
        row = db.query(AIProviderSettings).filter_by(id=1).first()
        if row is None:
            row = AIProviderSettings(id=1, provider="openai", model=payload.model)
            db.add(row)
        row.model = payload.model
        row.is_enabled = payload.is_enabled
        if payload.api_key:
            row.encrypted_api_key = encrypt_api_key(payload.api_key)
        elif payload.clear_api_key:
            row.encrypted_api_key = None
        db.commit()
    except (SQLAlchemyError, RuntimeError) as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI settings could not be saved. Check the database migration and encryption key configuration.",
        ) from exc
    return get_admin_ai_settings(db, current_user)


@router.put("/red-flag-rules/{category}")
def update_red_flag_rule(
    category: str,
    payload: ModerationCategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    if category not in MODERATION_CATEGORIES:
        raise HTTPException(status_code=404, detail="Unknown moderation category.")
    label, _ = MODERATION_CATEGORIES[category]
    setting = db.query(ModerationCategorySetting).filter_by(category=category).first()
    if setting is None:
        setting = ModerationCategorySetting(category=category, label=label)
        db.add(setting)
    setting.label = label
    setting.severity = payload.severity
    setting.is_enabled = payload.is_enabled
    try:
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="Safety rule could not be saved.") from exc
    return {
        "category": setting.category,
        "label": setting.label,
        "severity": setting.severity,
        "is_enabled": setting.is_enabled,
    }


@router.put("/assignments/{patient_id}")
def update_assignment(
    patient_id: int,
    payload: AssignmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    try:
        assignment = assign_patient_to_therapist(
            db,
            patient_id,
            payload.therapist_id,
        )
    except SQLAlchemyError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Patient assignment could not be updated.",
        ) from exc

    if assignment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active patient or therapist not found.",
        )

    return assignment


@router.delete("/assignments/{patient_id}")
def delete_assignment(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    try:
        removed = remove_patient_assignment(
            db,
            patient_id,
        )
    except SQLAlchemyError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Patient assignment could not be removed.",
        ) from exc

    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient assignment not found.",
        )

    return {
        "patient_id": patient_id,
        "removed": True,
    }
