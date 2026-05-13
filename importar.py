import os
import django
import re

# Configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'teide_iv.settings')
django.setup()

from gestion.models import Alumno, Ciclo

def importar():
    sql_file = 'bbdd_teide_depurada.sql'
    
    if not os.path.exists(sql_file):
        print(f"Error: No encuentro el archivo {sql_file}")
        return

    with open(sql_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Importar Ciclos
    print("Importando ciclos...")
    ciclos_data = re.findall(r"INSERT INTO `ciclos` VALUES \((.*?)\);", content)
    for data in ciclos_data:
        vals = [v.strip().strip("'") for v in data.split(',')]
        # Cambiamos id_ciclo= por id=
        Ciclo.objects.get_or_create(id=vals[0], ciclo=vals[1], preparacion=vals[2])
    # 2. Importar Alumnos
    print("Importando alumnos...")
    alumnos_data = re.findall(r"INSERT INTO `datos_alumnos` VALUES \((.*?)\);", content)
    for data in alumnos_data:
        # Split inteligente para manejar comas dentro de los textos
        vals = [v.strip().strip("'") for v in re.split(r",(?=(?:[^']*'[^']*')*[^']*$)", data)]
        
        try:
            Alumno.objects.get_or_create(
                dni=vals[1],
                defaults={
                    'apellidos': vals[2],
                    'nombre': vals[3],
                    'fecha_nto': vals[4] if vals[4] != 'NULL' else None,
                    'direccion': vals[5],
                    'poblacion': vals[6],
                    'codigo_postal': vals[7],
                    'tlf_casa': vals[8],
                    'tlf_movil': vals[9],
                    'ano_curso': vals[10],
                    # Cambiamos ciclo_id= por ciclo_id=vals[11] (esto suele estar bien, pero revísalo)
                    'ciclo_id': vals[11],
                    'grado': vals[12],
                    'turno': vals[13],
                    'num_alumno': int(vals[14]) if vals[14].isdigit() else None
                }
            )
        except Exception as e:
            print(f"Error con alumno {vals[1]}: {e}")

    print("--- Proceso finalizado con éxito ---")

if __name__ == '__main__':
    importar()