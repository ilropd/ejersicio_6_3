from func_compra import *
from func_pago import *


# ==========================================
# 3. BUCLE PRINCIPAL DE LA APLICACIÓN
# ==========================================

# ┌──────────────────────────────────────────────────────────┐
# │ FUNCIÓN:     ejecutar_tpv()                              │
# │ DESCRIPCIÓN: Bucle control del ciclo de vida del TPV     │
# └──────────────────────────────────────────────────────────┘
def ejecutar_tpv():
    try:
        while True:
            cesta = {}

            while True:
                limpiar_pantalla()
                mostrar_cesta(cesta)

                fruta = input("¿Qué fruta quieres?: ").strip()

                # 1. Comprobación de comandos especiales (/ o %)
                accion = procesar_comando_global(fruta, cesta)
                if accion in ("CANCELAR", "CONTINUAR"):
                    continue
                elif accion == "TICKET":
                    break

                # 2. Búsqueda y selección de fruta
                coincidencias = buscar_fruta(fruta)

                if len(coincidencias) == 1:
                    clave = coincidencias[0]
                    icono, nombre_bonito, precio = FRUTAS[clave]
                    print(f"{SUBIR}{BORRAR}¿Qué fruta quieres?: {nombre_bonito} {icono}")
                elif len(coincidencias) > 1:
                    nombres_sug = [FRUTAS[k][1] for k in coincidencias]
                    mostrar_mensaje(f"Especifica más... Coincidencias: {nombres_sug}", "warning")
                    continue
                else:
                    mostrar_mensaje(f"La fruta '{fruta}' no existe en el catálogo", "error")
                    continue

                # 3. Solicitar Kilos y actualizar cesta
                existente = cesta.get(clave)
                kg_acumulados = existente["kg"] if existente else 0.0

                kg = solicitar_kilos(kg_acumulados, nombre_bonito)
                actualizar_cesta(cesta, clave, nombre_bonito, icono, precio, kg)

            # 4. Cobro y generación de PDF
            id_ticket = datetime.now().strftime("%Y%m%d_%H%M%S")
            total_a_pagar = sum(item["total"] for item in cesta.values())

            mostrar_ticket(cesta, id_ticket)
            metodo_pago, entrega, cambio = procesar_pago(total_a_pagar)
            crear_pdf(cesta, id_ticket, entrega, cambio, metodo_pago)

            prompt = f"\n{AMARILLO}{BOLD}[/]{RESET} Nuevo pedido  |  {ROJO}{BOLD}[Ctrl + C]{RESET} Salir > "
            if input(prompt) != "/":
                continue

    except KeyboardInterrupt:
        pass

    print("\n\n¡Hasta pronto! 👋\n")
    sys.exit(0)


if __name__ == "__main__":
    ejecutar_tpv()
