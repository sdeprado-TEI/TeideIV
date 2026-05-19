from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # Dashboards
    path('administrador/', views.admin_dashboard, name='admin_dashboard'),
    path('profesor/', views.profesor_dashboard, name='profesor_dashboard'),

    # Datos generales
    path('api/get-datos-fct/', views.get_datos_fct, name='get_datos_fct'),

    # CRUD Alumnos
    path('api/alumno/crear/', views.crear_alumno, name='crear_alumno'),
    path('api/alumno/editar/<int:pk>/', views.editar_alumno, name='editar_alumno'),
    path('api/alumno/borrar/<int:pk>/', views.borrar_alumno, name='borrar_alumno'),

    # CRUD Empresas
    path('api/empresa/crear/', views.crear_empresa, name='crear_empresa'),
    path('api/empresa/editar/<int:pk>/', views.editar_empresa, name='editar_empresa'),
    path('api/empresa/borrar/<int:pk>/', views.borrar_empresa, name='borrar_empresa'),

    # CRUD Asignaciones
    path('api/asignacion/crear/', views.crear_asignacion, name='crear_asignacion'),
    path('api/asignacion/editar/<int:pk>/', views.editar_asignacion, name='editar_asignacion'),
    path('api/asignacion/borrar/<int:pk>/', views.borrar_asignacion, name='borrar_asignacion'),
]
