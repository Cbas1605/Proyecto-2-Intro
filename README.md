# Proyecto 2 - Defensor vs Atacante

Juego de estrategia por turnos para 2 jugadores, hecho en Python con Tkinter.
Un jugador defiende una base central construyendo torres y muros; el otro
ataca esa base comprando unidades.

## Como ejecutarlo

1. Asegurate de tener Python 3 instalado.
2. Si usas Linux y Tkinter no viene incluido, instalalo con:
   `sudo apt-get install python3-tk`
3. Ejecuta el archivo principal:
   `python3 Proyecto2_JuegoDefensa.py`

No se necesita instalar ninguna libreria adicional (no usa pygame ni Pillow,
solo Tkinter, que viene con Python).

## Estructura del proyecto

```
proyecto/
├── Proyecto2_JuegoDefensa.py   <- archivo principal, aqui se ejecuta el juego
├── imagenes/                   <- iconos de las piezas (torres, muros, unidades, base)
└── jugadores.json              <- se crea solo al jugar, guarda usuarios y victorias
```

## Clases principales

- **Juego**: controla todas las pantallas, las reglas y el flujo de la partida.
- **Torre**: representa una torre o un muro colocado por el defensor.
- **Unidad**: representa una unidad comprada por el atacante.

## Facciones

Cada faccion cambia el color y le da una pequena ventaja balanceada:

| Faccion     | Ventaja                                  |
|-------------|-------------------------------------------|
| Medieval    | +15% de vida en torres y unidades         |
| Futurista   | +1 de alcance (torres) o velocidad (unidades) |
| Naturaleza  | +20% de dinero al usar "Quitar" en una pieza |
| Oscura      | +15% de dano en torres y unidades         |

Cada tipo de pieza (Muro, Torre Basica/Pesada/Magica, Soldado/Tanque/Rapida,
Base) tiene su propio icono, y cada faccion tiene su propio color, para que
sea facil reconocer de quien es cada pieza con solo verla en el tablero.
