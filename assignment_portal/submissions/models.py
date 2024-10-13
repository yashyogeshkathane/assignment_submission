from djongo import models
from django.contrib.auth.models import AbstractUser

# Extend User model to allow distinction between Admin, Superuser, and User
class CustomUser(AbstractUser):
    is_admin = models.BooleanField(default=False)  # Distinguishes Admin from User
    is_superuser_custom = models.BooleanField(default=False)  # Custom superuser flag

    def __str__(self):
        return self.username

class Assignment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='assignments')
    task = models.TextField()
    admin = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='assigned_tasks', limit_choices_to={'is_admin': True})
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Assignment from {self.user.username} to {self.admin.username} - {self.status}'
