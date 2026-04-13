from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('registro/', views.register, name='register'),
    path('usuarios/', views.gerenciar_usuarios, name='usuarios'),
    path('usuarios/<int:pk>/toggle/', views.toggle_usuario, name='toggle_usuario'),
    path('usuarios/<int:pk>/plano/', views.atribuir_plano, name='atribuir_plano'),
]