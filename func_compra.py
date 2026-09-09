import json

from func_aux import *

# ------------------------------------------
# 2.2 FLUJO DE COMPRA Y CESTA
# ------------------------------------------

# ┌──────────────────────────────────────────────────────────┐
# │ FUNCIÓN:     load json data                              │
# │ DESCRIPCIÓN:                                             │
# │ ENTRADA:                                                 │
# └──────────────────────────────────────────────────────────┘

with open("data.json", "r", encoding="utf-8") as f:
    FRUTAS = json.load(f)

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
            kg_txt = f"{item['kg']:.2f}".replace(".00", "").replace(".", ",")
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
    clave_entrada = fruta.lower().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú",
                                                                                                                  "u")
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
        kg_input = input(f"¿Cuántos kilos? (máx. {kg_maximos_permitidos:.2f} kg): ".replace(".", ",")).strip().replace(
            ",", ".")

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
                    mostrar_mensaje(
                        f"No puedes restar {abs(num_kilos):.2f} Kg. Solo hay {kg_acumulados:.2f} Kg en la cesta",
                        "error")
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


if __name__ == "__main__":
    raise RuntimeError(
        "Este archivo no está diseñado para ejecutarse directamente. "
        "Ejecuta el programa principal."
    )