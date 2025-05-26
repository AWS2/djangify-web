from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login
from .models import Usuario, Project

# Create your views here.
def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        if password != password_confirm:
            messages.error(request, "Las contraseñas no coinciden.")
            return render(request, 'signin.html')

        if Usuario.objects.filter(username=username).exists():
            messages.error(request, "El nombre de usuario ya está en uso.")
            return render(request, 'signin.html')

        if Usuario.objects.filter(email=email).exists():
            messages.error(request, "El email ya está en uso.")
            return render(request, 'signin.html')

        user = Usuario(
            username=username,
            email=email,
            password=make_password(password)
        )
        user.save()

        # Aquí puedes enviar el correo si lo necesitas

        messages.success(request, "Usuario registrado correctamente. Ahora puedes iniciar sesión.")
        return redirect('login')

    return render(request, 'signin.html')

@login_required(login_url='login')
def dashboard(request):
    projects = Project.objects.filter(user=request.user)
    return render(request, 'dashboard.html', {'projects': projects})

def recover(request):
    return render(request, 'recover.html')

def home(request):
    return render(request, 'home.html')

@login_required(login_url='login')  # URL a donde redirigir si no está logueado
def new_project(request):
    # Lógica para determinar el límite
    max_projects = 6 if request.user.rol == 'GRATIS' else 12

    if request.method == 'POST':
        current_project_count = Project.objects.filter(user=request.user).count()
        if current_project_count >= max_projects:
            messages.error(request, f"Has alcanzado el límite de {max_projects} proyectos.")
            return redirect('dashboard')

        name = request.POST.get('name')
        description = request.POST.get('description')

        if not name:
            messages.error(request, "El nombre del proyecto es obligatorio.")
            return render(request, 'new_project.html')

        Project.objects.create(user=request.user, name=name, description=description)
        messages.success(request, "Proyecto creado correctamente.")
        return redirect('dashboard')

    return render(request, 'new_project.html')

def cookies(request):
    return render(request, 'cookies.html')

def terms_use(request):
    return render(request, 'terms_use.html')

def privacy(request):
    return render(request, 'privacy.html')

def legal_advice(request):
    return render(request, 'legal_advice.html')