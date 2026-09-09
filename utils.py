import platform, subprocess, sys, time, msvcrt, select
from decoracion import BOLD, RESET, AMARILLO, CYAN, ROJO, VERDE, SUBIR, BORRAR, BANDERAS 

try:
    import msvcrt
except ImportError:
    import select
    
ES_WINDOWS      = platform.system() == "Windows"
COMANDO_LIMPIAR = ["cls"] if ES_WINDOWS else ["clear"]


CABECERA        = (
    "================================================================================================\n"
    f"                                🛒 {BOLD}FRUTERÍA - PUNTO DE VENTA{RESET}                     \n"
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

def limpiar_buffer():
    try:
        while msvcrt.kbhit():
            msvcrt.getch()
    except Exception:
        while select.select([sys.stdin], [], [], 0)[0]:
            sys.stdin.read(1)

def limpiar_pantalla():
    subprocess.run(COMANDO_LIMPIAR, shell=ES_WINDOWS)
    print(CABECERA)



def mostrar_mensaje(texto, tipo="error", segundos=3, lineas_a_borrar=3):
    icono = BANDERAS.get(tipo, BANDERAS["warning"])
    print(f"\n{icono}  {texto}")
    time.sleep(segundos)
    limpiar_buffer()
    secuencia_borrado = f"{SUBIR}{BORRAR}" * lineas_a_borrar
    print(secuencia_borrado, end="", flush=True)

def pedir_confirmacion(mensaje, tipo="pregunta"):
    icono = BANDERAS.get(tipo, BANDERAS["pregunta"])
    respuesta = input(f"\n{icono}  {mensaje} (s/n): ").strip().lower()
    return respuesta in ["s", "si"]

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
