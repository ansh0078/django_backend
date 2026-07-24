from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, permissions
from .models import Task
from .serializers import TaskSerializer
from .permissions import IsOwner


class TaskViewSet(viewsets.ModelViewSet):
    """
    /api/tasks/            GET (list, supports ?search=&status=&priority=&ordering=), POST (create)
    /api/tasks/{id}/        GET (detail), PUT/PATCH (update), DELETE
    """
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "priority"]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "due_date", "priority", "status"]
    ordering = ["-created_at"]

    def get_queryset(self):
        # Each user only ever sees their own tasks - enforced at the
        # queryset level (not just object permission) so list/search/filter
        # can't leak other users' tasks either.
        return Task.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
