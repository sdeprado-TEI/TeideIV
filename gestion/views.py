from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Alumno, Empresa, Asignacion
from .serializers import AlumnoSerializer, EmpresaSerializer, AsignacionSerializer


# ── DATOS GENERALES ────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_datos_fct(request):
    return Response({
        'alumnos': AlumnoSerializer(
            Alumno.objects.select_related('ciclo').all(), many=True
        ).data,
        'empresas': EmpresaSerializer(Empresa.objects.all(), many=True).data,
        'asignaciones': AsignacionSerializer(
            Asignacion.objects.select_related('alumno', 'empresa').all(), many=True
        ).data,
    })


# ── AUTENTICACIÓN ──────────────────────────────────────────────────────────────

def user_login(request):
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('password'),
        )
        if user is not None:
            login(request, user)
            return redirect('admin_dashboard' if user.is_staff else 'profesor_dashboard')
        messages.error(request, "Usuario o contraseña incorrectos")
    return render(request, 'login.html')


def user_logout(request):
    logout(request)
    return redirect('login')


# ── DASHBOARDS ─────────────────────────────────────────────────────────────────

@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('profesor_dashboard')
    return render(request, 'FCT_Final.html', {'user_type': 'admin'})


@login_required
def profesor_dashboard(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    return render(request, 'FCT_Final.html', {'user_type': 'profesor'})


# ── CRUD ALUMNOS ───────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_alumno(request):
    serializer = AlumnoSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse(serializer.data, status=201)
    return JsonResponse(serializer.errors, status=400)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def editar_alumno(request, pk):
    alumno = get_object_or_404(Alumno, pk=pk)
    serializer = AlumnoSerializer(alumno, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse(serializer.data)
    return JsonResponse(serializer.errors, status=400)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def borrar_alumno(request, pk):
    alumno = get_object_or_404(Alumno, pk=pk)
    alumno.delete()
    return JsonResponse({'ok': True})


# ── CRUD EMPRESAS ──────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_empresa(request):
    serializer = EmpresaSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse(serializer.data, status=201)
    return JsonResponse(serializer.errors, status=400)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def editar_empresa(request, pk):
    empresa = get_object_or_404(Empresa, pk=pk)
    serializer = EmpresaSerializer(empresa, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse(serializer.data)
    return JsonResponse(serializer.errors, status=400)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def borrar_empresa(request, pk):
    empresa = get_object_or_404(Empresa, pk=pk)
    empresa.delete()
    return JsonResponse({'ok': True})


# ── CRUD ASIGNACIONES ──────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_asignacion(request):
    serializer = AsignacionSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse(serializer.data, status=201)
    return JsonResponse(serializer.errors, status=400)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def editar_asignacion(request, pk):
    asignacion = get_object_or_404(Asignacion, pk=pk)
    serializer = AsignacionSerializer(asignacion, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse(serializer.data)
    return JsonResponse(serializer.errors, status=400)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def borrar_asignacion(request, pk):
    asignacion = get_object_or_404(Asignacion, pk=pk)
    asignacion.delete()
    return JsonResponse({'ok': True})
