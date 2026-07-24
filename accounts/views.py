from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status, filters
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer, UserSerializer
from .serializers import UserSerializer  # you likely already import this
from .permissions import IsAdminRole

User = get_user_model()
class RegisterView(generics.CreateAPIView):
    """POST /api/auth/register/ - public. Returns tokens immediately so the
    Flutter app can log the user straight in after registering."""
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "success": True,
                "message": "Registration successful",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    """POST /api/auth/login/ - public. Accepts {email, password}."""
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]


class MeView(APIView):
    """GET /api/auth/me/ - requires auth. Returns the logged-in user's profile."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class LogoutView(APIView):
    """
    POST /api/auth/logout/ - acknowledges logout. With JWT, logout is primarily
    a client-side action (discard the stored token); this endpoint exists so
    the Flutter app has a consistent server call to hit on sign-out.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        return Response({"success": True, "message": "Logged out successfully"})


# ---------- Admin-only (React admin panel) ----------
class AdminUserListView(generics.ListAPIView):
    """GET /api/admin/users/?search= - View all users."""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["email", "name"]
    ordering_fields = ["date_joined", "name", "email"]
    ordering = ["-date_joined"]
    queryset = User.objects.all()


class AdminUserDetailView(generics.RetrieveDestroyAPIView):
    """GET/DELETE /api/admin/users/{id}/ - Delete users."""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]
    queryset = User.objects.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.id == request.user.id:
            raise ValidationError({"detail": "You cannot delete your own account."})
        if instance.is_superuser:
            raise ValidationError({"detail": "Superuser accounts cannot be deleted from this panel."})
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)