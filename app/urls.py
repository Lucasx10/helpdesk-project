from django.urls import path
from .views import *

urlpatterns = [
    path('home', index, name='index'),
    path("register", register, name="register"),
    path("login_view", login_view, name="login_view"),
    path("registration", registration, name="registration"),
    path("", loginpage, name="loginpage"),
    path('chamado/<int:chamado_id>', chamado_by_id, name='chamado_by_id'),
    path("abrir_chamado", abrir_chamado, name="abrir_chamado"),
    path("chamado", chamado, name="chamado"),
    path("logout", signout, name="logout"),
    path("editar_chamado/<int:chamado_id>", editar_chamado, name="editar_chamado"),
    path('chamado/<int:chamado_id>/transferir/', transferir_chamado, name='transferir_chamado'),
    path('confirmar_finalizacao/<int:chamado_id>/', confirmar_finalizacao, name='confirmar_finalizacao'),
]