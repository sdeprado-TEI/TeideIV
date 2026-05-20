from rest_framework import serializers
from .models import Alumno, Ciclo, Empresa, Asignacion

class CicloSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ciclo
        fields = '__all__'

class AlumnoSerializer(serializers.ModelSerializer):
    ciclo_nombre = serializers.ReadOnlyField(source='ciclo.ciclo')
    ciclo = serializers.PrimaryKeyRelatedField(
        queryset=Ciclo.objects.all(),
        required=False,
        allow_null=True
    )

    def to_internal_value(self, data):
        # Si ciclo llega como texto (nombre), lo convertimos al ID
        ciclo_val = data.get('ciclo')
        if ciclo_val and isinstance(ciclo_val, str) and not ciclo_val.isdigit():
            try:
                ciclo_obj = Ciclo.objects.get(ciclo__iexact=ciclo_val)
                data = data.copy()
                data['ciclo'] = ciclo_obj.pk
            except Ciclo.DoesNotExist:
                # Si no existe el ciclo, lo creamos
                ciclo_obj = Ciclo.objects.create(ciclo=ciclo_val)
                data = data.copy()
                data['ciclo'] = ciclo_obj.pk
        return super().to_internal_value(data)

    class Meta:
        model = Alumno
        fields = '__all__'

class EmpresaSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Empresa
        fields = '__all__'

class AsignacionSerializer(serializers.ModelSerializer):
    alumno_nombre = serializers.ReadOnlyField(source='alumno.nombre')
    empresa_nombre = serializers.ReadOnlyField(source='empresa.nombre')

    class Meta:
        model = Asignacion
        fields = '__all__'
