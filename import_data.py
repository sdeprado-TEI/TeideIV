"""
Script de importación: migra datos del SQL dump (bbdd_teide_depurada.sql) a Django DB.
Ejecutar desde la carpeta raíz del proyecto:  python import_data.py
"""
import os, sys, re, django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'teide_iv.settings')
django.setup()

from django.db import connection, transaction
from gestion.models import Alumno, Empresa, Asignacion, Ciclo

SQL_FILE = 'bbdd_teide_depurada.sql'


def parse_values(row_str):
    """Parse a SQL VALUES row string into a list of Python values."""
    values = []
    i = 0
    s = row_str.strip()
    while i < len(s):
        if s[i] == "'":
            # String value
            end = i + 1
            val_chars = []
            while end < len(s):
                if s[end] == '\\' and end + 1 < len(s):
                    val_chars.append(s[end + 1])
                    end += 2
                elif s[end] == "'":
                    break
                else:
                    val_chars.append(s[end])
                    end += 1
            values.append(''.join(val_chars))
            i = end + 1
            # Skip comma
            while i < len(s) and s[i] in (' ', ','):
                i += 1
        elif s[i:i+4].upper() == 'NULL':
            values.append(None)
            i += 4
            while i < len(s) and s[i] in (' ', ','):
                i += 1
        else:
            # Number
            end = i
            while end < len(s) and s[end] not in (',', ')'):
                end += 1
            num_str = s[i:end].strip()
            try:
                values.append(int(num_str))
            except ValueError:
                try:
                    values.append(float(num_str))
                except ValueError:
                    values.append(num_str)
            i = end
            while i < len(s) and s[i] in (' ', ','):
                i += 1
    return values


def extract_inserts(content, table):
    """Extract all rows from INSERT statements for a table."""
    pattern = r'INSERT INTO `' + re.escape(table) + r'` VALUES\s*(.*?);'
    rows = []
    for match in re.finditer(pattern, content, re.DOTALL):
        block = match.group(1).strip()
        # Split into individual row strings (each wrapped in parentheses)
        row_re = re.compile(r'\(([^()]*(?:\([^()]*\)[^()]*)*)\)')
        for row_match in row_re.finditer(block):
            rows.append(parse_values(row_match.group(1)))
    return rows


def safe_str(val):
    return str(val).strip() if val is not None else ''


def safe_date(val):
    if not val or str(val).strip() in ('', 'NULL', 'None', '0000-00-00'):
        return None
    return str(val).strip()


def import_all():
    print(f"Leyendo {SQL_FILE}...")
    with open(SQL_FILE, encoding='utf-8') as f:
        content = f.read()

    # ── Ciclos ────────────────────────────────────────────────────────────────
    # Schema: id_ciclo, CICLO, PREPARACION
    print("\nImportando ciclos...")
    ciclos = extract_inserts(content, 'ciclos')
    print(f"  Encontrados: {len(ciclos)}")
    ok = 0
    with transaction.atomic():
        for row in ciclos:
            if len(row) < 2:
                continue
            try:
                Ciclo.objects.update_or_create(
                    id=row[0],
                    defaults={'ciclo': safe_str(row[1]), 'preparacion': safe_str(row[2]) if len(row) > 2 else ''}
                )
                ok += 1
            except Exception as e:
                print(f"  ERROR ciclo id={row[0]}: {e}")
    print(f"  Importados: {ok}")

    # ── Alumnos ───────────────────────────────────────────────────────────────
    # Schema: id_alumno, DNI, APELLIDOS, NOMBRE, FECHA_NTO, DIRECCION, POBLACION,
    #         CODIGO_POSTAL, TLF_CASA, TLF_MOVIL, ANO_CURSO, id_ciclo, GRADO,
    #         TURNO, NUM_ALUMNO, TUTOR_FCT?, OBS?
    VALID_GRADOS = {'GS', 'GM', 'B', 'FPB'}
    VALID_TURNOS = {'M', 'T', 'O'}

    print("\nImportando alumnos...")
    alumnos = extract_inserts(content, 'datos_alumnos')
    print(f"  Encontrados: {len(alumnos)}")
    ok = skipped = 0
    seen_dni = set()

    with transaction.atomic():
        for row in alumnos:
            if len(row) < 14:
                skipped += 1
                continue
            alumno_id, dni, apellidos, nombre = row[0], row[1], row[2], row[3]
            fecha_nto = safe_date(row[4])
            poblacion = safe_str(row[6])
            tlf_movil = safe_str(row[9])
            curso = safe_str(row[10])
            ciclo_id = row[11] if row[11] else None
            grado = safe_str(row[12])
            turno = safe_str(row[13])
            num_alumno = safe_str(row[14]) if len(row) > 14 else ''
            obs = safe_str(row[16]) if len(row) > 16 else ''

            if not dni or dni in seen_dni:
                skipped += 1
                continue
            seen_dni.add(dni)

            if grado not in VALID_GRADOS:
                grado = None
            if turno not in VALID_TURNOS:
                turno = None

            ano = 'Segundo' if grado in ('GS', 'CFGS') else 'Primero'

            try:
                Alumno.objects.update_or_create(
                    id=alumno_id,
                    defaults=dict(
                        nombre=safe_str(nombre),
                        apellidos=safe_str(apellidos),
                        dni=safe_str(dni),
                        fecha_nto=fecha_nto,
                        poblacion=poblacion,
                        tlf_movil=tlf_movil,
                        ciclo_id=ciclo_id,
                        curso=curso,
                        ano=ano,
                        grado=grado,
                        turno=turno,
                        num_alumno=num_alumno,
                        obs=obs,
                    )
                )
                ok += 1
            except Exception as e:
                print(f"  ERROR alumno id={alumno_id} dni={dni}: {e}")
                skipped += 1

    print(f"  Importados: {ok}  |  Omitidos: {skipped}")

    # ── Empresas ──────────────────────────────────────────────────────────────
    # Schema: id_convenio, EMPRESA, NIF_CIF_EMPRESA, FECHA_CONVENIO,
    #         REPRESENTANTE_LEGAL, NIF_REPRESENTANTE, DIRECCION, LOCALIDAD,
    #         CODIGO_POSTAL, TXTTE_PUBLICO, PERSONA_CONTACTO, TUTOR_EMPRESA,
    #         TELEFONO, EMAIL?, PLAZAS?, ...
    print("\nImportando empresas...")
    empresas = extract_inserts(content, 'empresas')
    print(f"  Encontradas: {len(empresas)}")
    ok = skipped = 0
    seen_cif = set()

    with transaction.atomic():
        for row in empresas:
            if len(row) < 3:
                skipped += 1
                continue
            emp_id = row[0]
            nombre = safe_str(row[1])
            cif = safe_str(row[2])
            fecha_convenio = safe_date(row[3]) if len(row) > 3 else None
            representante = safe_str(row[4]) if len(row) > 4 else ''
            direccion = safe_str(row[6]) if len(row) > 6 else ''
            ciudad = safe_str(row[7]) if len(row) > 7 else ''
            cp = safe_str(row[8]) if len(row) > 8 else ''
            contacto = safe_str(row[10]) if len(row) > 10 else ''
            tutor_empresa = safe_str(row[11]) if len(row) > 11 else ''
            tel = safe_str(row[12]) if len(row) > 12 else ''
            email = safe_str(row[13]) if len(row) > 13 else ''
            plazas = 2
            try:
                plazas = int(row[14]) if len(row) > 14 and row[14] else 2
            except (ValueError, TypeError):
                pass

            if not cif or cif in seen_cif:
                skipped += 1
                continue
            seen_cif.add(cif)

            try:
                Empresa.objects.update_or_create(
                    id=emp_id,
                    defaults=dict(
                        nombre=nombre,
                        cif=cif,
                        fecha_convenio=fecha_convenio,
                        representante=representante,
                        direccion=direccion,
                        ciudad=ciudad,
                        cp=cp,
                        contacto=contacto,
                        tutor_empresa=tutor_empresa,
                        tel=tel,
                        email=email if email else None,
                        plazas=plazas,
                    )
                )
                ok += 1
            except Exception as e:
                print(f"  ERROR empresa id={emp_id} cif={cif}: {e}")
                skipped += 1

    print(f"  Importadas: {ok}  |  Omitidas: {skipped}")

    # ── Asignaciones (detalle_alumnos) ────────────────────────────────────────
    # Schema: id_detalle, id_alumno, id_convenio, ANEXO, INICIO_FCT, FIN_FCT,
    #         HORAS_REALIZADAS, HORAS_1_SEM, HORAS_2_SEM, FCT_FINALIZADA,
    #         RDO_FCT, CONVALIDACION_RECIBIDA, INSERCION_LABORAL, VISITA_REALIZADA,
    #         FECHA_FIRMA?, TUTOR_CENTRO?
    print("\nImportando asignaciones...")
    asignaciones = extract_inserts(content, 'detalle_alumnos')
    print(f"  Encontradas: {len(asignaciones)}")
    ok = skipped = 0
    alumno_ids = set(Alumno.objects.values_list('id', flat=True))
    empresa_ids = set(Empresa.objects.values_list('id', flat=True))

    with transaction.atomic():
        for row in asignaciones:
            if len(row) < 6:
                skipped += 1
                continue
            asig_id = row[0]
            alumno_id = row[1]
            empresa_id = row[2]
            obs = safe_str(row[3]) if len(row) > 3 else ''
            inicio = safe_date(row[4]) if len(row) > 4 else None
            fin = safe_date(row[5]) if len(row) > 5 else None

            if not inicio or not fin:
                skipped += 1
                continue
            if alumno_id not in alumno_ids or empresa_id not in empresa_ids:
                skipped += 1
                continue

            try:
                horas = int(row[6]) if len(row) > 6 and row[6] else 400
            except (ValueError, TypeError):
                horas = 400

            fecha_firma = safe_date(row[14]) if len(row) > 14 else None
            tutor_centro = safe_str(row[15]) if len(row) > 15 else ''

            try:
                Asignacion.objects.update_or_create(
                    id=asig_id,
                    defaults=dict(
                        alumno_id=alumno_id,
                        empresa_id=empresa_id,
                        tutor_centro=tutor_centro,
                        inicio=inicio,
                        fin=fin,
                        horas=horas,
                        horas_comp=0,
                        obs=obs,
                        fecha_firma=fecha_firma,
                    )
                )
                ok += 1
            except Exception as e:
                print(f"  ERROR asignacion id={asig_id}: {e}")
                skipped += 1

    print(f"  Importadas: {ok}  |  Omitidas: {skipped}")

    # ── Actualizar secuencias de auto-incremento ──────────────────────────────
    from django.db import connection as conn
    if 'sqlite' in conn.vendor:
        import sqlite3 as _sqlite3
        db_path = str(conn.settings_dict['NAME'])
        print("\nActualizando secuencias SQLite...")
        raw = _sqlite3.connect(db_path)
        rc = raw.cursor()
        for table in ('gestion_alumno', 'gestion_empresa', 'gestion_asignacion', 'gestion_ciclo'):
            rc.execute(f'SELECT MAX(id) FROM "{table}"')
            max_id = rc.fetchone()[0]
            if max_id:
                rc.execute(
                    "INSERT OR REPLACE INTO sqlite_sequence (name, seq) VALUES (?, ?)",
                    (table, max_id)
                )
                print(f"  {table}: siguiente ID será {max_id + 1}")
        raw.commit()
        raw.close()
    elif 'postgresql' in conn.vendor:
        print("\nActualizando secuencias PostgreSQL...")
        with conn.cursor() as cursor:
            for table in ('gestion_alumno', 'gestion_empresa', 'gestion_asignacion', 'gestion_ciclo'):
                cursor.execute(
                    f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), COALESCE(MAX(id), 1)) FROM \"{table}\""
                )
                next_id = cursor.fetchone()[0]
                print(f"  {table}: secuencia reiniciada a {next_id}")

    print("\n¡Importación completa!")


if __name__ == '__main__':
    import_all()
