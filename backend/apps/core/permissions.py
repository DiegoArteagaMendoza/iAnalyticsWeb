from rest_framework import permissions


class IsStaffWithModelPermissions(permissions.DjangoModelPermissions):
    """
    API de gestión: solo usuarios del staff, y cada acción según los permisos
    del modelo (ver, agregar, cambiar, eliminar) asignados en el admin.
    """

    perms_map = {
        **permissions.DjangoModelPermissions.perms_map,
        "GET": ["%(app_label)s.view_%(model_name)s"],
        "HEAD": ["%(app_label)s.view_%(model_name)s"],
    }

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated and user.is_staff):
            return False
        return super().has_permission(request, view)
