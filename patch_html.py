"""Apply all frontend fixes to FCT_Final.html"""

HTML = r'c:\Users\Usuario\Desktop\proyecto teide\TeideIV-main\gestion\templates\FCT_Final.html'

with open(HTML, encoding='utf-8') as f:
    content = f.read()

original_len = len(content)

replacements = []

# ── 1. Fix edAl: a.tel → a.tlf_movil and ciclo → ciclo_nombre
replacements.append((
    " sv('al-t',a.tel);sv('al-e',a.email);sv('al-fn',a.fecha_nto);sv('al-p',a.poblacion);\n sv('al-c',a.ciclo);",
    " sv('al-t',a.tlf_movil||a.tel||'');sv('al-e',a.email);sv('al-fn',a.fecha_nto);sv('al-p',a.poblacion);\n sv('al-c',a.ciclo_nombre||a.ciclo||'');"
))

# ── 2. Fix delAl → async API call
replacements.append((
    "function delAl(id){\n if(!confirm('¿Eliminar este alumno y sus asignaciones?'))return;\n alumnos=alumnos.filter(a=>a.id!==id);\n asignaciones=asignaciones.filter(a=>a.alumnoId!==id);\n renderAll();toast('Alumno eliminado','ok');\n}",
    "async function delAl(id){\n if(!confirm('¿Eliminar este alumno y sus asignaciones?'))return;\n try{\n  const res=await fetch(`/api/alumno/borrar/${id}/`,{method:'DELETE',headers:{'X-CSRFToken':getCookie('csrftoken')}});\n  if(res.ok){\n   alumnos=alumnos.filter(a=>a.id!==id);\n   asignaciones=asignaciones.filter(a=>a.alumnoId!==id);\n   renderAll();toast('Alumno eliminado','ok');\n  }else{toast('Error al eliminar el alumno','err');}\n }catch(e){toast('Error de conexión','err');}\n}"
))

# ── 3. Fix saveEm → async API call
replacements.append((
    "function saveEm(){\n const id=gv('em-eid');\n const o={nombre:gv('em-n'),cif:gv('em-c'),representante:gv('em-r'),direccion:gv('em-d'),ciudad:gv('em-ci'),cp:gv('em-cp'),contacto:gv('em-ct'),tutor_empresa:gv('em-tu'),tel:gv('em-t'),email:gv('em-e'),fecha_convenio:gv('em-fc'),plazas:parseInt(gv('em-p'))||2};\n if(!o.nombre||!o.cif){toast('Rellena los campos obligatorios (*)','err');return}\n if(id){Object.assign(empresas.find(x=>x.id==id),o);toast('Empresa actualizada ','ok')}\n else{empresas.push({id:emSeq++,...o});toast('Empresa añadida ','ok')}\n closeM('modal-em');renderAll();\n}",
    "async function saveEm(){\n const id=gv('em-eid');\n const o={nombre:gv('em-n'),cif:gv('em-c'),representante:gv('em-r'),direccion:gv('em-d'),ciudad:gv('em-ci'),cp:gv('em-cp'),contacto:gv('em-ct'),tutor_empresa:gv('em-tu'),tel:gv('em-t'),email:gv('em-e'),fecha_convenio:gv('em-fc')||null,plazas:parseInt(gv('em-p'))||2};\n if(!o.nombre||!o.cif){toast('Rellena los campos obligatorios (*)','err');return}\n const url=id?`/api/empresa/editar/${id}/`:'/api/empresa/crear/';\n const method=id?'PUT':'POST';\n try{\n  const res=await fetch(url,{method,headers:{'Content-Type':'application/json','X-CSRFToken':getCookie('csrftoken')},body:JSON.stringify(o)});\n  if(res.ok){\n   const saved=await res.json();\n   if(id){Object.assign(empresas.find(x=>x.id==id),saved);toast('Empresa actualizada','ok');}\n   else{empresas.push(saved);toast('Empresa añadida','ok');}\n   closeM('modal-em');renderAll();\n  }else{toast('Error al guardar la empresa','err');}\n }catch(e){toast('Error de conexión','err');}\n}"
))

# ── 4. Fix delEm → async API call
replacements.append((
    "function delEm(id){\n if(!confirm('¿Eliminar esta empresa?'))return;\n empresas=empresas.filter(e=>e.id!==id);\n asignaciones=asignaciones.filter(a=>a.empresaId!==id);\n renderAll();toast('Empresa eliminada','ok');\n}",
    "async function delEm(id){\n if(!confirm('¿Eliminar esta empresa?'))return;\n try{\n  const res=await fetch(`/api/empresa/borrar/${id}/`,{method:'DELETE',headers:{'X-CSRFToken':getCookie('csrftoken')}});\n  if(res.ok){\n   empresas=empresas.filter(e=>e.id!==id);\n   asignaciones=asignaciones.filter(a=>a.empresaId!==id);\n   renderAll();toast('Empresa eliminada','ok');\n  }else{toast('Error al eliminar la empresa','err');}\n }catch(e){toast('Error de conexión','err');}\n}"
))

# ── 5. Fix saveAs → async API call with field mapping
replacements.append((
    "function saveAs(){\n const id=gv('as-eid');\n const o={alumnoId:parseInt(gv('as-al')),empresaId:parseInt(gv('as-em')),tutor:gv('as-tu'),inicio:gv('as-ini'),fin:gv('as-fin'),horas:parseInt(gv('as-h'))||400,horasComp:parseInt(gv('as-hc'))||0,obs:gv('as-o'),fechaFirma:gv('as-firma')};\n if(!o.alumnoId||!o.empresaId||!o.inicio||!o.fin){toast('Rellena los campos obligatorios','err');return}\n if(id){Object.assign(asignaciones.find(x=>x.id==id),o);toast('Asignación actualizada ','ok')}\n else{asignaciones.push({id:asigSeq++,...o});toast('Asignación creada ','ok')}\n closeM('modal-asig');renderAll();\n}",
    "async function saveAs(){\n const id=gv('as-eid');\n const o={alumnoId:parseInt(gv('as-al')),empresaId:parseInt(gv('as-em')),tutor:gv('as-tu'),inicio:gv('as-ini'),fin:gv('as-fin'),horas:parseInt(gv('as-h'))||400,horasComp:parseInt(gv('as-hc'))||0,obs:gv('as-o'),fechaFirma:gv('as-firma')||null};\n if(!o.alumnoId||!o.empresaId||!o.inicio||!o.fin){toast('Rellena los campos obligatorios','err');return}\n const apiData={alumno:o.alumnoId,empresa:o.empresaId,tutor_centro:o.tutor,inicio:o.inicio,fin:o.fin,horas:o.horas,horas_comp:o.horasComp,obs:o.obs,fecha_firma:o.fechaFirma};\n const url=id?`/api/asignacion/editar/${id}/`:'/api/asignacion/crear/';\n const method=id?'PUT':'POST';\n try{\n  const res=await fetch(url,{method,headers:{'Content-Type':'application/json','X-CSRFToken':getCookie('csrftoken')},body:JSON.stringify(apiData)});\n  if(res.ok){\n   const saved=await res.json();\n   const norm=normalizeAsignacion(saved);\n   if(id){Object.assign(asignaciones.find(x=>x.id==id),norm);toast('Asignación actualizada','ok');}\n   else{asignaciones.push(norm);toast('Asignación creada','ok');}\n   closeM('modal-asig');renderAll();\n  }else{toast('Error al guardar la asignación','err');}\n }catch(e){toast('Error de conexión','err');}\n}"
))

# ── 6. Fix delAs → async API call
replacements.append((
    "function delAs(id){\n if(!confirm('¿Eliminar esta asignación?'))return;\n asignaciones=asignaciones.filter(a=>a.id!==id);\n renderAll();toast('Asignación eliminada','ok');\n}",
    "async function delAs(id){\n if(!confirm('¿Eliminar esta asignación?'))return;\n try{\n  const res=await fetch(`/api/asignacion/borrar/${id}/`,{method:'DELETE',headers:{'X-CSRFToken':getCookie('csrftoken')}});\n  if(res.ok){\n   asignaciones=asignaciones.filter(a=>a.id!==id);\n   renderAll();toast('Asignación eliminada','ok');\n  }else{toast('Error al eliminar la asignación','err');}\n }catch(e){toast('Error de conexión','err');}\n}"
))

# ── 7. Fix inicializarApp: use API as primary source + normalize asignaciones
replacements.append((
    "        if (response.ok) {\n            const data = await response.json();\n            if (data.alumnos) alumnos = dedupeByData([...alumnos, ...data.alumnos]);\n            if (data.empresas) empresas = dedupeByData([...empresas, ...data.empresas]);\n            if (data.asignaciones) asignaciones = dedupeAsignacionesVisual([...asignaciones, ...data.asignaciones]);\n        }",
    "        if (response.ok) {\n            const data = await response.json();\n            if (data.alumnos && data.alumnos.length > 0) alumnos = data.alumnos;\n            if (data.empresas && data.empresas.length > 0) empresas = data.empresas;\n            if (data.asignaciones) asignaciones = data.asignaciones.map(normalizeAsignacion);\n        }"
))

# ── 8. Add normalizeAsignacion function before dedupeAsignacionesVisual
replacements.append((
    "function dedupeAsignacionesVisual(rows){",
    "function normalizeAsignacion(a){\n return {\n  id:a.id,\n  alumnoId:a.alumnoId!==undefined?a.alumnoId:a.alumno,\n  empresaId:a.empresaId!==undefined?a.empresaId:a.empresa,\n  tutor:a.tutor!==undefined?a.tutor:(a.tutor_centro||''),\n  inicio:a.inicio,fin:a.fin,horas:a.horas,\n  horasComp:a.horasComp!==undefined?a.horasComp:(a.horas_comp||0),\n  obs:a.obs,\n  fechaFirma:a.fechaFirma!==undefined?a.fechaFirma:(a.fecha_firma||null)\n };\n}\n\nfunction dedupeAsignacionesVisual(rows){"
))

# Apply all replacements
for i, (old, new) in enumerate(replacements, 1):
    count = content.count(old)
    if count != 1:
        print(f"ERROR: replacement {i} found {count} times (expected 1)")
        # Show a bit of context
        idx = content.find(old[:50])
        if idx == -1:
            print(f"  First 50 chars: {repr(old[:50])}")
        continue
    content = content.replace(old, new)
    print(f"Replacement {i} applied OK")

print(f"\nOriginal size: {original_len} chars")
print(f"New size: {len(content)} chars")

with open(HTML, 'w', encoding='utf-8') as f:
    f.write(content)

print("File saved successfully!")
