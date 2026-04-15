from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard, name='index'),
    path('graficos/', views.dashboard_graficos, name='graficos'),
    path('relatorio/vencimento/', views.relatorio_vencimento, name='relatorio_vencimento'),
    path('relatorio/vencimento/csv/', views.relatorio_vencimento_csv, name='relatorio_vencimento_csv'),
    path('relatorio/vencimento/excel/', views.relatorio_vencimento_excel, name='relatorio_vencimento_excel'),
]
