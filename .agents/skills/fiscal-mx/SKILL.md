---
name: fiscal-mx
description: "Capa fiscal de México para razonar bien: tipos de contribuyente, regímenes (RESICO, actividad empresarial/profesional, arrendamiento, sueldos, plataformas), ISR, IVA y saldos a favor, obligaciones mensuales y anuales, recargos y actualización, y coherencia de CFDI 4.0. Usar para calcular impuestos, explicar conceptos fiscales o validar facturas."
---

# Fiscalidad mexicana — guía conceptual

**Regla de oro: aquí no hay números.** Tasas, tarifas, UMA, INPC, tasa de recargos y calendarios cambian cada año.
Viven en `datos/vigentes-AAAA.json` (con fuente y fecha de verificación) y se calculan con las herramientas MCP
`calcular_resico`, `calcular_iva`, `desglosar_iva`, `calcular_recargos`, `tope_resico` (o la CLI `declara`).
- Si un valor falta o `verificado` es `false` → lanza el agente `investigador-fiscal` antes de calcular
  (`valores_vigentes` dice qué está verificado).
- No hagas aritmética fiscal a mano.

**Guardrails:** informa y calcula; el usuario decide. Las decisiones con consecuencias (enviar, timbrar, cambiar de
régimen, pedir devolución) necesitan su OK. En temas dudosos o de alto monto, recomienda consultar a un contador;
esto no es asesoría fiscal.

## Contribuyentes y regímenes (clave)
El régimen de cada usuario está en su perfil (`contribuyente`).
- **PF / PM**: persona física o moral.
- **605 Sueldos y salarios**: el patrón retiene ISR cada mes. Anual obligatoria si hay otros ingresos (p. ej. RESICO),
  dos o más patrones o se superan los límites vigentes.
- **626 RESICO PF**: ISR sobre ingresos **cobrados**, sin deducciones, con tasa según el ingreso del mes. Tiene tope
  anual; si lo rebasa, sale del régimen. Si una PM le paga, esta retiene ISR. Incompatible con ser socio de PM y con
  algunos regímenes; sueldos sí es compatible.
- **612 Actividad empresarial/profesional**: pago provisional **acumulado** con la tarifa del art. 96 y deducciones. DIOT.
- **625 Plataformas tecnológicas**: la plataforma retiene; puede ser pago definitivo si se opta por él.
- **606 Arrendamiento**: deducción ciega o gastos reales. Casa habitación exenta de IVA.

## ISR
- Base de flujo: lo **efectivamente cobrado** en el mes. PUE: fecha de la factura; PPD: la del complemento de pago.
- ISR a pagar = ISR causado − retenciones acreditables.
- Anual: se acumulan los regímenes que lo exigen, se aplican deducciones personales (tope en `vigentes`) y se restan
  pagos provisionales y retenciones de nómina.

## IVA (mensual, definitivo)
- IVA a cargo = trasladado **cobrado** − acreditable **pagado** (gastos estrictamente indispensables con CFDI) − retenido.
- Tasas: general, frontera con estímulo, 0% y exento (valores en `vigentes`). La exportación de servicios a un
  residente en el extranjero puede ir a 0% si cumple el art. 29 de la LIVA.
- **Saldo a favor**: se controla en `AAAA/saldos.json` por **periodo de origen**. Se acredita contra IVA a cargo de
  meses siguientes, empezando por el más antiguo, o se pide devolución. Antes de usar uno, confirma con acuses
  anteriores (`leer_acuses`) que exista y no se haya aplicado.

## Creadores de contenido y plataformas
- Pagos por vistas (p. ej. TikTok Creator Rewards) suelen llegar por **SPEI desde un procesador mexicano** (Ebanx),
  sin CFDI ni retenciones. Los pagadores conocidos y las decisiones del usuario están en `clientes.json` (privado).
- Sin CFDI emitido, el ingreso se captura como **"¿Tienes ingresos adicionales? Sí"** (el formulario no lo precarga).
- Flujo de efectivo: el ingreso cuenta en el mes de la **fecha de abono** del CEP.
- IVA: si el depósito se trata como **IVA incluido**, `desglosar_iva` da la base (actividades gravadas 16%) y el IVA;
  el ISR RESICO va sobre la base. La tasa 0% por exportación es dudosa si el pago llega de una entidad mexicana y el
  contenido se consume en México: revisarlo con un contador si los montos crecen.
- Pagador PM mexicana → factura con su RFC y las retenciones que correspondan. Extranjero sin RFC → RFC genérico
  extranjero, sin retención; revisa la tasa 0%.

## Obligaciones y calendario
- Mensual: **día 17** del mes siguiente (si es inhábil, el siguiente hábil) más los días hábiles extra según el sexto
  dígito numérico del RFC. `vencimiento` lo estima; **manda la fecha que muestra el formulario oficial**.
- Anual PF: abril, con las constancias de sueldos.
- Otras: buzón tributario, opinión de cumplimiento, vigencia de la e.firma (renovar antes de que venza).

## Pago tardío (`calcular_recargos`)
- **Actualización**: contribución × (INPC del mes anterior al pago / INPC del mes anterior al vencimiento); mínimo 1.
- **Recargos**: contribución actualizada × tasa mensual (LIF del año) × meses o fracción.
- Si no se paga antes de la vigencia, la línea de captura vence y hay que generar otra (complementaria).

## Coherencia CFDI 4.0
- Nombre, RFC, CP del domicilio fiscal y régimen del receptor deben coincidir **exacto** con su constancia.
- UsoCFDI compatible con el régimen del receptor; régimen del emisor compatible con la actividad.
- **PUE** = pagado en el mes, con forma de pago real. **PPD** = forma 99 y luego complemento de pago (REP).
- ObjetoImp coherente; la suma de traslados y retenciones por concepto cuadra con los totales; Moneda y TipoCambio.
- Cancelación con motivo (01 con UUID que sustituye, 02, 03 o 04); algunas requieren aceptación del receptor.
