from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter

from accounts.urls import admin_urlpatterns as accounts_admin_urlpatterns
from tasks.views import AdminTaskViewSet


def health_check(request):
    return JsonResponse({"status": "ok", "message": "Employee Task Management API is running"})


admin_task_router = DefaultRouter(trailing_slash=True)
admin_task_router.register(r"tasks", AdminTaskViewSet, basename="admin-task")

urlpatterns = [
    path("", health_check, name="health-root"),
    path("health/", health_check, name="health"),
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/tasks/", include("tasks.urls")),
    path("api/admin/", include(accounts_admin_urlpatterns)),
    path("api/admin/", include(admin_task_router.urls)),
]