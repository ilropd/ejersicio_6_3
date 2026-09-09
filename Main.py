from decoracion import BOLD, RESET, AMARILLO, ROJO, VERDE, SUBIR, BORRAR
import sys
from datetime import datetime
import fruteria as core
from utils import limpiar_pantalla, mostrar_mensaje


def ejecutar_tpv():
    try:
        while True: 
            cesta = {}

            while True:
                limpiar_pantalla()
                core.mostrar_cesta(cesta)

                fruta = input("¿Qué fruta quieres?: ").strip()

                accion = core.procesar_comando_global(fruta, cesta)
                if accion in ("CANCELAR", "CONTINUAR"):
                    continue
                elif accion == "TICKET":
                    break

                coincidencias = core.buscar_fruta(fruta)
                
                if len(coincidencias) == 1:
                    clave = coincidencias[0]
                    datos_fruta = core.FRUTAS[clave]
                    icono, nombre_bonito, precio = datos_fruta["icono"], datos_fruta["nombre"], datos_fruta["precio"]
                    print(f"{SUBIR}{BORRAR}¿Qué fruta quieres?: {nombre_bonito} {icono}")
                elif len(coincidencias) > 1:
                    nombres_sug = [core.FRUTAS[k]["nombre"] for k in coincidencias]
                    mostrar_mensaje(f"Especifica más... Coincidencias: {nombres_sug}", "warning")
                    continue
                else:
                    mostrar_mensaje(f"La fruta '{fruta}' no existe en el catálogo", "error")
                    continue

                existente = cesta.get(clave)
                kg_acumulados = existente["kg"] if existente else 0.0
                
                kg = core.solicitar_kilos(kg_acumulados, nombre_bonito)
                core.actualizar_cesta(cesta, clave, nombre_bonito, icono, precio, kg)

            id_ticket = datetime.now().strftime("%Y%m%d_%H%M%S")
            total_a_pagar = sum(item["total"] for item in cesta.values())

            core.mostrar_ticket(cesta, id_ticket)
            metodo_pago, entrega, cambio = core.procesar_pago(total_a_pagar)
            
            print("⏳ Generando ticket en PDF...")
            core.crear_pdf(cesta, id_ticket, entrega, cambio, metodo_pago)
            print(f"{VERDE}📄 Ticket 'ticket_{id_ticket}.pdf' guardado correctamente{RESET}")

            prompt = f"\n{AMARILLO}{BOLD}[/]{RESET} Nuevo pedido  |  {ROJO}{BOLD}[Ctrl + C]{RESET} Salir > "
            if input(prompt) != "/": 
                continue

    except KeyboardInterrupt:
        pass

    print("\n\n¡Hasta pronto! 👋\n")
    sys.exit(0)

if __name__ == "__main__":
    ejecutar_tpv()