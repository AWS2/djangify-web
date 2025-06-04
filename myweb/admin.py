from django.contrib import admin
from .models import Usuario, Project, Mail
# Register your models here.

class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'date_joined')
    search_fields = ('username', 'email')
    ordering = ('-date_joined',)

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user', 'created_at')
    search_fields = ('name',)
    ordering = ('-created_at',)

class MailAdmin(admin.ModelAdmin):
    list_display = ('subject', 'user', 'send')
    list_filter = ('send',)
    search_fields = ('subject', 'body', 'user__username', 'user__email')
    ordering = ('-id',)

admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Mail, MailAdmin)