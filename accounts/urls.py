from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('registro/', views.register, name='register'),
    path('usuarios/', views.gerenciar_usuarios, name='usuarios'),
    path('usuarios/<int:pk>/toggle/', views.toggle_usuario, name='toggle_usuario'),
    path('usuarios/<int:pk>/plano/', views.atribuir_plano, name='atribuir_plano'),
    path('upgrade/', views.upgrade, name='upgrade'),
    path('perfil/', views.editar_perfil, name='perfil'),
    path('alterar-senha/', views.alterar_senha, name='alterar_senha'),
    path('assinar/', views.assinar, name='assinar'),
    path('assinar/sucesso/', views.checkout_sucesso, name='checkout_sucesso'),
    path('webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),
]