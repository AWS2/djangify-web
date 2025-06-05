import requests
import environ
import json
from django.shortcuts import render, redirect, render, get_object_or_404
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, update_session_auth_hash, logout
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Usuario, Project, Mail
from ollama import chat
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ObjectDoesNotExist

User = get_user_model()

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

def home(request):
    lang = request.COOKIES.get('django_language', 'es')  # por defecto 'es' si no hay cookie

    features_dict = {
        'es': [
            {'name': 'Django', 'description': 'Framework de desarrollo web utilizado para toda la web'},
            {'name': 'Docker', 'description': 'Contenedores para parametrizar y tener una subida a producción fácil y segura'},
            {'name': 'Swarm', 'description': 'Swarms y clusters para escalar los proyectos manteniendo un bajo consumo de recursos'},
            {'name': 'Selenium', 'description': 'Tests para comprobar el correcto funcionamiento de la web'},
            {'name': 'OLlama', 'description': 'IA para la creación de archivos clave para Django'}, 
            {'name': 'Prometheus', 'description': 'Monitorización de sistemas'},
        ],
        'en': [
            {'name': 'Django', 'description': 'Web development framework used for the entire site'},
            {'name': 'Docker', 'description': 'Containers to configure and easily and safely deploy to production'},
            {'name': 'Swarm', 'description': 'Swarms and clusters to scale projects while keeping resource usage low'},
            {'name': 'Selenium', 'description': 'Tests to verify the correct operation of the website'},
            {'name': 'OLlama', 'description': 'AI for creating key Django files'},
            {'name': 'Prometheus', 'description': 'System monitoring'},
        ],
        'ca': [
            {'name': 'Django', 'description': 'Framework de desenvolupament web utilitzat per a tot el lloc web'},
            {'name': 'Docker', 'description': 'Contenidors per parametritzar i fer una pujada a producció fàcil i segura'},
            {'name': 'Swarm', 'description': 'Swarms i clústers per escalar els projectes mantenint un baix consum de recursos'},
            {'name': 'Selenium', 'description': 'Tests per comprovar el correcte funcionament del lloc web'},
            {'name': 'OLlama', 'description': 'IA per a la creació d’arxius clau per a Django'}, 
            {'name': 'Prometheus', 'description': 'Monitorització de sistemes'},
        ]
    }

    features = features_dict.get(lang, features_dict['es'])

    return render(request, 'home.html', {'features': features})

def verify_user(request, username):
    user = get_object_or_404(User, username=username)
    
    if not user.validated:
        user.validated = True
        user.save()
        messages.success(request, "Tu cuenta ha sido verificada correctamente.")
    else:
        messages.info(request, "Tu cuenta ya estaba verificada.")

    return redirect('login')  # Asegúrate de que 'login' esté definido en tus urls

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

        mail = Mail(
            subject="Validacion de correo electronico",
            body=f"""
                    Hola {user.username},

                    ¡Gracias por registrarte en nuestra plataforma!

                    Para completar tu registro, por favor verifica tu dirección de correo electrónico haciendo clic en el siguiente enlace:

                    {env('URL_MAIL')}/verify/{user.username}/

                    Si no has creado esta cuenta, puedes ignorar este mensaje.

                    Saludos,
                    Djangify.
                    """,
            send=False,
            user=user
        )
        mail.save()

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

@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        if password != password_confirm:
            messages.error(request, "Las contraseñas no coinciden.")
        else:
            user = request.user
            user.set_password(password)
            user.save()
            logout(request)  # 🔒 cierra la sesión del usuario
            messages.success(request, "Contraseña cambiada correctamente. Por favor, inicia sesión nuevamente.")
            return redirect('login')  # 🔁 redirige a la vista de login (ajusta el nombre si es distinto)

        return redirect('dashboard')

    return redirect('dashboard')

def recover(request):
    if request.method == "POST":
        email = request.POST.get("email")

        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = user.id
            reset_link = f"{env('URL_MAIL')}/new_password/{uid}/{token}/"

            mail = Mail(
                subject="Recuperacion de contrasena - Djangify",
                body=f"""
                    Hola {user.username},

                    Hemos recibido una solicitud para restablecer la contraseña de tu cuenta en Djangify.

                    Para crear una nueva contraseña, haz clic en el siguiente enlace:

                    {reset_link}

                    Este enlace es válido solo por un tiempo limitado y solo puede usarse una vez.  
                    Si no solicitaste el restablecimiento, ignora este mensaje.

                    Saludos,  
                    El equipo de Djangify.
                """,
                send=False,
                user=user
            )
            mail.save()

            messages.success(request, "Correo de recuperación enviado.")

        except ObjectDoesNotExist:
            messages.error(request, "No existe un usuario con ese correo.")

    return render(request, 'recover.html')

def new_password(request, uid, token):
    user = get_object_or_404(User, pk=uid)

    if not default_token_generator.check_token(user, token):
        messages.error(request, "El enlace no es válido o ha expirado.")
        return redirect('login')

    if request.method == "POST":
        password = request.POST.get("password")
        confirm = request.POST.get("confirm")

        if password != confirm:
            messages.error(request, "Las contraseñas no coinciden.")
        else:
            user.set_password(password)
            user.save()
            messages.success(request, "Contraseña restablecida correctamente.")
            return redirect('login')

    return render(request, 'new_password.html', {'user': user})

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
            "Eres un asistente especializado en Django, con foco exclusivo en la creación de archivos models.py y admin.py. "
            "Solo respondes consultas relacionadas con Django; si te preguntan sobre otro tema, indícalo claramente (“Solo puedo ayudar con Django”). "
            "Cuando soliciten un modelo o un admin, envía ambos archivos juntos, en un único bloque de código, sin agregar ningún texto extra. "
            "No menciones ni generes ningún otro archivo (ni vistas, ni formularios, ni settings, etc.). Solo models.py y admin.py. "
            "El contenido dentro de cada archivo debe ser sencillo y directo. Si necesitas explicar algo, hazlo con comentarios dentro del código. "
            "Nunca combines el admin en el mismo archivo que los modelos. models.py y admin.py siempre separados, pero enviados juntos en la misma etiqueta de código. "
            "Usa siempre la etiqueta de bloque de código Markdown: el contenido de models.py entre python y luego el contenido de admin.py entre python. No agregues encabezados, notas adicionales ni explicaciones fuera de comentarios en el código. "
            "Si ya enviaste un models.py y un admin.py y solicitan cambios, solo modifica exactamente lo pedido; no alteres nada más. "
            "Lo más importante: responder únicamente cosas de Django, y solo models.py y admin.py; entregar siempre ambos archivos a la vez, en un solo bloque de código; no alucinar ni inventar información."
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

            try:
                response = requests.post(
                    f"http://{env('URL_IA')}:{env('PORT_IA')}/api/generate",
                    json={
                        'model': env('MODEL_IA'),
                        'prompt': 
                        "Te voy a pasar una respuesta tuya y quiero que me duelvas unica y exclusivamente el models.py y el admin.py."
                        "No añadas ningun comentario, solo codigo. "
                        "Quiero que me lo hagas siempre con el mismo formato, " 
                        + assistant_response
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