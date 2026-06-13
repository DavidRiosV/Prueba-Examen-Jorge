from django.urls import path
from django.contrib.auth.views import LoginView
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', LoginView.as_view(template_name='examen/login.html'), name='login'),
    path('logout/', views.mi_logout, name='logout'),
    path('registro/veterinario/', views.registro_veterinario, name='registro_vet'),
    path('registro/dueno/', views.registro_dueno, name='registro_dueno'),
    path('intervenciones/', views.listar_intervenciones, name='listar_intervenciones'),
    path('intervenciones/nueva/', views.crear_intervencion, name='crear_intervencion'),
    path('intervenciones/<int:pk>/editar/', views.editar_intervencion, name='editar'),
    path('intervenciones/<int:pk>/eliminar/', views.eliminar_intervencion, name='eliminar'),
    path('mis-animales/', views.mis_animales, name='mis_animales'),
    path('buscar/', views.buscar, name='buscar'),
]