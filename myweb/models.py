from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
# Create your models here.

class Usuario(AbstractUser):
    email = models.EmailField(unique=True)
    validated = models.BooleanField(default=False)

    ROL_CHOICES = (
        ('GRATIS', 'Gratis'),
        ('PLUS', 'Plus'),
    )
    rol = models.CharField(max_length=10, choices=ROL_CHOICES, default='GRATIS')

    def __str__(self):
        return self.username

class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    models_code = models.TextField("Código de models.py", blank=True, null=True)
    admin_code = models.TextField("Código de admin.py", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class Mail(models.Model):
    subject = models.CharField(max_length=255)
    body = models.TextField()
    send = models.BooleanField(default=False)
    user = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.subject} to {self.user.email}"
