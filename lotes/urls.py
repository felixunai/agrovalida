from django.urls import path
from . import views

app_name = 'lotes'

urlpatterns = [
    path('', views.lote_list, name='list'),
    path('novo/', views.lote_create, name='create'),
    path('<int:pk>/', views.lote_detail, name='detail'),
    path('<int:pk>/editar/', views.lote_update, name='update'),
    path('<int:pk>/excluir/', views.lote_delete, name='delete'),
    path('<int:pk>/toggle-ativo/', views.lote_toggle_ativo, name='toggle_ativo'),
]