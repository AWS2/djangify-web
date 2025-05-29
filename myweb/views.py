from django.shortcuts import render, redirect, render
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login
from .models import Usuario, Project
from ollama import chat
import requests

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
    return render(request, 'new_project.html')


@login_required(login_url='login')
def chat_llama(request):
    # Inicializa el historial en la sesión si no existe
    if 'llama_chat' not in request.session:
        request.session['llama_chat'] = []

    messages = request.session['llama_chat']
    user_input = ''

    if request.method == 'POST':
        user_input = request.POST.get('user_input', '').strip()
        if user_input:
            messages.append({'role': 'user', 'content': user_input})

            response = requests.post(
                f"http://localhost:{env('PORT_IA')}/api/generate",
                json={
                    'model': env('MODEL_IA'),
                    'prompt': user_input
                }
            )

            if response.status_code == 200:
                data = response.json()
                assistant_response = data.get('response', '[Sin respuesta]')
                messages.append({'role': 'assistant', 'content': assistant_response})
            else:
                messages.append({'role': 'assistant', 'content': 'Error al contactar con la IA.'})

            # Guarda la conversación actualizada
            request.session['llama_chat'] = messages

    return render(request, 'new_project.html', {
        'messages': messages,
        'user_input': '',
    })

def cookies(request):
    return render(request, 'cookies.html')

def terms_use(request):
    return render(request, 'terms_use.html')

def privacy(request):
    return render(request, 'privacy.html')

def legal_advice(request):
    return render(request, 'legal_advice.html')