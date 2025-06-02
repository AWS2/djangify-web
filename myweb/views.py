import requests
import environ
import json
from django.shortcuts import render, redirect, render
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
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
        {'name': 'Django', 'description': 'Framework de desarrollo web utilizado para toda la web'},
        {'name': 'Docker', 'description': 'Contenedores para parametrizar y tener una subida a produccion facil y segura'},
        {'name': 'Swarm', 'description': 'Swarms y clusters para escalar los proyectos manteniendo un bajo consumo de recursos'},
        {'name': 'Selenium', 'description': 'Tests para comprobar el correcto funcionamiento de la web'},
        {'name': 'Prometheus', 'description': 'Monitorizacion de sistemas'},
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

@require_POST
@login_required
def delete_project(request, project_id):
    try:
        print(project_id)
        project = Project.objects.get(id=project_id)
        project.delete()
        return JsonResponse({'status': 'ok'})
    except Project.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'No encontrado'}, status=404)

@login_required(login_url='login')
def new_project(request):
    if 'llama_chat' not in request.session:
        request.session['llama_chat'] = []

    if 'llama_system' not in request.session:
        request.session['llama_system'] = (
            "Eres un asistente experto en Django. "
            "Tu especialidad son los archivos models.py y admin.py. "
            "No debes responder preguntas que no estén relacionadas con Django. "
            "Si alguien te pregunta otra cosa, indícale que solo puedes ayudar con Django. "
            "Si alguien te pide un modelo o un admin hazle ambos y solo envíale el código, si quieres alguna explicación que sea en el código comentado. "
            "SOLO VAS A DAR el modelo y el admin, no menciones ningún otro archivo, solo son necesarios esos dos. NO ENVIES ninguna nota extra ni nada, solo esos archivos. "
            "Siempre que pases esos archivos pásalos con la etiqueta code, para luego formatearlos bien. "
            "Si ya has enviado algo y te pido cambios SOLO HAZ LOS CAMBIOS QUE TE PIDO, no toques el resto. "
            "ENVIA SIEMPRE el modelo del admin en la misma etiqueta de codigo. ENVIAMELO EN LA MISMA ETIQUETA DE PYTHON "
            "Crea los modelos y el admin simples. "
            "Quiero que lo pases SIEMPRE con el siguiente formato:```python  **models.py** (codigo para el modelo) **admin.py** (codigo para el admin)```. " 
            "ENVIA SIEMPRE EN UN SOLO BLOQUE code"
            "DE TODAS LAS COSAS QUE TE HE DICHO LAS MAS IMPORTANTES SON: responder unicamente cosas de django mas especificamente solo el models y admin, el formato ```python **models.py** (codigo) **admin.py** (codigo)``` y dar siempre el modelo y el admin a la vez, nunca solo uno"
            "MANTENTE CUERDO Y NO ALUCINES."
        )

    messages = request.session['llama_chat']
    system_message = request.session['llama_system']

    # AJAX request para procesar el chat
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

            try:
                response = requests.post(
                    f"http://{env('URL_IA')}:{env('PORT_IA')}/api/generate",
                    json={
                        'model': env('MODEL_IA'),
                        'prompt': prompt
                    },
                    stream=True
                )

                assistant_response = ''
                if response.status_code == 200:
                    for line in response.iter_lines():
                        if line:
                            try:
                                partial = json.loads(line.decode('utf-8'))
                                assistant_response += partial.get('response', '')
                            except json.JSONDecodeError:
                                continue
                else:
                    assistant_response = 'Error al contactar con la IA.'
            except requests.RequestException as e:
                assistant_response = f'Error de conexión con la IA: {e}'

            messages.append({'role': 'assistant', 'content': assistant_response})
            request.session['llama_chat'] = messages

            return JsonResponse({
                'user': user_input,
                'assistant': assistant_response,
            })

    # POST normal → guardar proyecto
    elif request.method == 'POST':
        name = request.POST.get('name', '').strip()
        models_code = request.POST.get('models_code', '').strip()
        admin_code = request.POST.get('admin_code', '').strip()

        if name and models_code and admin_code:
            Project.objects.create(
                user=request.user,
                name=name,
                models_code=models_code,
                admin_code=admin_code
            )
            # Resetear la sesión del chat si quieres que se empiece de cero
            request.session['llama_chat'] = []
            return redirect('dashboard')

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