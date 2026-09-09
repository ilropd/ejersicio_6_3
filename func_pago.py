from datetime import datetime

from reportlab.pdfgen import canvas

from func_aux import *


# ------------------------------------------
# 2.3 FLUJO DE CIERRE, PAGO Y FACTURACIÓN
# ------------------------------------------

# ┌──────────────────────────────────────────────────────────┐
# │ FUNCIÓN:     mostrar_ticket()                            │
# │ DESCRIPCIÓN: Imprime la vista previa del desglose final  │
# │ ENTRADA:     cesta (dict), id_ticket (str)               │
# └──────────────────────────────────────────────────────────┘
def mostrar_ticket(cesta, id_ticket):
    if not cesta:
        return

    limpiar_pantalla()
    W_TEXTO, W_LINEA = 51, 53
    total = sum(item["total"] for item in cesta.values())
    base = total / (1 + TIPO_IVA)
    iva = total - base

    print("=" * W_LINEA)
    print(f" {BOLD}{'TICKET DE COMPRA':^{W_LINEA}}{RESET}")
    print(" " + "=" * W_LINEA)
    print(f"  {f'Nº Ticket: {id_ticket}':>{W_TEXTO}}")
    print(" " + "-" * W_LINEA)
    print(f"  {'PRODUCTO':<16} | {'PESO':>8} | {'PVP/Kg':>9} | {'TOTAL':>9}")
    print(" " + "-" * W_LINEA)

    for item in cesta.values():
        peso = f"{item['kg']:.2f} Kg".replace(".", ",")
        print(
            f"  {item['nombre']:<16} | {peso:>8} | {formato_precio(item['pvp']):>9} | {formato_precio(item['total']):>9}")

    print(" " + "-" * W_LINEA)
    print(f"  {f'Base Imponible: {formato_precio(base)}':>{W_TEXTO}}")
    print(f"  {f'IVA ({TIPO_IVA * 100:g}%): {formato_precio(iva)}':>{W_TEXTO}}")
    print(" " + "=" * W_LINEA)
    print(f"  {f'TOTAL A PAGAR: {formato_precio(total)}':>{W_TEXTO}}")
    print(" " + "=" * W_LINEA + "\n")


# ┌──────────────────────────────────────────────────────────────────────────┐
# │ FUNCIÓN:     procesar_pago()                                             │
# │ DESCRIPCIÓN: Gestiona el cobro en efectivo o tarjeta                     │
# │ ENTRADA:     total_a_pagar (float)                                       │
# │ SALIDA:      tuple (metodo_pago, entrega, cambio) -> (str, float, float) │
# └──────────────────────────────────────────────────────────────────────────┘
def procesar_pago(total_a_pagar):
    while True:
        entrega_input = input(
            f"\n{BOLD}Total: {formato_precio(total_a_pagar)}{RESET} | "
            f"{NARANJA}Entrega (€){RESET} {CYAN}[ENTER = Tarjeta]{RESET} > "
        ).strip()

        if entrega_input == "":
            print(f"{CYAN}💳 PAGO CON TARJETA ACEPTADO{RESET}\n")
            return "Tarjeta", total_a_pagar, 0.0

        try:
            entrega = float(entrega_input.replace(",", "."))
            if entrega >= total_a_pagar:
                cambio = entrega - total_a_pagar
                print(f"{NARANJA}💶 CAMBIO A DEVOLVER: {formato_precio(cambio)}{RESET}\n")
                return "Efectivo", entrega, cambio

            faltante = total_a_pagar - entrega
            mostrar_mensaje(f"Cantidad insuficiente. Faltan {formato_precio(faltante)}", "error", segundos=2,
                            lineas_a_borrar=4)

        except ValueError:
            mostrar_mensaje("Introduce un número válido o pulsa ENTER para tarjeta", "error", segundos=2,
                            lineas_a_borrar=4)


# ┌────────────────────────────────────────────────────────────────────────────────────────────────┐
# │ FUNCIÓN:     crear_pdf()                                                                       │
# │ DESCRIPCIÓN: Construye e imprime el archivo PDF                                                │
# │ ENTRADA:     cesta (dict), id_ticket (str), entrega (float), cambio (float), metodo_pago (str) │
# └────────────────────────────────────────────────────────────────────────────────────────────────┘
def crear_pdf(cesta, id_ticket, entrega, cambio, metodo_pago):
    print("⏳ Generando ticket en PDF...")
    total = sum(item["total"] for item in cesta.values())
    base = total / (1 + TIPO_IVA)
    iva = total - base
    ANCHO_L = 36

    # Fecha y hora actual
    fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")

    # 1. Cabecera fiscal e informativa del comercio
    lineas = [
        "FRUITERIA L'HORT".center(ANCHO_L),
        "CIF: B-12345678".center(ANCHO_L),
        "Carrer Major 123, Barcelona".center(ANCHO_L),
        f"Fecha: {fecha_actual}".center(ANCHO_L),
        f"Nº Ticket: {id_ticket}".center(ANCHO_L),
        "=" * ANCHO_L,
        f"{'PRODUCTO':<12} {'PESO(Kg)':>8} {'PVP':>5} {'TOTAL':>8}",
        "-" * ANCHO_L
    ]

    # 2. Detalle de productos
    for item in cesta.values():
        nombre = item['nombre'][:12]
        peso = f"{item['kg']:.2f}".replace(".", ",")
        pvp = f"{item['pvp']:.2f}".replace(".", ",")
        lineas.append(f"{nombre:<12} {peso:>8} {pvp:>5} {formato_precio(item['total']):>8}")

    # 3. Totales y forma de pago
    bloque_pago = [
        "-" * ANCHO_L,
        f"{'Base Imponible:':<27} {formato_precio(base):>8}",
        f"{f'IVA ({TIPO_IVA * 100:g}%):':<27} {formato_precio(iva):>8}",
        "=" * ANCHO_L,
        f"{'TOTAL A PAGAR:':<27} {formato_precio(total):>8}",
        "=" * ANCHO_L,
        f"{'Forma de Pago:':<27} {metodo_pago:>8}"
    ]

    if metodo_pago == "Efectivo":
        bloque_pago.extend([
            f"{'Entregado:':<27} {formato_precio(entrega):>8}",
            f"{'Cambio:':<27} {formato_precio(cambio):>8}"
        ])

    bloque_pago.extend([
        "- " * (ANCHO_L // 2),
        "",
        "¡Gracias por su compra!".center(ANCHO_L)
    ])

    lineas.extend(bloque_pago)

    # 4. Generación del lienzo
    ancho_ticket = 226
    alto_ticket = 40 + len(lineas) * 12
    c = canvas.Canvas(f"ticket_{id_ticket}.pdf", pagesize=(ancho_ticket, alto_ticket))

    text_object = c.beginText(14, alto_ticket - 20)
    text_object.setFont("Courier-Bold", 8.5)
    text_object.setLeading(12)

    for linea in lineas:
        text_object.textLine(linea)

    c.drawText(text_object)
    c.save()
    print(f"{VERDE}📄 Ticket 'ticket_{id_ticket}.pdf' guardado correctamente{RESET}")
    print(f"🖨️  Ticket enviado a la impresora...")
