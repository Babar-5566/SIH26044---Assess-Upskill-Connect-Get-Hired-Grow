"""Deliver pending notifications to an optional webhook.

Run periodically with: python -m app.scripts.notification_worker
"""
from datetime import datetime, timezone
import httpx
from app.core.config import settings
from app.db.session import SessionLocal
from app.models import Notification


def run_once(limit: int = 100) -> int:
    if not settings.notification_webhook_url:
        return 0
    delivered = 0
    with SessionLocal() as db:
        rows = db.query(Notification).filter_by(delivery_status="PENDING").order_by(Notification.created_at).limit(limit).all()
        for row in rows:
            row.delivery_attempts += 1
            try:
                response = httpx.post(settings.notification_webhook_url, json={"id": str(row.id), "user_id": str(row.user_id), "title": row.title, "message": row.message, "kind": row.kind}, timeout=10)
                response.raise_for_status()
                row.delivery_status = "DELIVERED"
                row.delivered_at = datetime.now(timezone.utc)
                row.last_delivery_error = None
                delivered += 1
            except Exception as exc:
                row.last_delivery_error = str(exc)[:2000]
                if row.delivery_attempts >= 5:
                    row.delivery_status = "FAILED"
        db.commit()
    return delivered


if __name__ == "__main__":
    print(f"delivered={run_once()}")
