try:
    from .celery import app as celery_app
except Exception:  # pragma: no cover - optional in local env without celery installed
    celery_app = None

__all__ = ("celery_app",)
