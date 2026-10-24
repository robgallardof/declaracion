# Runbook: declaración mensual RESICO PF en el nuevo portal DyP

## Reglas de navegación (por incidentes reales)
- **Nunca presentes un mes que no ha terminado.** El portal ofrece el periodo, pero al abrir ISR sale "Guardando información… Formularios no enviados", se queda colgado y los selects se resetean (septiembre 2026, probado el 24-sep, dos veces).
- Clics en botones de navegación o de modales: con `find` + `ref`, no por coordenadas. Screenshot después de cada cambio de pantalla.
- Si aparece el modal "Cantidad a pagar… ¿Desea continuar?" sin el OK del usuario: **no toques nada**; navega a la URL del formulario para salir.
- "Guardando información" es el autoguardado y suele durar 1-3 s. Si dura más de 20 s, recarga la URL del formulario; si se repite, detente y avisa.
- La sesión dura unos 30-60 min. Si aparece el login, el usuario vuelve a entrar.

Probado en septiembre de 2026 (declaración en 0). Versión del portal: 24.0.0.

## URLs (usar SIEMPRE el portal nuevo)
| Qué | URL |
|---|---|
| Portal nuevo DyP (RESICO) | `https://pstcdypisr.clouda.sat.gob.mx/` |
| Configurar declaración | `https://pstcdypisr.clouda.sat.gob.mx/Declaracion/Temporales` → redirige a `/Declaracion/PerfilDeclaracion` |
| Formulario directo | herramienta `url_declaracion(AAAA, M)` (CLI: `declara url AAAA M`) → `/Formulario/Formulario?data=<base64 JSON>` |
| Consulta por obligación (presentadas) | `https://pstcdypisr.clouda.sat.gob.mx/Consulta/Consulta?tipoDocumento=4` |
| Acuse (se abre solo después de enviar) | `/Recepcion/AcuseDeclaracion?data=...` |
| Portal VIEJO (no sirve para RESICO) | `ptscdecprov.clouda.sat.gob.mx`: solo tiene la liga "Nuevo portal de pagos provisionales" |

Login: si al abrir la URL aparece `loginda.siat.sat.gob.mx` o `cfdiau.sat.gob.mx`, **el usuario** inicia sesión con e.firma y avisa con "listo".
El portal de facturas (`portalcfdi...`) pide **otro** login; evítalo si basta con lo que precarga DyP.

## JSON del parámetro `data`
```json
{"tipopersona":"A","regimen":38,"ejercicio":"2026","periodicidad":"M","periodo":"008","periodoDesc":"Agosto",
 "fechaCausacion":"","tipoDeclaracion":"001","tipoDeclaracionDesc":"Normal","tipoComplementaria":"",
 "tipoComplementariaDesc":"","obligaciones":["0168","0318"]}
```
- `regimen` 38 = RESICO PF. `0168` = ISR simplificado de confianza PF. `0318` = IVA simplificado de confianza.
- `tipoDeclaracion`: 001 Normal, 002 Complementaria, 003 Normal por corrección fiscal.

## Flujo manual (si la URL directa falla)
En PerfilDeclaracion, los selects se llenan con `form_input`, en cadena: Ejercicio → Periodicidad `1-Mensual` → Periodo (`Agosto`) → Tipo `Normal`.
Aparecen las obligaciones ya marcadas (ISR simplificado + IVA simplificado) → botón **SIGUIENTE**. Tarda 10-20 s ("Cargando información").

## Modal de precarga (al entrar al formulario)
Muestra "Pagos provisionales con fecha de corte" y "Facturas emitidas de tipo ingreso, egreso y pago": o dice **"No existe información"** o trae montos.
**Léelo con get_page_text y anótalo en `calculo.md`**, porque es la validación cruzada contra los comprobantes. Luego **CERRAR**.
También trae el **vencimiento** (arriba a la derecha): anótalo.

## ISR simplificado de confianza (clic en su círculo)
Pestaña **Ingresos**:
- `¿Los ingresos fueron obtenidos a través de copropiedad?` → select, valor `2` = No.
- `Total de ingresos efectivamente cobrados` → precargado, solo lectura. Si no cuadra con `calculo.md`, **PARA** y reporta.
- `Descuentos, devoluciones y bonificaciones` → marca error hasta que abras **CAPTURAR** y llenes `Descuentos... de integrantes por copropiedad` = 0 → CERRAR.
- `¿Tienes ingresos adicionales?` → `2` = No (o Sí y capturar el monto si hay ingresos sin CFDI).

Pestaña **Determinación**:
- Tasa aplicable e impuesto mensual: los calcula el portal. Compáralos con `calcular_resico`.
- `ISR retenido por personas morales` → **VER DETALLE**. Dentro: `ISR retenido no acreditable` = 0 (obligatorio aunque sea 0), `ISR retenido a adicionar` si hay retención sin CFDI → CERRAR.

Pestaña **Pago**: solo lectura (A cargo, Total de aplicaciones, Cantidad a pagar). Si hay compensaciones o estímulos, se capturan aquí.

→ **ADMINISTRACIÓN DE LA DECLARACIÓN** para volver.

## IVA simplificado de confianza
Pestaña **Determinación**:
- `Actividades gravadas 16%`, `0%`, `exentas`, `no objeto` → precargadas desde CFDI (VER DETALLE / CAPTURAR).
- `IVA retenido` → VER DETALLE (precarga).
- `*IVA acreditable del periodo` → **CAPTURAR** (obligatorio). Modal:
  - `IVA pagado en gastos y adquisiciones` (precarga de facturas recibidas, solo lectura).
  - `*IVA acreditable por actividades gravadas 16%/8%/0%` → monto (0 si no hay).
  - `*IVA acreditable por actividades mixtas` → 0 salvo proporción.
  - `IVA no acreditable` → opcional.
  - Tip: el primer `type` a veces no se registra. Usa triple_click + type + Tab y verifica con zoom.
- `Cantidad a cargo` / `Impuesto a cargo` → calculados. **Si da negativo = saldo a favor del mes**: anótalo en `saldos.json`.

Pestaña **Pago**: aquí se aplican los **saldos a favor de periodos anteriores** (Total de aplicaciones). Pendiente de documentar con un caso real: al primer mes con IVA a cargo y saldo a favor, capturar pantallas y completar esta sección.

## Envío
1. Administración de la declaración → debe mostrar ✔ en ambas obligaciones y **Total a pagar**.
2. Screenshot con `save_to_disk` → copia a `AAAA/MM-mes/acuse/previa_envio.jpg`. **PAUSA: pedir el OK del usuario.**
3. **ENVIAR DECLARACIÓN** → modal "Declaro bajo protesta..." → **SI**.
4. `/Recepcion/AcuseDeclaracion` tarda 20-40 s en mostrar el PDF. La URL trae `"errores":true` aunque todo esté bien; **no significa rechazo**. Lo que cuenta es el número de operación del acuse.
5. Descarga el acuse y la declaración completa con la sección **"Descarga masiva"** (más abajo): nombres claros, directo a `MM-mes/acuse/`. (El botón DESCARGAR también sirve, pero cae como `~/Downloads/Acuse.<RFC>.38.AAAA.pdf`, sin el mes.)
6. Si hubo pago: la línea de captura viene en el acuse (hoja 1: línea, importe, "Vigente hasta"). Repórtala y anótala en `declaraciones_presentadas.md`.
7. La consulta por obligación puede tardar varios minutos en mostrar la nueva declaración. **No reenvíes** por eso.

## Consulta de declaraciones presentadas (rápido, por JS)
En `/Consulta/Consulta?tipoDocumento=4`:
```js
for (const [id,v] of [['Ejercicio','2026'],['Periodicidad','M']]) { const s=document.getElementById(id); s.value=v; s.dispatchEvent(new Event('change',{bubbles:true})); }
await new Promise(r=>setTimeout(r,1000));
[...document.querySelectorAll('a,button')].find(e=>e.textContent.trim()==='Buscar Conceptos').click();
await new Promise(r=>setTimeout(r,4000));
document.getElementById('0318').click();   // o '0168' para ISR
[...document.querySelectorAll('a,button')].find(e=>e.textContent.trim()==='Buscar').click();
await new Promise(r=>setTimeout(r,5000));
[...document.querySelectorAll('table tr')].map(r=>[...r.cells].map(c=>c.textContent.trim()).join(' | '))
```
Actualiza `AAAA/declaraciones_presentadas.md` con el resultado.

## Selects en el formulario
Los selects Sí/No no tienen ref útil: `document.querySelectorAll('select')` visibles → `value='2'` + `dispatchEvent(new Event('change',{bubbles:true}))`. Funcionó y el portal lo validó.

## Consultas (tipoDocumento)
- `?tipoDocumento=1`: **declaración completa** (PDF con ingresos, tasa, IVA trasladado/acreditable, a favor). El clic en el icono no funciona bien: usa la "Descarga masiva".
- `?tipoDocumento=3` = **acuse** (hoja 1: totales y línea de captura).
- `?tipoDocumento=2`: Declaraciones pagadas.
- `?tipoDocumento=3`: Reimpresión del acuse.
- `?tipoDocumento=4`: Por obligación (la más útil; su columna Estado es confiable: "Vigente").
- ⚠️ En `tipoDocumento=1` la columna Estado dice **"Anulada" en todas**, incluso en una recién presentada y vigente. **No es confiable**: usa la 4.
- Filtros por JS: ids `Ejercicio`, `Periodicidad` (M), `Periodo` (001-012, se llena después de Periodicidad), `NumeroOperacion`, `TipoDeclaracion`.

## Descarga masiva de acuses y declaraciones (probado)
Requisito: Chrome con **descargas automáticas permitidas** para `pstcdypisr.clouda.sat.gob.mx` (el usuario ya lo activó). Si no, Chrome bloquea en silencio a partir de la segunda descarga.
En `?tipoDocumento=3` (acuses) o `?tipoDocumento=1` (declaraciones): filtra por Ejercicio + Periodicidad (sin periodo = todos) → Buscar → ejecuta:
```js
const pref='acuse'; // o 'declaracion' en tipoDocumento=1
const mes={Enero:'01',Febrero:'02',Marzo:'03',Abril:'04',Mayo:'05',Junio:'06',Julio:'07',Agosto:'08',Septiembre:'09',Octubre:'10',Noviembre:'11',Diciembre:'12'};
const out=[];
for (const row of [...document.querySelectorAll('table tr')].filter(r=>/\d{12}/.test(r.textContent))) {
  const c=[...row.cells].map(x=>x.textContent.trim()); // c[1]=operación c[2]=tipo c[7]=periodo
  const b=await (await fetch(row.cells[0].querySelector('a').href,{credentials:'include'})).blob();
  const d=document.createElement('a'); d.href=URL.createObjectURL(b);
  d.download=`${pref}_2026-${mes[c[7]]}_${c[2].toLowerCase().replace(/ /g,'-')}_${c[1]}.pdf`;
  document.body.appendChild(d); d.click(); d.remove(); out.push(d.download);
  await new Promise(r=>setTimeout(r,2000));
}
out
```
Luego, en bash, mueve de `~/Downloads/<pref>_AAAA-MM_*.pdf` a `AAAA/MM-*/acuse/` (el mes está en las posiciones 11-12 de `acuse_` y 17-18 de `declaracion_`).
Para leerlos: herramienta `leer_acuses(AAAA)` (usa `pypdf` y corrige ligaduras como "ﬁ").

## Declaraciones pagadas
`?tipoDocumento=2` lista **solo las pagadas**. Una declaración con línea de captura que no aparece ahí = **no pagada**. Si su "Vigente hasta" ya pasó, hay que generar una nueva línea (complementaria del mes, con recargos actualizados).

## Complementaria (probado en 2026)
Sirve para **obtener una línea de captura nueva** cuando la anterior venció sin pagarse, o para corregir datos.
- PerfilDeclaracion (ids en minúsculas): `ejercicio`, `periodicidad`=M, `periodos`=005, `tipodeclaracion`=002 (Complementaria), `tipocomplementaria`=**003 Modificación de Obligaciones** (002 = Dejar sin efecto obligación, 004 = Obligación no presentada). Usa change + 2.5 s de espera entre cada uno.
- La complementaria **precarga el ISR** de la original (ingresos adicionales, tasa), pero **en IVA NO precarga "Actividades gravadas a la tasa del 16%"**: hay que recapturarlas. Compara SIEMPRE contra `declaracion_...pdf` de la original.
- ISR, pestaña Pago: se piden `Parte actualizada` (0 si el monto es chico), `Recargos` (viene el de la original), `¿Tienes compensaciones?`=No y `¿Realizó en las últimas 48 horas un pago para este concepto?`=No. Son selects: `document.querySelectorAll('select')` visibles, value '2'.
- La nueva línea de captura sale en el acuse (hoja 2) con vigencia de unas 2 semanas.

## ⚠️ Incidente: se envió sin confirmación (24-sep-2026)
Después de ir a "Administración de la declaración" con un clic por coordenadas, apareció el modal final "Cantidad a pagar… ¿Desea continuar?". Se hizo clic en **NO** y **aun así se envió**.
Reglas desde ahora:
1. Después de cualquier clic que cambie de pantalla, **screenshot antes del siguiente clic**. Nada de clics encadenados a ciegas en el formulario.
2. Para volver a Administración, usa `find("botón ADMINISTRACIÓN DE LA DECLARACIÓN")` + ref, no coordenadas.
3. Si aparece el modal de envío sin OK del usuario: **no toques ningún botón**. Recarga con navigate a la misma URL del formulario (el borrador se conserva en "Temporales") y avisa.
