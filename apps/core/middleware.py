from apps.core.models import AuditLog


class AuditTrailMiddleware:
    """
    Lightweight request-level audit logging.
    Records mutating actions on /api and /admin paths.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.method in {"POST", "PUT", "PATCH", "DELETE"} and (
            request.path.startswith("/api/") or request.path.startswith("/admin/")
        ):
            user = request.user if getattr(request, "user", None) and request.user.is_authenticated else None
            AuditLog.objects.create(
                actor=user,
                action="request",
                path=request.path[:255],
                method=request.method,
                object_type="http_request",
                object_id="",
                ip_address=self._client_ip(request),
                user_agent=request.META.get("HTTP_USER_AGENT", "")[:255],
                metadata={"status_code": response.status_code},
            )
        return response

    @staticmethod
    def _client_ip(request):
        xff = request.META.get("HTTP_X_FORWARDED_FOR", "")
        if xff:
            return xff.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")
