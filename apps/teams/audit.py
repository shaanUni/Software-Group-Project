from .models import AuditTrail


def log_audit_event(*, user, action, obj=None, description=""):
    if not user or not user.is_authenticated or not user.is_superuser:
        return

    AuditTrail.objects.create(
        admin_user=user,
        action=action,
        model_name=obj.__class__.__name__ if obj else "",
        object_id=str(getattr(obj, "pk", "")) if obj else "",
        object_repr=str(obj) if obj else "",
        description=description,
    )