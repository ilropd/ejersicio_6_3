import platform

# ==========================================
# 1. CONFIGURACIÓN Y CONSTANTES DEL SISTEMA
# ==========================================

ES_WINDOWS = platform.system() == "Windows"
COMANDO_LIMPIAR = ["cls"] if ES_WINDOWS else ["clear"]

BOLD = "\033[1m"
ROJO = "\033[31;1m"
VERDE = "\033[32m"
NARANJA = "\033[38;5;208m"
AMARILLO = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"

SUBIR = "\033[1A"
BORRAR = "\033[2K"

TIPO_IVA = 0.04

BANDERAS = {
    "error": "❌",
    "warning": "⚠️",
    "info": "ℹ️",
    "exito": "✅",
    "pregunta": "❓",
}

CABECERA = (
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

if __name__ == "__main__":
    raise RuntimeError(
        "Este archivo no está diseñado para ejecutarse directamente. "
        "Ejecuta el programa principal."
    )