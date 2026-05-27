"""
Importa alumnos, empresas y asignaciones desde los arrays JS del HTML original.
Ejecutar desde la raíz del proyecto:  python import_from_html.py
"""
import os, sys, re, json, django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'teide_iv.settings')
django.setup()

from django.db import transaction
from gestion.models import Alumno, Empresa, Asignacion, Ciclo

HTML_FILE = 'FCT_Final (2).html'

VALID_GRADOS = {'GS', 'GM', 'B', 'FPB'}
VALID_TURNOS = {'M', 'T', 'O'}


def safe_str(v):
    return str(v).strip() if v else ''


def safe_date(v):
    s = str(v).strip() if v else ''
    if not s or s in ('None', 'NULL', '0000-00-00', 'null'):
        return None
    # acepta YYYY-MM-DD o DD/MM/YYYY
    if re.match(r'^\d{4}-\d{2}-\d{2}$', s):
        return s
    m = re.match(r'^(\d{2})/(\d{2})/(\d{4})$', s)
    if m:
        return f'{m.group(3)}-{m.group(2)}-{m.group(1)}'
    return None


def extract_array(content, varname):
    """Extrae el array JS asignado a 'let <varname> = [...]'."""
    pattern = rf'let\s+{re.escape(varname)}\s*=\s*(\[.*?\]);'
    m = re.search(pattern, content, re.DOTALL)
    if not m:
        raise ValueError(f"No se encontró el array '{varname}' en el HTML")
    return json.loads(m.group(1))


def get_or_create_ciclo(nombre):
    if not nombre:
        return None
    obj, _ = Ciclo.objects.get_or_create(
        ciclo__iexact=nombre,
        defaults={'ciclo': nombre.strip()}
    )
    return obj


# ── LEER HTML ─────────────────────────────────────────────────────────────────

print(f"Leyendo {HTML_FILE}...")
with open(HTML_FILE, encoding='utf-8') as f:
    content = f.read()

alumnos_data   = extract_array(content, 'alumnos')
empresas_data  = extract_array(content, 'empresas')
asig_data      = extract_array(content, 'asignaciones')

print(f"  alumnos: {len(alumnos_data)}")
print(f"  empresas: {len(empresas_data)}")
print(f"  asignaciones: {len(asig_data)}")


# ── 1. ALUMNOS ────────────────────────────────────────────────────────────────

print("\nImportando alumnos...")
ok = skipped = errors = 0
seen_dni = set(Alumno.objects.values_list('dni', flat=True))

with transaction.atomic():
    for a in alumnos_data:
        dni = safe_str(a.get('dni'))
        if not dni or dni in seen_dni:
            skipped += 1
            continue
        seen_dni.add(dni)

        grado = safe_str(a.get('grado'))
        turno = safe_str(a.get('turno'))
        if grado not in VALID_GRADOS:
            grado = None
        if turno not in VALID_TURNOS:
            turno = None

        ciclo_obj = get_or_create_ciclo(safe_str(a.get('ciclo')))
        ano = 'Segundo' if grado in ('GS', 'CFGS') else 'Primero'

        try:
            Alumno.objects.update_or_create(
                id=a['id'],
                defaults=dict(
                    dni=dni,
                    nombre=safe_str(a.get('nombre')),
                    apellidos=safe_str(a.get('apellidos')),
                    fecha_nto=safe_date(a.get('fecha_nto')),
                    poblacion=safe_str(a.get('poblacion')),
                    tlf_movil=safe_str(a.get('tel')),
                    ciclo=ciclo_obj,
                    curso=safe_str(a.get('curso')),
                    ano=ano,
                    grado=grado,
                    turno=turno,
                    num_alumno=safe_str(a.get('num_alumno')),
                    obs=safe_str(a.get('obs')),
                )
            )
            ok += 1
        except Exception as e:
            print(f"  ERROR alumno id={a.get('id')} dni={dni}: {e}")
            errors += 1

print(f"  OK: {ok}  |  Omitidos (DNI duplicado): {skipped}  |  Errores: {errors}")


# ── 2. EMPRESAS ───────────────────────────────────────────────────────────────

print("\nImportando empresas...")
ok = skipped = errors = 0
seen_cif = set(Empresa.objects.values_list('cif', flat=True))

with transaction.atomic():
    for e in empresas_data:
        cif = safe_str(e.get('cif'))
        if not cif or cif in seen_cif:
            skipped += 1
            continue
        seen_cif.add(cif)

        try:
            plazas = int(e.get('plazas') or 2)
        except (ValueError, TypeError):
            plazas = 2

        try:
            Empresa.objects.update_or_create(
                id=e['id'],
                defaults=dict(
                    nombre=safe_str(e.get('nombre')),
                    cif=cif,
                    representante=safe_str(e.get('representante')),
                    direccion=safe_str(e.get('direccion')),
                    ciudad=safe_str(e.get('ciudad')),
                    cp=safe_str(e.get('cp')),
                    contacto=safe_str(e.get('contacto')),
                    tutor_empresa=safe_str(e.get('tutor_empresa')),
                    tel=safe_str(e.get('tel')),
                    email=safe_str(e.get('email')) or None,
                    plazas=plazas,
                )
            )
            ok += 1
        except Exception as ex:
            print(f"  ERROR empresa id={e.get('id')} cif={cif}: {ex}")
            errors += 1

print(f"  OK: {ok}  |  Omitidas (CIF duplicado): {skipped}  |  Errores: {errors}")


# ── 3. ASIGNACIONES ───────────────────────────────────────────────────────────

print("\nImportando asignaciones...")
ok = skipped = errors = 0

alumno_ids  = set(Alumno.objects.values_list('id', flat=True))
empresa_ids = set(Empresa.objects.values_list('id', flat=True))

with transaction.atomic():
    for a in asig_data:
        al_id  = a.get('alumnoId')
        em_id  = a.get('empresaId')
        inicio = safe_date(a.get('inicio'))
        fin    = safe_date(a.get('fin'))

        if not inicio or not fin:
            skipped += 1
            continue
        if al_id not in alumno_ids or em_id not in empresa_ids:
            skipped += 1
            continue

        try:
            horas = int(a.get('horas') or 400)
        except (ValueError, TypeError):
            horas = 400

        try:
            Asignacion.objects.update_or_create(
                id=a['id'],
                defaults=dict(
                    alumno_id=al_id,
                    empresa_id=em_id,
                    tutor_centro='',
                    inicio=inicio,
                    fin=fin,
                    horas=horas,
                    horas_comp=0,
                    obs=safe_str(a.get('obs')),
                    fecha_firma=None,
                )
            )
            ok += 1
        except Exception as ex:
            print(f"  ERROR asig id={a.get('id')}: {ex}")
            errors += 1

print(f"  OK: {ok}  |  Omitidas (FK no existe / sin fechas): {skipped}  |  Errores: {errors}")


# ── 4. RESET DE SECUENCIAS ────────────────────────────────────────────────────

from django.db import connection as conn

print("\nReseteando secuencias...")
if 'sqlite' in conn.vendor:
    import sqlite3 as _sq
    db_path = str(conn.settings_dict['NAME'])
    raw = _sq.connect(db_path)
    rc = raw.cursor()
    for table in ('gestion_alumno', 'gestion_empresa', 'gestion_asignacion', 'gestion_ciclo'):
        rc.execute(f'SELECT MAX(id) FROM "{table}"')
        max_id = rc.fetchone()[0]
        if max_id:
            rc.execute(
                "INSERT OR REPLACE INTO sqlite_sequence (name, seq) VALUES (?, ?)",
                (table, max_id)
            )
            print(f"  {table}: siguiente ID = {max_id + 1}")
    raw.commit()
    raw.close()
elif 'postgresql' in conn.vendor:
    from django.core.management import call_command
    import io
    out = io.StringIO()
    call_command('sqlsequencereset', 'gestion', stdout=out)
    sql = out.getvalue()
    with conn.cursor() as cur:
        cur.execute(sql)
    print("  Secuencias PostgreSQL reseteadas con sqlsequencereset")

print("\n¡Importación completa!")
