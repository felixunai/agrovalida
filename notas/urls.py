from django.urls import path
from . import views

app_name = 'notas'

urlpatterns = [
    path('', views.nota_list, name='list'),
    path('upload/', views.nota_upload, name='upload'),
    path('<int:pk>/', views.nota_detail, name='detail'),
    path('<int:pk>/importar/', views.nota_importar, name='importar'),
    path('item/<int:item_pk>/importar/', views.importar_item_lote, name='importar_item'),
]