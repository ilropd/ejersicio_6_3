import json
import os
from datetime import datetime
from reportlab.pdfgen import canvas
from utils import limpiar_pantalla, mostrar_mensaje, pedir_confirmacion
from decoracion import BOLD, RESET, CYAN, NARANJA

TIPO_IVA = 0.04
ARCHIVO_DATOS = "datos.json"

# Catálogo fallback por si no existe el archivo JSON
CATALOGO_BASE = {
    "cereza": {"icono": "🍒", "nombre": "Cereza", "precio": 4.50},
    "datil": {"icono": "🌴", "nombre": "Dátil", "precio": 6.20},
    "fresa": {"icono": "🍓", "nombre": "Fresa", "precio": 3.80},
    "kiwi": {"icono": "🥝", "nombre": "Kiwi", "precio": 3.20},
    "limon": {"icono": "🍋", "nombre": "Limón", "precio": 1.60},
    "mango": {"icono": "🥭", "nombre": "Mango", "precio": 3.50},
    "manzana": {"icono": "🍎", "nombre": "Manzana", "precio": 1.95},
    "melocoton": {"icono": "🍑", "nombre": "Melocotón", "precio": 2.40},
    "melon": {"icono": "🍈", "nombre": "Melón", "precio": 1.20},
    "naranja": {"icono": "🍊", "nombre": "Naranja", "precio": 1.50},
    "pera": {"icono": "🍐", "nombre": "Pera", "precio": 2.15},
    "pina": {"icono": "🍍", "nombre": "Piña", "precio": 1.80},
    "platano": {"icono": "🍌", "nombre": "Plátano", "precio": 2.10},
    "sandia": {"icono": "🍉", "nombre": "Sandía", "precio": 0.95},
    "uva": {"icono": "🍇", "nombre": "Uva", "precio": 2.90}
}
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

            if es_fijado:
                if num_kilos == 0:
                    return -kg_acumulados
                if 0.001 <= num_kilos <= 10.0:
                    return num_kilos - kg_acumulados
                mostrar_mensaje("El peso fijado debe estar entre 0,001 y 10 Kg", "error")
                continue

            if num_kilos < 0:
                nuevo_total = round(kg_acumulados + num_kilos, 3)
                if nuevo_total == 0:
                    return num_kilos
                elif nuevo_total > 0:
                    return num_kilos
                else:
                    mostrar_mensaje(f"No puedes restar {abs(num_kilos):.2f} Kg. Solo hay {kg_acumulados:.2f} Kg en la cesta", "error")
                    continue

            if 0.001 <= num_kilos <= kg_maximos_permitidos:
                return num_kilos

            if kg_maximos_permitidos < 0.001:
                mostrar_mensaje("Límite de 10 Kg alcanzado. Solo puedes restar (ej: -2) o fijar (ej: *5)", "error")
            else:
                mostrar_mensaje(f"Introduce una cantidad válida (máx. {kg_maximos_permitidos:.2f} Kg)", "error")
            continue

        except ValueError:
            mostrar_mensaje("Entrada no válida. Escribe un número (ej: ,05), resta (ej: -,5) o fija (ej: *,5)", "error")

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
# ==========================================
# MANTENIMIENTO DE DATOS (PERSISTENCIA JSON)
# ==========================================

def cargar_catalogo():
    """Carga los datos desde JSON o crea el archivo base si no existe."""
    if not os.path.exists(ARCHIVO_DATOS):
        guardar_catalogo(CATALOGO_BASE)
        return CATALOGO_BASE
    
    try:
        with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return CATALOGO_BASE

def guardar_catalogo(catalogo):
    """Guarda las actualizaciones del catálogo en el archivo de mantenimiento."""
    with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
        json.dump(catalogo, f, ensure_ascii=False, indent=4)

# Cargar datos al importar el módulo
FRUTAS = cargar_catalogo()

# ==========================================
# LÓGICA DE NEGOCIO Y OPERACIONES
# ==========================================

def formato_precio(numero):
    return f"{numero:.2f} €".replace(".", ",")

def buscar_fruta(fruta):
    clave_entrada = fruta.lower().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
    coincidencias = []
    if clave_entrada != "":
        for k in FRUTAS:
            if k.startswith(clave_entrada):
                coincidencias.append(k)
    return coincidencias

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

# ==========================================
# GENERACIÓN DE PDF
# ==========================================

def crear_pdf(cesta, id_ticket, entrega, cambio, metodo_pago):
    total = sum(item["total"] for item in cesta.values())
    base = total / (1 + TIPO_IVA)
    iva = total - base
    ANCHO_L = 36

    fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")

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

    for item in cesta.values():
        nombre = item['nombre'][:12]
        peso = f"{item['kg']:.2f}".replace(".", ",")
        pvp = f"{item['pvp']:.2f}".replace(".", ",")
        lineas.append(f"{nombre:<12} {peso:>8} {pvp:>5} {formato_precio(item['total']):>8}")

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