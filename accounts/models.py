from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import UserManager


class User(AbstractUser):
    """
    Custom user: email is the login identifier instead of username.
    username is kept (required by AbstractUser/Django admin internals)
    but is auto-derived and not used for login.
    """
    username = models.CharField(max_length=150, unique=True, blank=True)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=150)
    is_admin_user = models.BooleanField(
        default=False,
        help_text="Marks this account as an Employee Task Management admin (separate from Django is_staff).",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    objects = UserManager()

    def save(self, *args, **kwargs):
        if not self.username:
            # derive a unique-enough username from email so Django internals
            # (which still reference `username`) don't break
            import uuid
            base = self.email.split("@")[0][:130]
            self.username = base if not User.objects.filter(username=base).exists() else f"{base}-{uuid.uuid4().hex[:8]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email
