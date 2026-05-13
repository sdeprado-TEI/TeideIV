from django.contrib import admin
from .models import Ciclo, Alumno

@admin.register(Ciclo)
class CicloAdmin(admin.ModelAdmin):
    list_display = ('ciclo', 'preparacion')

@admin.register(Alumno)
class AlumnoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellidos', 'ciclo', 'tutor_fct')
    search_fields = ('nombre', 'apellidos', 'dni')