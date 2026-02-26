from rest_framework import permissions

from .models import BranchMembership, BranchRole


class IsBranchStaff(permissions.BasePermission):
    allowed_roles = {BranchRole.MANAGER, BranchRole.CHEF, BranchRole.COURIER, BranchRole.ADMIN}

    def has_permission(self, request, view):
        branch_id = request.query_params.get("branch_id") or request.data.get("branch")
        if not request.user or not request.user.is_authenticated or not branch_id:
            return False
        return BranchMembership.objects.filter(
            user=request.user,
            branch_id=branch_id,
            role__in=self.allowed_roles,
            is_active=True,
        ).exists()
