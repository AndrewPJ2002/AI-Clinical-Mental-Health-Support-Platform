
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.db_tables import ConsentAcknowledgement, User


router = APIRouter(prefix="/consent", tags=["Consent"])

# Increment this value whenever the consent disclosure materially changes.
CURRENT_DISCLOSURE_VERSION = "v1"


class ConsentRequest(BaseModel):
    disclosure_version: str


@router.get("/status")
def get_consent_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    acknowledgement = (
        db.query(ConsentAcknowledgement)
        .filter(
            ConsentAcknowledgement.user_id == current_user.id,
            ConsentAcknowledgement.disclosure_version
            == CURRENT_DISCLOSURE_VERSION,
        )
        .order_by(ConsentAcknowledgement.acknowledged_at.desc())
        .first()
    )

    return {
        "required": acknowledgement is None,
        "disclosure_version": CURRENT_DISCLOSURE_VERSION,
        "acknowledged_at": (
            acknowledgement.acknowledged_at.isoformat()
            if acknowledgement is not None
            else None
        ),
    }


@router.post("/acknowledge")
def acknowledge_consent(
    payload: ConsentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.disclosure_version != CURRENT_DISCLOSURE_VERSION:
        raise HTTPException(
            status_code=409,
            detail="The disclosure version has changed. Please review the current disclosure.",
        )

    existing = (
        db.query(ConsentAcknowledgement)
        .filter(
            ConsentAcknowledgement.user_id == current_user.id,
            ConsentAcknowledgement.disclosure_version
            == CURRENT_DISCLOSURE_VERSION,
        )
        .first()
    )

    if existing is not None:
        return {
            "success": True,
            "disclosure_version": CURRENT_DISCLOSURE_VERSION,
            "acknowledged_at": existing.acknowledged_at.isoformat(),
        }

    acknowledgement = ConsentAcknowledgement(
        user_id=current_user.id,
        disclosure_version=CURRENT_DISCLOSURE_VERSION,
        acknowledged_at=datetime.now(timezone.utc),
    )

    try:
        db.add(acknowledgement)
        db.commit()
        db.refresh(acknowledgement)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to save consent. Please try again.",
        )

    return {
        "success": True,
        "disclosure_version": CURRENT_DISCLOSURE_VERSION,
        "acknowledged_at": acknowledgement.acknowledged_at.isoformat(),
    }
