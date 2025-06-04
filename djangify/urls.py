"""
URL configuration for djangify project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from myweb.views import *
from myweb import api
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.views.i18n import set_language

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
]

urlpatterns += i18n_patterns(
    path('home/', home, name='home'),
    path('administracio/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('signin/', signin, name='signin'),
    path('dashboard/', dashboard, name='dashboard'),
    path('recover/', recover, name='recover'),
    path('new_password/<int:uid>/<str:token>/', new_password, name='new_password'),
    path('cookies/', cookies, name='cookies'),
    path('terms_use/', terms_use, name='terms'),
    path('privacy/', privacy, name='privacy'),
    path('legal_advice/', legal_advice, name='legal_advice'),
    path('new_project/', new_project, name='new_project'),
    path('delete_project/<uuid:project_id>/', delete_project, name='delete_project'),
    path('verify/<str:username>/', verify_user, name='verify_user'),
    path('change-password/', change_password, name='change_password'),
)
