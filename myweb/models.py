from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class Usuario(AbstractUser):
    email = models.EmailField(unique=True)
    
    ROL_CHOICES = (
        ('GRATIS', 'Gratis'),
        ('PLUS', 'Plus'),
    )
    rol = models.CharField(max_length=10, choices=ROL_CHOICES, default='GRATIS')

    def __str__(self):
        return self.username

class Project(models.Model):
    user = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name