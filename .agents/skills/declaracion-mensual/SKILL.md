---
name: declaracion-mensual
description: "Prepara y presenta la declaración provisional mensual RESICO (ISR + IVA) en el portal de Declaraciones y Pagos, incluidos el acreditamiento del IVA a favor, las declaraciones en 0, las complementarias y una nueva línea de captura cuando la anterior venció. Usar cuando el usuario diga 'declara <mes>', 'declara <mes> en 0', 'no he pagado <mes>' o deje comprobantes de un mes."
---

# Declaración mensual RESICO

Runbook del portal: skill `portal-fiscal` → `dyp-resico.md` (**léelo antes de tocar el navegador**).
Carpeta del mes: `AAAA/MM-mes/{comprobantes,facturas,acuse}` (`preparar_mes` la crea).

## 0. Pre-chequeo (sin navegador, mientras el usuario inicia sesión)
1. `estado_anio(AAAA)` + `leer_acuses(AAAA)` + `AAAA/declaraciones_presentadas.md`:
   - ¿El mes ya se presentó? → es **complementaria** (`url_declaracion(..., complementaria=true)`); avisa.
   - ¿Hay líneas de captura **no pagadas** o vencidas? → avisa.
2. **¿Ya terminó el mes?** Si no, **no lo presentes**: el autoguardado se cuelga y lo que entre después obliga a una
   complementaria. Propón hacerlo desde el día 1 del mes siguiente.
3. `vencimiento(AAAA, M)`: fecha estimada; manda la que muestra el formulario. Si ya pasó y hay impuesto → recargos.
4. Si `comprobantes/` está vacío → pregunta "No hay comprobantes de <mes>. ¿Seguro que quieres declarar en 0?" y **detente**.
5. Ingresos sin factura en `facturas/` → avisa y ofrece la skill `facturacion`.

## 1. Con comprobantes
1. `extractor-comprobantes` (CEP SPEI, XML con `leer_cfdi`, PDF) + `validador-cfdi`, en paralelo.
2. `valores_vigentes(AAAA)`: si algo no está verificado → `investigador-fiscal`.
3. `contador-mx` → `calculo.md` (ISR, IVA y saldo a favor desde `saldos.json`).
4. `auditor-fiscal` → si dice NO ENVIAR, corrige o pregunta.
5. Tabla al usuario: ingresos, ISR, IVA trasladado/acreditable/retenido, saldo a favor aplicado (con su origen), total y dudas.
6. Portal (runbook) → comparar con la precarga → screenshot `acuse/previa_envio.jpg` → **OK explícito** → Enviar.

## 2. Vía rápida: en 0 (unos 5 minutos, sin agentes)
`url_declaracion(AAAA, M)` → el aviso de precarga debe decir "No existe información" en facturas (si trae montos, PARA) →
ISR: copropiedad No · descuentos → CAPTURAR → copropiedad 0 · ingresos adicionales No · Determinación → VER DETALLE
en ISR retenido → no acreditable 0 → IVA: CAPTURAR IVA acreditable → 16%/8%/0% = 0 y mixtas = 0 → total $0 →
screenshot → **OK** → Enviar. `saldos.json` no cambia. `calculo.md` corto:

```markdown
# <Mes> AAAA — RESICO PF — declaración en 0
- Comprobantes: ninguno. El usuario pidió declarar en 0.
- Precarga: facturas emitidas → "No existe información". IVA pagado en gastos → 0.
- ISR: ingresos 0, retenciones 0, a cargo 0. IVA: gravado 0, acreditable 0, a cargo 0.
- Saldo a favor de IVA: no se aplica ni se genera.
- Total a pagar: $0. Vencimiento según el formulario: <fecha>.
## Presentada
- Número de operación: <n>. Fecha: <fecha hora>.
```

## 3. Línea de captura vencida o no pagada
Complementaria **"Modificación de Obligaciones"** con los mismos datos (sección Complementaria del runbook). Compárala
contra `declaracion_...pdf` de la original: **el IVA 16% no se precarga**. Se recalculan recargos y sale línea nueva
(vigencia de unas 2 semanas).

## 4. Cierre (siempre)
- Descarga masiva: acuse + declaración → `MM-mes/acuse/`.
- `leer_acuses(AAAA, como_tabla=true)` → actualiza `declaraciones_presentadas.md` (pagada: no, hasta que aparezca en pagadas).
- `saldos.json` si hubo IVA a favor o se aplicó alguno.
- Al usuario: **línea de captura, importe y vigencia** (o "$0, sin pago") y el número de operación.
