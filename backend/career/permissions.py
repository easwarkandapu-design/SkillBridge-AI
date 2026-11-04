from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsRecruiterOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.role in ("RECRUITER", "ADMIN"))

class IsOwnerOrRecruiter(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.role == "ADMIN":
            return True
        if hasattr(obj, "candidate_id"):
            return obj.candidate_id == request.user.id or obj.job.recruiter_id == request.user.id
        return getattr(obj, "user_id", None) == request.user.id
