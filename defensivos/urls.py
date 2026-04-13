from django.urls import path
from . import views

app_name = 'defensivos'

urlpatterns = [
    path('', views.defensivo_list, name='list'),
    path('novo/', views.defensivo_create, name='create'),
    path('<int:pk>/', views.defensivo_detail, name='detail'),
    path('<int:pk>/editar/', views.defensivo_update, name='update'),
    path('<int:pk>/excluir/', views.defensivo_delete, name='delete'),
]