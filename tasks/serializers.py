from django.utils import timezone
from rest_framework import serializers
from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    owner_email = serializers.EmailField(source="owner.email", read_only=True)

    class Meta:
        model = Task
        fields = [
            "id", "title", "description", "priority", "status",
            "due_date", "created_at", "updated_at", "owner", "owner_email",
        ]
        read_only_fields = ["id", "owner", "owner_email", "created_at", "updated_at"]

    def validate_title(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Title cannot be empty.")
        return value

    def validate_due_date(self, value):
        # Allow None (no due date set) but reject dates absurdly in the past
        # on creation only - editing a task to mark an old overdue date as
        # Completed should still be allowed, so we only check on create.
        if value and self.instance is None and value < timezone.now() - timezone.timedelta(days=1):
            raise serializers.ValidationError("Due date cannot be in the past.")
        return value