from django.urls import path
from . import views

app_name = 'fazendas'

urlpatterns = [
    path('', views.fazenda_list, name='list'),
    path('nova/', views.fazenda_create, name='create'),
    path('<int:pk>/', views.fazenda_detail, name='detail'),
    path('<int:pk>/editar/', views.fazenda_update, name='update'),
    path('<int:pk>/excluir/', views.fazenda_delete, name='delete'),
]
