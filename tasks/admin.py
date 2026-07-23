from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """
    Bonus requirement covered out of the box: view all tasks, update task
    status, delete tasks - all available immediately via /admin/.
    """
    list_display = ["title", "owner", "priority", "status", "due_date", "created_at"]
    list_filter = ["status", "priority"]
    search_fields = ["title", "description", "owner__email"]
    list_editable = ["status"]
    autocomplete_fields = ["owner"]
    ordering = ["-created_at"]
