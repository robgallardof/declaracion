---
name: facturacion
description: "Emite CFDI 4.0 de ingreso en el portal de Factura electrónica para clientes (p. ej. plataformas que pagan a creadores) y guarda el PDF y el XML en la carpeta del mes; también cancela con motivo. Usar cuando el usuario diga 'factura a <cliente>', 'genera la factura de <mes>' o pida cancelar una factura."
---

# Facturación (RESICO 626)

1. **Datos**: cliente (RFC, razón social exacta, CP fiscal, régimen), monto, mes y concepto. El monto sale del
   comprobante de pago o del estado de cuenta del mes (`AAAA/MM-mes/`). Si falta un dato, pregunta.
   Guarda los clientes recurrentes en `clientes.json` (privado) para no volver a pedirlos.
2. **Campos típicos**:
   - Tipo I. Régimen del emisor: el del perfil (`contribuyente`). Uso CFDI G03 (o el que pida el cliente).
     Moneda MXN (si es USD, tipo de cambio).
   - Método de pago: **PUE** si ya se cobró; **PPD** si se cobra después (luego complemento de pago).
   - Forma de pago: 03 transferencia (99 si es PPD).
   - Clave del producto/servicio según la actividad (p. ej. 80141600 publicidad / 82101600 creación de contenido);
     confírmala con el usuario la primera vez.
   - IVA trasladado a la tasa general. Si el cliente es PM: retenciones de ISR e IVA según `datos/vigentes-AAAA.json`,
     **salvo** que el cliente indique otra cosa. Sus instrucciones de facturación mandan (si contradicen la ley, avisa).
3. **Portal**: skill `portal-fiscal` → login con e.firma (lo hace el usuario) → Factura electrónica → "Generación de CFDI"
   → formulario → Vista previa.
4. Pasa el borrador al agente `validador-cfdi`. Corrige los ❌ antes de seguir.
5. **Pausa**: resumen (cliente, concepto, subtotal, IVA, retenciones, total, PUE/PPD) y espera un OK → Sellar.
6. **Guardar** PDF y XML en `AAAA/MM-mes/facturas/` como `AAAA-MM-DD_<cliente>_<total>.pdf|xml`. Confirma el UUID.
7. **Cancelar** solo si el usuario lo pide, con el motivo (01–04) y el UUID de sustitución si aplica.
