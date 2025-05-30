import requests
import environ
import json
from django.shortcuts import render, redirect, render
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login
from .models import Usuario, Project
from ollama import chat
from django.http import JsonResponse
from django.conf import settings

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

def home(request):
    features = [
        {'name': 'Django', 'description': 'Framework de desarrollo web'},
        {'name': 'Python', 'description': 'Lenguaje de programación'},
        {'name': 'Docker', 'description': 'Contenedores para aplicaciones'},
        {'name': 'CI/CD', 'description': 'Integración continua y entrega continua'},
        {'name': 'Prometheus', 'description': 'Monitoreo de sistemas'},
        {'name': 'Grafana', 'description': 'Visualización de métricas'},
    ]

    return render(request, 'home.html', {'features': features})

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
    request.session.pop('llama_chat', None)
    request.session.pop('llama_system', None)
    return render(request, 'dashboard.html', {'projects': projects})

def recover(request):
    return render(request, 'recover.html')

@login_required(login_url='login')
def new_project(request):
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if 'llama_chat' not in request.session:
            request.session['llama_chat'] = []

        if 'llama_system' not in request.session:
            request.session['llama_system'] = (
                "Eres un asistente experto en Django. "
                "Tu especialidad son los archivos models.py y admin.py. "
                "No debes responder preguntas que no estén relacionadas con Django. "
                "Si alguien te pregunta otra cosa, indícale que solo puedes ayudar con Django."
                "Si alguien te pide un modelo o un admin hazle ambos y solo envíale el código, si quieres alguna explicación que sea en el código comentado."
            )

        messages = request.session['llama_chat']
        system_message = request.session['llama_system']
        user_input = request.POST.get('user_input', '').strip()

        if user_input:
            messages.append({'role': 'user', 'content': user_input})

            prompt = f"Sistema: {system_message}\n"
            for m in messages:
                role = m['role']
                if role == 'user':
                    prompt += f"Usuario: {m['content']}\n"
                elif role == 'assistant':
                    prompt += f"Asistente: {m['content']}\n"
            prompt += "Asistente:"

            try:
                response = requests.post(
                    f"http://localhost:{env('PORT_IA')}/api/generate",
                    json={
                        'model': env('MODEL_IA'),
                        'prompt': prompt,
                        'stream': True
                    },
                    stream=True
                )

                assistant_response = ''
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line.decode('utf-8'))
                            assistant_response += data.get('response', '')
                        except json.JSONDecodeError:
                            continue

                messages.append({'role': 'assistant', 'content': assistant_response})
                request.session['llama_chat'] = messages
                return JsonResponse({'role': 'assistant', 'content': assistant_response})

            except requests.RequestException as e:
                return JsonResponse({'role': 'assistant', 'content': f'Error de conexión con la IA: {e}'})

        return JsonResponse({'role': 'assistant', 'content': 'Entrada vacía'})

    # GET request
    return render(request, 'new_project.html', {
        'messages': request.session.get('llama_chat', []),
        'user_input': '',
    })
    
@login_required(login_url='login')
def new_project(request):
    if 'llama_chat' not in request.session:
            request.session['llama_chat'] = []

    if 'llama_system' not in request.session:
        request.session['llama_system'] = (
                "Eres un asistente experto en Django. "
                "Tu especialidad son los archivos models.py y admin.py. "
                "No debes responder preguntas que no estén relacionadas con Django. "
                "Si alguien te pregunta otra cosa, indícale que solo puedes ayudar con Django."
                "Si alguien te pide un modelo o un admin hazle ambos y solo enviale el codigo, si quieres alguna explicacion que sea en el codigo comentado."
                "SOLO VAS A DAR el modelo y el admin, no menciones ningun otro archivo, solo son necesarios esos dos."
                "Siempre que pases esos archivos pasalos con la etiqueta code, para luego formatearlos bien."
                "Si ya has enviado algo y te pido cambios SOLO HAZ LOS CAMBIOS QUE TE PIDO, no toques el resto. "
                "Separa el modelo del admin simpre. "
                "MANTENTE CUERDO Y NO ALUCINES"
    )

    messages = request.session['llama_chat']
    system_message = request.session['llama_system']

    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        user_input = request.POST.get('user_input', '').strip()
        if user_input:
            messages.append({'role': 'user', 'content': user_input})

            # Construir prompt: system + historial
            prompt = f"Sistema: {system_message}\n"
            for m in messages:
                role = m['role']
                if role == 'user':
                    prompt += f"Usuario: {m['content']}\n"
                elif role == 'assistant':
                    prompt += f"Asistente: {m['content']}\n"
            prompt += "Asistente:"

            response = requests.post(
                f"http://{env('URL_IA')}:{env('PORT_IA')}/api/generate",
                json={
                    'model': env('MODEL_IA'),
                    'prompt': prompt
                }
            )

            if response.status_code == 200:
                assistant_response = ''
                for line in response.iter_lines():
                    if line:
                        try:
                            partial = json.loads(line.decode('utf-8'))
                            assistant_response += partial.get('response', '')
                        except json.JSONDecodeError:
                            continue
            else:
                assistant_response = 'Error al contactar con la IA.'

            messages.append({'role': 'assistant', 'content': assistant_response})
            request.session['llama_chat'] = messages

            return JsonResponse({
                'user': user_input,
                'assistant': assistant_response,
            })

    # Si no es AJAX, muestra la plantilla normal
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