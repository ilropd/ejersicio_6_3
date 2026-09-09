from datetime import datetime
from reportlab.pdfgen import canvas
from colores import BOLD, ROJO, VERDE, NARANJA, AMARILLO, CYAN, RESET
from utils import formato_precio, pedir_confirmacion, mostrar_mensaje, limpiar_pantalla, TIPO_IVA



CABECERA        = (
    "================================================================================================\n"
    f"                                 🛒 {BOLD}FRUTERÍA - PUNTO DE VENTA{RESET}                     \n"
    f"  Selecciona fruta, ajusta peso (+/-/*), cobra en efectivo o tarjeta y genera e imprime ticket      \n"
    "================================================================================================\n"
    " ┌─────────────────┬──────────┬──┬─────────────────┬──────────┬──┬─────────────────┬──────────┐ \n"
    " │ FRUTA           │ PVP / Kg │  │ FRUTA           │ PVP / Kg │  │ FRUTA           │ PVP / Kg │ \n"
    " ├─────────────────┼──────────┼──┼─────────────────┼──────────┼──┼─────────────────┼──────────┤ \n"
    " │ 🍒 Cereza       │  4,50 €  │  │ 🥭 Mango        │  3,50 €  │  │ 🍐 Pera         │  2,15 €  │ \n"
    " │ 🌴 Dátil        │  6,20 €  │  │ 🍎 Manzana      │  1,95 €  │  │ 🍍 Piña         │  1,80 €  │ \n"
    " │ 🍓 Fresa        │  3,80 €  │  │ 🍑 Melocotón    │  2,40 €  │  │ 🍌 Plátano      │  2,10 €  │ \n"
    " │ 🥝 Kiwi         │  3,20 €  │  │ 🍈 Melón        │  1,20 €  │  │ 🍉 Sandía       │  0,95 €  │ \n"
    " │ 🍋 Limón        │  1,60 €  │  │ 🍊 Naranja      │  1,50 €  │  │ 🍇 Uva          │  2,90 €  │ \n"
    " └─────────────────┴──────────┴──┴─────────────────┴──────────┴──┴─────────────────┴──────────┘ \n"
    f" 🎮 COMANDOS: {AMARILLO}[/]{RESET} Nuevo pedido     {CYAN}[%]{RESET} Generar Ticket   {ROJO}[Ctrl+C]{RESET} Salir\n"
    f" ⚖️  Kg (EJ.): {VERDE}[+3,5]{RESET} Sumar         {VERDE}[-2,7]{RESET} Restar        {VERDE}[*1,9]{RESET} Fijar      (Límite: {BOLD}hasta 10 Kg{RESET})\n"
    "================================================================================================\n"
)

FRUTAS          = {
    "cereza":    ("🍒", "Cereza",    4.50),
    "datil":     ("🌴", "Dátil",     6.20),
    "fresa":     ("🍓", "Fresa",     3.80),
    "kiwi":      ("🥝", "Kiwi",      3.20),
    "limon":     ("🍋", "Limón",     1.60),
    "mango":     ("🥭", "Mango",     3.50),
    "manzana":   ("🍎", "Manzana",   1.95),
    "melocoton": ("🍑", "Melocotón", 2.40),
    "melon":     ("🍈", "Melón",     1.20),
    "naranja":   ("🍊", "Naranja",   1.50),
    "pera":      ("🍐", "Pera",      2.15),
    "pina":      ("🍍", "Piña",      1.80),
    "platano":   ("🍌", "Plátano",   2.10),
    "sandia":    ("🍉", "Sandía",    0.95),
    "uva":       ("🍇", "Uva",       2.90)
}

# ------------------------------------------
# 2.2 FLUJO DE COMPRA Y CESTA
# ------------------------------------------

# ┌──────────────────────────────────────────────────────────┐
# │ FUNCIÓN:     mostrar_cesta()                             │
# │ DESCRIPCIÓN: Renderiza los productos en la cesta actual  │
# │ ENTRADA:     cesta (dict)                                │
# └──────────────────────────────────────────────────────────┘
def mostrar_cesta(cesta):
    if cesta:
        print("🛒 CESTA ACTUAL:")
        total_provisional = sum(item["total"] for item in cesta.values())
        for item in cesta.values():
            kg_txt  = f"{item['kg']:.2f}".replace(".00", "").replace(".", ",")
            tot_txt = formato_precio(item['total'])
            print(f"   • {item['icono']} {item['nombre']:<10}: {kg_txt:>5} Kg  ->  {tot_txt:>9}")
        
        tot_prov_txt = formato_precio(total_provisional)
        print("-" * 46)
        print(f"   {'TOTAL PROVISIONAL':<26} ->  {tot_prov_txt:>9}")
        print("-" * 46 + "\n")


# ┌─────────────────────────────────────────────────────────────────┐
# │ FUNCIÓN:     procesar_comando_global()                          │
# │ DESCRIPCIÓN: Evalúa órdenes especiales ('/', '%', '')           │
# │ ENTRADA:     fruta (str), cesta (dict)                          │
# │ SALIDA:      str ('CANCELAR', 'TICKET', 'CONTINUAR', 'NINGUNA') │
# └─────────────────────────────────────────────────────────────────┘
def procesar_comando_global(fruta, cesta):
    if fruta == "/":
        if cesta:
            if pedir_confirmacion("¿Seguro que quieres CANCELAR este pedido y empezar uno nuevo?"):
                cesta.clear()
                mostrar_mensaje("Pedido cancelado. Iniciando nueva cesta...", "info", segundos=2)
                return "CANCELAR"
            return "CONTINUAR"
        mostrar_mensaje("La cesta ya está vacía", "warning")
        return "CONTINUAR"

    elif fruta == "%":
        if cesta:
            if pedir_confirmacion("¿Generar el ticket final y cobrar?"):
                return "TICKET"
            return "CONTINUAR"
        mostrar_mensaje("La cesta está vacía. Añade al menos una fruta", "warning")
        return "CONTINUAR"

    elif fruta == "":
        mostrar_mensaje("Usa '%' para generar el ticket o '/' para cancelar el pedido", "info")
        return "CONTINUAR"

    return "NINGUNA"


# ┌──────────────────────────────────────────────────────────┐
# │ FUNCIÓN:     buscar_fruta()                              │
# │ DESCRIPCIÓN: Filtra coincidencias en el diccionario      │
# │ ENTRADA:     fruta (str)                                 │
# │ SALIDA:      list[str] (claves de frutas coincidentes)   │
# └──────────────────────────────────────────────────────────┘
def buscar_fruta(fruta):
    clave_entrada = fruta.lower().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
    coincidencias = []
    if clave_entrada != "":
        for k in FRUTAS:
            if k.startswith(clave_entrada):
                coincidencias.append(k)
    return coincidencias


# ┌──────────────────────────────────────────────────────────┐
# │ FUNCIÓN:     solicitar_kilos()                           │
# │ DESCRIPCIÓN: Captura, valida y calcula variación de peso │
# │ ENTRADA:     kg_acumulados (float), nombre_bonito (str)  │
# │ SALIDA:      float (diferencia de kilos a sumar/restar)  │
# └──────────────────────────────────────────────────────────┘
def solicitar_kilos(kg_acumulados, nombre_bonito):
    kg_maximos_permitidos = round(10.0 - kg_acumulados, 2)

    if kg_maximos_permitidos < 0.001:
        mensaje_aviso = (
            f"\nTienes {kg_acumulados:.2f} Kg de {nombre_bonito}. "
            f"Límite máximo (10,00 Kg) alcanzado. Usa '*' o '-' para reducir."
        ).replace(".", ",")
        mostrar_mensaje(mensaje_aviso, "warning", segundos=3)

    while True:
        kg_input = input(f"¿Cuántos kilos? (máx. {kg_maximos_permitidos:.2f} kg): ".replace(".", ",")).strip().replace(",", ".")

        # Soporte para omisión de cero inicial (.25, -.25, *.25)
        if kg_input.startswith("."):
            kg_input = "0" + kg_input
        elif kg_input.startswith("-."):
            kg_input = kg_input.replace("-.", "-0.")
        elif kg_input.startswith("*."):
            kg_input = kg_input.replace("*.", "*0.")

        es_fijado = False
        if kg_input.startswith("*"):
            es_fijado = True
            kg_input = kg_input.replace("*", "")

        try:
            num_kilos = float(kg_input)

            # 1. Modificador '*' (Fijar peso absoluto)
            if es_fijado:
                if num_kilos == 0:
                    return -kg_acumulados  # Elimina el producto de la cesta
                if 0.001 <= num_kilos <= 10.0:
                    return num_kilos - kg_acumulados
                mostrar_mensaje("El peso fijado debe estar entre 0,001 y 10 Kg", "error")
                continue

            # 2. Modificador '-' (Restar peso)
            if num_kilos < 0:
                nuevo_total = round(kg_acumulados + num_kilos, 3)
                if nuevo_total == 0:
                    return num_kilos  # Si queda exactamente 0, la función actualizar_cesta lo borra
                elif nuevo_total > 0:
                    return num_kilos
                else:
                    mostrar_mensaje(f"No puedes restar {abs(num_kilos):.2f} Kg. Solo hay {kg_acumulados:.2f} Kg en la cesta", "error")
                    continue

            # 3. Sumar peso (sin mínimo arbitrario de 0.10)
            if 0.001 <= num_kilos <= kg_maximos_permitidos:
                return num_kilos

            if kg_maximos_permitidos < 0.001:
                mostrar_mensaje("Límite de 10 Kg alcanzado. Solo puedes restar (ej: -2) o fijar (ej: *5)", "error")
            else:
                mostrar_mensaje(f"Introduce una cantidad válida (máx. {kg_maximos_permitidos:.2f} Kg)", "error")
            continue

        except ValueError:
            mostrar_mensaje("Entrada no válida. Escribe un número (ej: ,05), resta (ej: -,5) o fija (ej: *,5)", "error")


# ┌──────────────────────────────────────────────────────────────────────────────────────────────────────┐
# │ FUNCIÓN:     actualizar_cesta()                                                                      │
# │ DESCRIPCIÓN: Modifica subtotales y estructura en cesta                                               │
# │ ENTRADA:     cesta (dict), clave (str), nombre_bonito (str), icono (str), precio (float), kg (float) │
# │ SALIDA:      None (modifica diccionario in-place)                                                    │
# └──────────────────────────────────────────────────────────────────────────────────────────────────────┘
def actualizar_cesta(cesta, clave, nombre_bonito, icono, precio, kg):
    total_producto = precio * kg
    
    if clave in cesta:
        cesta[clave]["kg"] += kg
        cesta[clave]["total"] += total_producto
        if cesta[clave]["kg"] <= 0:
            del cesta[clave]
    elif kg > 0:
        cesta[clave] = {
            "icono": icono,
            "nombre": nombre_bonito,
            "pvp": precio,
            "kg": kg,
            "total": total_producto
        }


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
        print(f"  {item['nombre']:<16} | {peso:>8} | {formato_precio(item['pvp']):>9} | {formato_precio(item['total']):>9}")

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
            mostrar_mensaje(f"Cantidad insuficiente. Faltan {formato_precio(faltante)}", "error", segundos=2, lineas_a_borrar=4)

        except ValueError:
            mostrar_mensaje("Introduce un número válido o pulsa ENTER para tarjeta", "error", segundos=2, lineas_a_borrar=4)


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