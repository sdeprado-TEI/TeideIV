from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib import messages
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Alumno, Empresa, Asignacion
from .serializers import AlumnoSerializer, EmpresaSerializer, AsignacionSerializer
from django.contrib.auth import logout # Añade este import arriba



# 1. FUNCIÓN DE DATOS USANDO SERIALIZERS (Protegida)
@api_view(['GET'])
@login_required
def get_datos_fct(request):
    alumnos = Alumno.objects.all()
    empresas = Empresa.objects.all()
    asignaciones = Asignacion.objects.all()

    return Response({
        'alumnos': AlumnoSerializer(alumnos, many=True).data,
        'empresas': EmpresaSerializer(empresas, many=True).data,
        'asignaciones': AsignacionSerializer(asignaciones, many=True).data
    })

# 2. LOGIN
def user_login(request):
    if request.method == 'POST':
        u_name = request.POST.get('username')
        p_word = request.POST.get('password')
        
        user = authenticate(request, username=u_name, password=p_word)
        
        if user is not None:
            login(request, user)
            if user.is_staff: 
                return redirect('admin_dashboard')
            else:
                return redirect('profesor_dashboard')
        else:
            messages.error(request, "Usuario o contraseña incorrectos")
            
    return render(request, 'login.html')

# 3. DASHBOARDS PROTEGIDOS
@login_required
def admin_dashboard(request):
    # Si un usuario no es staff (profesor) intenta entrar aquí, lo mandamos a su panel
    if not request.user.is_staff:
        return redirect('profesor_dashboard')
    return render(request, 'FCT_Final.html', {'user_type': 'admin'})

@login_required
def profesor_dashboard(request):
    # Opcional: si un admin entra aquí, lo mandamos a su panel de gestión
    if request.user.is_staff:
        return redirect('admin_dashboard')
    return render(request, 'FCT_Final.html', {'user_type': 'profesor'})

def user_logout(request):
    logout(request)
    return redirect('login')

import json
from django.http import JsonResponse

@api_view(['POST'])
@login_required
def crear_alumno(request):
    data = json.loads(request.body)
    serializer = AlumnoSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse(serializer.data, status=201)
    return JsonResponse(serializer.errors, status=400)

@api_view(['PUT'])
@login_required
def editar_alumno(request, pk):
    alumno = Alumno.objects.get(pk=pk)
    data = json.loads(request.body)
    serializer = AlumnoSerializer(alumno, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse(serializer.data)
    return JsonResponse(serializer.errors, status=400)

@api_view(['DELETE'])
@login_required
def borrar_alumno(request, pk):
    Alumno.objects.get(pk=pk).delete()
    return JsonResponse({'ok': True})
