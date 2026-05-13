from rest_framework import serializers
from .models import Alumno, Ciclo, Empresa, Asignacion

class CicloSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ciclo
        fields = '__all__'

class AlumnoSerializer(serializers.ModelSerializer):
    # Esto permite ver el nombre del ciclo en el JSON
    ciclo_nombre = serializers.ReadOnlyField(source='ciclo.ciclo')

    class Meta:
        model = Alumno
        fields = '__all__'

# --- ESTO ES LO QUE TE FALTA ---

class EmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = '__all__'

class AsignacionSerializer(serializers.ModelSerializer):
    # Para que el JS vea nombres reales y no solo números de ID
    alumno_nombre = serializers.ReadOnlyField(source='alumno.nombre') 
    empresa_nombre = serializers.ReadOnlyField(source='empresa.nombre')

    class Meta:
        model = Asignacion
        fields = '__all__'