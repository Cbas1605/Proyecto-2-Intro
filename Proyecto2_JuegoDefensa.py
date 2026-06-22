
import tkinter as tk
from tkinter import messagebox
import json
import os
import time



ARCHIVO = "jugadores.json"   #se guardan los jugadores

FILAS = 10
COLUMNAS = 10
BASE_FILA = 4      
BASE_COL = 8
BASE_VIDA = 200

DINERO_INICIAL = 120  



C_FONDO   = "#E8EEF1"   
C_CARD    = "#FFFFFF"   
C_BANNER  = "#1F3A5F"   
C_TEXTO   = "#2C3E50"   
C_AZUL    = "#2980B9"   
C_ROJO    = "#C0392B"   
C_NARANJA = "#E67E22"   
C_VERDE   = "#27AE60"   
C_GRIS    = "#7F8C8D"   
C_CELDA   = "#CFD8DC"   
C_ZONA    = "#F5CBA7"   

FACCIONES = {
    "Medieval": "#8B5A2B",
    "Futurista": "#2E86DE",
    "Naturaleza": "#27AE60",
    "Oscura": "#6C3483",
}

COLOR_MURO = {
    "Medieval": "#5C3A1B",
    "Futurista": "#1B4F8C",
    "Naturaleza": "#155C32",
    "Oscura": "#3F1F52",
}

FACCION_BONOS = {
    "Medieval":   {"vida": 1.15},     # +15% de vida en torres y unidades
    "Futurista":  {"extra": 1},       # +1 de alcance (torres) o velocidad (unidades)
    "Naturaleza": {"reembolso": 1.20},# +20% de dinero al quitar una pieza
    "Oscura":     {"dano": 1.15},     # +15% de dano en torres y unidades
}

FACCION_DESCRIPCION = {
    "Medieval": "+15% de vida",
    "Futurista": "+1 alcance / velocidad",
    "Naturaleza": "+20% dinero al quitar piezas",
    "Oscura": "+15% de dano",
}

TORRES = {
    "Basica": [20, 50, 10, 3, 3],
    "Pesada": [40, 120, 20, 2, 4],
    "Magica": [35, 40, 8, 4, 3],
    "Muro":   [10, 80, 0, 0, 0],
}

UNIDADES = {
    "Soldado": [15, 40, 10, 1, 3, 10],
    "Tanque":  [35, 120, 15, 1, 4, 20],
    "Rapida":  [20, 30, 8, 2, 3, 12],
}

TEXTO = {
    "Basica": "TB", "Pesada": "TP", "Magica": "TM", "Muro": "MURO",
    "Soldado": "SOL", "Tanque": "TAN", "Rapida": "RAP", "BASE": "BASE",
}



class Torre:
    def __init__(self, tipo, fila, col, faccion=None):
        datos = TORRES[tipo]
        self.tipo = tipo
        self.fila = fila
        self.col = col
        self.faccion = faccion
        self.costo = datos[0]
        self.vida = datos[1]
        self.dano = datos[2]
        self.alcance = datos[3]
        self.cooldown = datos[4]
        self.contador = 0   # cuenta los turnos para la habilidad


        if faccion in FACCION_BONOS:
            bono = FACCION_BONOS[faccion]
            if "vida" in bono:
                self.vida = int(self.vida * bono["vida"])
            if "dano" in bono:
                self.dano = int(self.dano * bono["dano"])
            if "extra" in bono and self.tipo != "Muro":
                self.alcance += bono["extra"]


class Unidad:
    def __init__(self, tipo, fila, col, faccion=None):
        datos = UNIDADES[tipo]
        self.tipo = tipo
        self.fila = fila
        self.col = col
        self.faccion = faccion
        self.costo = datos[0]
        self.vida = datos[1]
        self.dano = datos[2]
        self.velocidad = datos[3]
        self.cooldown = datos[4]
        self.recompensa = datos[5]
        self.contador = 0
        self.congelada = False
        self.escudo = False

        if faccion in FACCION_BONOS:
            bono = FACCION_BONOS[faccion]
            if "vida" in bono:
                self.vida = int(self.vida * bono["vida"])
            if "dano" in bono:
                self.dano = int(self.dano * bono["dano"])
            if "extra" in bono:
                self.velocidad += bono["extra"]



class Juego:
    def __init__(self, root):
        self.root = root
        self.root.title("Proyecto 2 - Defensor vs Atacante")
        self.root.config(bg=C_FONDO)   

        # jugadores
        self.jugadores = self.cargar_jugadores()
        self.jugador_def = None   # nombre del defensor
        self.jugador_atk = None   # nombre del atacante
        self.faccion_def = None
        self.faccion_atk = None

        self.ronda = 1
        self.ganadas_def = 0
        self.ganadas_atk = 0

        self.pantalla_login()


    def cargar_jugadores(self):
        if os.path.exists(ARCHIVO):
            f = open(ARCHIVO, "r", encoding="utf-8")
            datos = json.load(f)
            f.close()
            return datos
        return {}

    def guardar_jugadores(self):
        f = open(ARCHIVO, "w", encoding="utf-8")
        json.dump(self.jugadores, f, indent=4, ensure_ascii=False)
        f.close()

    

    def limpiar(self):
        for w in self.root.winfo_children():
            w.destroy()

    
    def banner(self, texto):
        tk.Label(self.root, text=texto, font=("Arial", 20, "bold"),
                 bg=C_BANNER, fg="white", pady=12).pack(fill="x")

    def boton(self, parent, texto, comando, color=C_AZUL):
        # crea un boton con estilo y lo devuelve (el que lo llama lo coloca)
        return tk.Button(parent, text=texto, command=comando,
                         bg=color, fg="white", font=("Arial", 11, "bold"),
                         relief="raised", bd=2, padx=8, pady=4,
                         activebackground=color, activeforeground="white")


    def pantalla_login(self):
        self.limpiar()

        self.banner("DEFENSOR  vs  ATACANTE")

        marco = tk.Frame(self.root, bg=C_FONDO)
        marco.pack(pady=15)

        f_def = tk.Frame(marco, bg=C_CARD, bd=2, relief="ridge", padx=18, pady=18)
        f_def.grid(row=0, column=0, padx=15)
        tk.Label(f_def, text="Jugador 1 (DEFENSOR)", bg=C_CARD, fg=C_AZUL,
                 font=("Arial", 13, "bold")).pack(pady=(0, 8))
        tk.Label(f_def, text="Usuario:", bg=C_CARD, fg=C_TEXTO).pack()
        self.e_def_user = tk.Entry(f_def)
        self.e_def_user.pack()
        tk.Label(f_def, text="Contrasena:", bg=C_CARD, fg=C_TEXTO).pack()
        self.e_def_pass = tk.Entry(f_def, show="*")
        self.e_def_pass.pack()
        self.boton(f_def, "Iniciar sesion",
                   lambda: self.iniciar_sesion("def"), C_AZUL).pack(pady=4)
        self.boton(f_def, "Registrarse",
                   lambda: self.registrar("def"), C_GRIS).pack()
        self.l_def = tk.Label(f_def, text="No ha iniciado sesion",
                              bg=C_CARD, fg="red")
        self.l_def.pack(pady=5)

        f_atk = tk.Frame(marco, bg=C_CARD, bd=2, relief="ridge", padx=18, pady=18)
        f_atk.grid(row=0, column=1, padx=15)
        tk.Label(f_atk, text="Jugador 2 (ATACANTE)", bg=C_CARD, fg=C_ROJO,
                 font=("Arial", 13, "bold")).pack(pady=(0, 8))
        tk.Label(f_atk, text="Usuario:", bg=C_CARD, fg=C_TEXTO).pack()
        self.e_atk_user = tk.Entry(f_atk)
        self.e_atk_user.pack()
        tk.Label(f_atk, text="Contrasena:", bg=C_CARD, fg=C_TEXTO).pack()
        self.e_atk_pass = tk.Entry(f_atk, show="*")
        self.e_atk_pass.pack()
        self.boton(f_atk, "Iniciar sesion",
                   lambda: self.iniciar_sesion("atk"), C_ROJO).pack(pady=4)
        self.boton(f_atk, "Registrarse",
                   lambda: self.registrar("atk"), C_GRIS).pack()
        self.l_atk = tk.Label(f_atk, text="No ha iniciado sesion",
                              bg=C_CARD, fg="red")
        self.l_atk.pack(pady=5)

     
        abajo = tk.Frame(self.root, bg=C_FONDO)
        abajo.pack(pady=12)
        self.boton(abajo, "Continuar a facciones",
                   self.ir_a_facciones, C_VERDE).pack(pady=4)
        self.boton(abajo, "Ver Top de jugadores",
                   self.pantalla_top, C_GRIS).pack()

    def registrar(self, rol):
        if rol == "def":
            user = self.e_def_user.get().strip()
            pwd = self.e_def_pass.get().strip()
        else:
            user = self.e_atk_user.get().strip()
            pwd = self.e_atk_pass.get().strip()

        if user == "" or pwd == "":
            messagebox.showinfo("Aviso", "Escriba usuario y contrasena")
            return
        if user in self.jugadores:
            messagebox.showinfo("Aviso", "Ese usuario ya existe")
            return

        self.jugadores[user] = {"password": pwd, "vic_def": 0, "vic_atk": 0}
        self.guardar_jugadores()
        messagebox.showinfo("Listo", "Jugador registrado")

    def iniciar_sesion(self, rol):
        if rol == "def":
            user = self.e_def_user.get().strip()
            pwd = self.e_def_pass.get().strip()
        else:
            user = self.e_atk_user.get().strip()
            pwd = self.e_atk_pass.get().strip()

        if user not in self.jugadores:
            messagebox.showinfo("Aviso", "El usuario no existe")
            return
        if self.jugadores[user]["password"] != pwd:
            messagebox.showinfo("Aviso", "Contrasena incorrecta")
            return

        if rol == "def":
            self.jugador_def = user
            self.l_def.config(text="Sesion: " + user, fg="green")
        else:
            self.jugador_atk = user
            self.l_atk.config(text="Sesion: " + user, fg="green")

    def ir_a_facciones(self):
        if self.jugador_def is None or self.jugador_atk is None:
            messagebox.showinfo("Aviso", "Ambos jugadores deben iniciar sesion")
            return
        if self.jugador_def == self.jugador_atk:
            messagebox.showinfo("Aviso", "No puede ser el mismo jugador")
            return
        self.pantalla_facciones()

  

    def pantalla_facciones(self):
        self.limpiar()
        self.faccion_def = None
        self.faccion_atk = None

        self.banner("Seleccion de facciones")

        marco = tk.Frame(self.root, bg=C_FONDO)
        marco.pack(pady=15)

        # defensor
        f1 = tk.Frame(marco, bg=C_CARD, bd=2, relief="ridge", padx=20, pady=15)
        f1.grid(row=0, column=0, padx=15)
        tk.Label(f1, text="Defensor: " + self.jugador_def, bg=C_CARD, fg=C_AZUL,
                 font=("Arial", 12, "bold")).pack(pady=(0, 6))
        self.var_def = tk.StringVar(value="")
        for nombre in FACCIONES:
            f_op = tk.Frame(f1, bg=C_CARD)
            f_op.pack(anchor="w")
            tk.Radiobutton(f_op, text=nombre, variable=self.var_def, bg=C_CARD,
                           value=nombre, fg=FACCIONES[nombre],
                           font=("Arial", 11, "bold"),
                           selectcolor=C_FONDO).pack(side="left")
            tk.Label(f_op, text="(" + FACCION_DESCRIPCION[nombre] + ")",
                     bg=C_CARD, fg=C_GRIS, font=("Arial", 9)).pack(side="left")

        # atacante
        f2 = tk.Frame(marco, bg=C_CARD, bd=2, relief="ridge", padx=20, pady=15)
        f2.grid(row=0, column=1, padx=15)
        tk.Label(f2, text="Atacante: " + self.jugador_atk, bg=C_CARD, fg=C_ROJO,
                 font=("Arial", 12, "bold")).pack(pady=(0, 6))
        self.var_atk = tk.StringVar(value="")
        for nombre in FACCIONES:
            f_op = tk.Frame(f2, bg=C_CARD)
            f_op.pack(anchor="w")
            tk.Radiobutton(f_op, text=nombre, variable=self.var_atk, bg=C_CARD,
                           value=nombre, fg=FACCIONES[nombre],
                           font=("Arial", 11, "bold"),
                           selectcolor=C_FONDO).pack(side="left")
            tk.Label(f_op, text="(" + FACCION_DESCRIPCION[nombre] + ")",
                     bg=C_CARD, fg=C_GRIS, font=("Arial", 9)).pack(side="left")

        abajo = tk.Frame(self.root, bg=C_FONDO)
        abajo.pack(pady=15)
        self.boton(abajo, "Comenzar partida",
                   self.confirmar_facciones, C_VERDE).pack(pady=4)
        self.boton(abajo, "Volver al menu",
                   self.pantalla_login, C_GRIS).pack()

    def confirmar_facciones(self):
        d = self.var_def.get()
        a = self.var_atk.get()
        if d == "" or a == "":
            messagebox.showinfo("Aviso", "Cada jugador debe elegir una faccion")
            return
        if d == a:
            messagebox.showinfo("Aviso", "No pueden usar la misma faccion")
            return
        self.faccion_def = d
        self.faccion_atk = a

  
        self.ronda = 1
        self.ganadas_def = 0
        self.ganadas_atk = 0
  
        self.dinero_def = 0
        self.dinero_atk = 0
        self.bono_def = 0   
        self.bono_atk = 0   
        self.iniciar_ronda()

    

    def iniciar_ronda(self):
        self.dinero_def += DINERO_INICIAL + self.bono_def
        self.dinero_atk += DINERO_INICIAL + self.bono_atk
        self.bono_def = 0
        self.bono_atk = 0

        # tablero vacio
        self.tablero = []
        for f in range(FILAS):
            fila = []
            for c in range(COLUMNAS):
                fila.append(None)
            self.tablero.append(fila)

        # base central
        self.base_vida = BASE_VIDA
        self.tablero[BASE_FILA][BASE_COL] = "BASE"

        self.defensas = []  
        self.unidades = []  

        self.fase = "def"        
        self.seleccion = None    
        self.dano_ronda = 0      

        self.pantalla_juego()

    def pantalla_juego(self):
        self.limpiar()

        self.l_info = tk.Label(self.root, font=("Arial", 12, "bold"),
                               fg="white", pady=8)
        self.l_info.pack(fill="x")

        marco = tk.Frame(self.root, bg=C_BANNER, bd=3, relief="ridge")
        marco.pack(pady=8)
        self.botones = []
        for f in range(FILAS):
            filab = []
            for c in range(COLUMNAS):
                b = tk.Button(marco, text="", width=5, height=2,
                              relief="ridge", bd=1, font=("Arial", 9, "bold"),
                              command=lambda ff=f, cc=c: self.clic_celda(ff, cc))
                b.grid(row=f, column=c, padx=1, pady=1)
                filab.append(b)
            self.botones.append(filab)

        self.panel = tk.Frame(self.root, bg=C_FONDO)
        self.panel.pack(pady=8)

        log_frame = tk.Frame(self.root, bg=C_FONDO)
        log_frame.pack(pady=5)
        tk.Label(log_frame, text="Registro de combate", bg=C_FONDO,
                 fg=C_TEXTO, font=("Arial", 10, "bold")).pack(anchor="w")
        self.log = tk.Text(log_frame, height=6, width=70, bg="#FBFCFC",
                           fg=C_TEXTO, font=("Consolas", 9),
                           relief="sunken", bd=2)
        self.log.pack()

        self.dibujar_tablero()
        self.actualizar_controles()
        self.actualizar_info()

    def actualizar_info(self):
        if self.fase == "def":
            fase_txt = "Fase: Construccion (Defensor)"
            dinero = "Dinero defensor: $" + str(self.dinero_def)
            color = C_AZUL
        elif self.fase == "atk":
            fase_txt = "Fase: Compra (Atacante)"
            dinero = "Dinero atacante: $" + str(self.dinero_atk)
            color = C_ROJO
        elif self.fase == "fin":
            fase_txt = "Combate terminado"
            dinero = "Pulsa el boton para ver el resultado de la ronda"
            color = C_VERDE
        else:
            fase_txt = "Fase: Combate"
            dinero = "Vida base: " + str(self.base_vida)
            color = C_NARANJA

        texto = ("Ronda " + str(self.ronda) +
                 "    Defensor " + str(self.ganadas_def) +
                 " - " + str(self.ganadas_atk) + " Atacante\n" +
                 fase_txt + "    |    " + dinero)
        self.l_info.config(text=texto, bg=color)

    def escribir_log(self, texto):
        self.log.insert("end", texto + "\n")
        self.log.see("end")

    
    def dibujar_tablero(self):
        for f in range(FILAS):
            for c in range(COLUMNAS):
                cosa = self.tablero[f][c]
                b = self.botones[f][c]
                if cosa is None:
                    if c == 0:
                       
                        b.config(text="", bg=C_ZONA, fg="black")
                    else:
                        b.config(text="", bg=C_CELDA, fg="black")
                elif cosa == "BASE":
                    b.config(text="BASE", bg=FACCIONES[self.faccion_def],
                             fg="white")
                elif isinstance(cosa, Torre):
                    if cosa.tipo == "Muro":
                        color = COLOR_MURO[self.faccion_def]   # color de muro segun faccion
                    else:
                        color = FACCIONES[self.faccion_def]
                    b.config(text=TEXTO[cosa.tipo] + "\n" + str(cosa.vida),
                             bg=color, fg="white")
                elif isinstance(cosa, Unidad):
                    b.config(text=TEXTO[cosa.tipo] + "\n" + str(cosa.vida),
                             bg=FACCIONES[self.faccion_atk], fg="white")



    def actualizar_controles(self):
        for w in self.panel.winfo_children():
            w.destroy()

        if self.fase == "def":
            tk.Label(self.panel, text="Construir:", bg=C_FONDO, fg=C_TEXTO,
                     font=("Arial", 11, "bold")).grid(row=0, column=0, padx=4)
            col = 1
            for tipo in ["Basica", "Pesada", "Magica", "Muro"]:
                costo = TORRES[tipo][0]
                self.boton(self.panel, tipo + " ($" + str(costo) + ")",
                           lambda t=tipo: self.seleccionar(t), C_AZUL
                           ).grid(row=0, column=col, padx=2)
                col += 1
           
            self.boton(self.panel, "Quitar",
                       lambda: self.seleccionar("QUITAR"), C_ROJO
                       ).grid(row=0, column=col, padx=2)
            col += 1
            self.boton(self.panel, "Terminar construccion",
                       self.terminar_construccion, C_VERDE
                       ).grid(row=0, column=col, padx=2)

            self.l_seleccion = tk.Label(self.panel, text="Nada seleccionado",
                                        bg=C_FONDO, fg=C_TEXTO,
                                        font=("Arial", 10, "italic"))
            self.l_seleccion.grid(row=1, column=0, columnspan=col + 1, pady=6)
            tk.Label(self.panel,
                     text="Tip: las torres van de la columna 1 en adelante. "
                          "Con 'Quitar' puedes recuperar el dinero de una pieza.",
                     bg=C_FONDO, fg=C_GRIS, font=("Arial", 9)
                     ).grid(row=2, column=0, columnspan=col + 1)

        elif self.fase == "atk":
            tk.Label(self.panel, text="Comprar unidad:", bg=C_FONDO, fg=C_TEXTO,
                     font=("Arial", 11, "bold")).grid(row=0, column=0, padx=4)
            col = 1
            for tipo in ["Soldado", "Tanque", "Rapida"]:
                costo = UNIDADES[tipo][0]
                self.boton(self.panel, tipo + " ($" + str(costo) + ")",
                           lambda t=tipo: self.seleccionar(t), C_ROJO
                           ).grid(row=0, column=col, padx=2)
                col += 1
          
            self.boton(self.panel, "Quitar",
                       lambda: self.seleccionar("QUITAR"), C_GRIS
                       ).grid(row=0, column=col, padx=2)
            col += 1
            self.boton(self.panel, "Iniciar combate",
                       self.iniciar_combate, C_VERDE
                       ).grid(row=0, column=col, padx=2)

            self.l_seleccion = tk.Label(self.panel, text="Nada seleccionado",
                                        bg=C_FONDO, fg=C_TEXTO,
                                        font=("Arial", 10, "italic"))
            self.l_seleccion.grid(row=1, column=0, columnspan=col + 1, pady=6)
            tk.Label(self.panel,
                     text="Tip: las unidades se colocan en la columna 0 (zona naranja).",
                     bg=C_FONDO, fg=C_GRIS, font=("Arial", 9)
                     ).grid(row=2, column=0, columnspan=col + 1)

        elif self.fase == "fin":
            tk.Label(self.panel, text="El combate termino.", bg=C_FONDO,
                     fg=C_TEXTO, font=("Arial", 11, "bold")
                     ).grid(row=0, column=0, padx=4)
            self.boton(self.panel, "Ver resultado de la ronda",
                       self.continuar_resultado, C_VERDE
                       ).grid(row=0, column=1, padx=5)

        else:  
            self.boton(self.panel, "Siguiente turno",
                       self.turno, C_AZUL).grid(row=0, column=0, padx=5)
            self.boton(self.panel, "Combatir todo",
                       self.combatir_todo, C_NARANJA).grid(row=0, column=1, padx=5)

    def seleccionar(self, tipo):
        self.seleccion = tipo
        if tipo == "QUITAR":
            self.l_seleccion.config(
                text="Modo QUITAR activado: haz clic en una pieza para quitarla")
            self.escribir_log("Modo QUITAR activado")
        else:
            self.l_seleccion.config(text="Seleccionado: " + tipo)
            self.escribir_log("Seleccionado: " + tipo)

    

    def clic_celda(self, f, c):
        if self.fase == "def":
            if self.seleccion == "QUITAR":
                self.quitar_pieza(f, c)
            else:
                self.colocar_defensa(f, c)
        elif self.fase == "atk":
            if self.seleccion == "QUITAR":
                self.quitar_pieza(f, c)
            else:
                self.colocar_unidad(f, c)
        

    def colocar_defensa(self, f, c):
        if self.seleccion is None:
            messagebox.showinfo("Aviso", "Primero elija que construir")
            return
        if self.tablero[f][c] is not None:
            messagebox.showinfo("Aviso", "Esa casilla esta ocupada")
            return
        if c == 0:
            messagebox.showinfo("Aviso", "La columna 0 es del atacante")
            return

        costo = TORRES[self.seleccion][0]
        if self.dinero_def < costo:
            messagebox.showinfo("Aviso", "No tiene suficiente dinero")
            return

        self.dinero_def -= costo
        self.tablero[f][c] = Torre(self.seleccion, f, c, self.faccion_def)
        self.defensas.append(self.tablero[f][c])
        self.dibujar_tablero()
        self.actualizar_info()

    def colocar_unidad(self, f, c):
        if self.seleccion is None:
            messagebox.showinfo("Aviso", "Primero elija una unidad")
            return
        if c != 0:
            messagebox.showinfo("Aviso", "Las unidades se colocan en la columna 0")
            return
        if self.tablero[f][c] is not None:
            messagebox.showinfo("Aviso", "Esa casilla esta ocupada")
            return

        costo = UNIDADES[self.seleccion][0]
        if self.dinero_atk < costo:
            messagebox.showinfo("Aviso", "No tiene suficiente dinero")
            return

        self.dinero_atk -= costo
        self.tablero[f][c] = Unidad(self.seleccion, f, c, self.faccion_atk)
        self.unidades.append(self.tablero[f][c])
        self.dibujar_tablero()
        self.actualizar_info()

    def quitar_pieza(self, f, c):
       
        cosa = self.tablero[f][c]

        if self.fase == "def":
            if cosa == "BASE":
                messagebox.showinfo("Aviso", "No se puede quitar la base")
                return
            if not isinstance(cosa, Torre):
                messagebox.showinfo("Aviso", "Ahi no hay nada para quitar")
                return
            reembolso = cosa.costo
            if self.faccion_def == "Naturaleza":
                reembolso = int(reembolso * FACCION_BONOS["Naturaleza"]["reembolso"])
            self.dinero_def += reembolso
            self.tablero[f][c] = None
            if cosa in self.defensas:
                self.defensas.remove(cosa)
            self.escribir_log("Se quito " + TEXTO[cosa.tipo] +
                              " (+$" + str(reembolso) + ")")

        elif self.fase == "atk":
            if not isinstance(cosa, Unidad):
                messagebox.showinfo("Aviso", "Ahi no hay nada para quitar")
                return
            reembolso = cosa.costo
            if self.faccion_atk == "Naturaleza":
                reembolso = int(reembolso * FACCION_BONOS["Naturaleza"]["reembolso"])
            self.dinero_atk += reembolso
            self.tablero[f][c] = None
            if cosa in self.unidades:
                self.unidades.remove(cosa)
            self.escribir_log("Se quito " + TEXTO[cosa.tipo] +
                              " (+$" + str(reembolso) + ")")

        self.dibujar_tablero()
        self.actualizar_info()

    def terminar_construccion(self):
        self.fase = "atk"
        self.seleccion = None
        self.escribir_log("--- Turno del atacante ---")
        self.actualizar_controles()
        self.actualizar_info()
        self.revisar_dinero_atacante()

    def revisar_dinero_atacante(self):
     
        costo_minimo = min(UNIDADES[t][0] for t in UNIDADES)
        if self.dinero_atk < costo_minimo:
            messagebox.showinfo(
                "Ronda",
                "El atacante no tiene dinero para comprar unidades. Gana el defensor.")
            self.fin_ronda("def")

    def iniciar_combate(self):
        if len(self.unidades) == 0:
            
            messagebox.showinfo("Ronda", "El atacante no tiene unidades. Gana el defensor.")
            self.fin_ronda("def")
            return
        self.fase = "combate"
        self.seleccion = None
        self.escribir_log("--- Comienza el combate ---")
        self.actualizar_controles()
        self.actualizar_info()

   

    def habilidad_torre(self, t):
        # devuelve el efecto segun el tipo de torre
        if t.tipo == "Basica":
            return "doble"      # disparo doble
        if t.tipo == "Pesada":
            return "area"       # dano en area
        if t.tipo == "Magica":
            return "congelar"   # congelar unidad
        return None

    def habilidad_unidad(self, u):
        # devuelve el efecto segun el tipo de unidad
        if u.tipo == "Soldado":
            return "doble"      # ataque doble
        if u.tipo == "Tanque":
            return "escudo"     # escudo temporal
        if u.tipo == "Rapida":
            return "veloz"      # aumento de velocidad
        return None

 

    def distancia(self, f1, c1, f2, c2):

        return max(abs(f1 - f2), abs(c1 - c2))

    def turno(self):
        if self.fase != "combate":
            return

        for t in self.defensas:
            if t.vida <= 0 or t.tipo == "Muro":
                continue

       
            en_rango = []
            for u in self.unidades:
                if u.vida > 0 and self.distancia(t.fila, t.col, u.fila, u.col) <= t.alcance:
                    en_rango.append(u)
            if len(en_rango) == 0:
                continue

           
            t.contador += 1
            efecto = None
            if t.cooldown > 0 and t.contador >= t.cooldown:
                t.contador = 0
                efecto = self.habilidad_torre(t)

            if efecto == "area":
     
                for u in en_rango:
                    self.dano_a_unidad(u, t.dano)
                self.escribir_log(TEXTO[t.tipo] + " usa DANO EN AREA")
            else:
              
                objetivo = en_rango[0]
                for u in en_rango:
                    if self.distancia(t.fila, t.col, u.fila, u.col) < \
                       self.distancia(t.fila, t.col, objetivo.fila, objetivo.col):
                        objetivo = u

                dano = t.dano
                if efecto == "doble":
                    dano = dano * 2
                    self.escribir_log(TEXTO[t.tipo] + " usa DISPARO DOBLE")
                if efecto == "congelar":
                    objetivo.congelada = True
                    self.escribir_log(TEXTO[t.tipo] + " CONGELA una unidad")

                self.dano_a_unidad(objetivo, dano)

        self.limpiar_muertos()

    
        for u in list(self.unidades):
            if u.vida <= 0:
                continue
            if u.congelada:
                u.congelada = False
                self.escribir_log("Una unidad esta congelada y no se mueve")
                continue

           
            u.contador += 1
            efecto = None
            if u.cooldown > 0 and u.contador >= u.cooldown:
                u.contador = 0
                efecto = self.habilidad_unidad(u)

            pasos = u.velocidad
            ataque_doble = False
            if efecto == "veloz":
                pasos += 1
                self.escribir_log(TEXTO[u.tipo] + " aumenta su VELOCIDAD")
            if efecto == "doble":
                ataque_doble = True
            if efecto == "escudo":
                u.escudo = True
                self.escribir_log(TEXTO[u.tipo] + " activa ESCUDO")

           
            for _ in range(pasos):
                if u.vida <= 0:
                    break
                self.mover_unidad(u, ataque_doble)
                ataque_doble = False   

        self.limpiar_muertos()
        self.dibujar_tablero()
        self.actualizar_info()

        if self.base_vida <= 0:
            self.escribir_log(">>> La base fue destruida <<<")
            self.fin_ronda("atk")
            return

        vivos = 0
        for u in self.unidades:
            if u.vida > 0:
                vivos += 1
        if vivos == 0:
            self.escribir_log(">>> Todas las unidades fueron eliminadas <<<")
            self.fin_ronda("def")
            return

    def dano_a_unidad(self, u, dano):
        if u.escudo:
            dano = dano // 2  
            u.escudo = False
        u.vida -= dano
        if u.vida <= 0:
            
            self.bono_def += u.recompensa
            self.escribir_log("Unidad " + TEXTO[u.tipo] + " eliminada (+" +
                              str(u.recompensa) + " al defensor)")

    def mover_unidad(self, u, ataque_doble):
        df = BASE_FILA - u.fila
        dc = BASE_COL - u.col

        if abs(dc) >= abs(df):
            opciones = [(0, self.signo(dc)), (self.signo(df), 0)]
        else:
            opciones = [(self.signo(df), 0), (0, self.signo(dc))]

        for (mf, mc) in opciones:
            if mf == 0 and mc == 0:
                continue
            nf = u.fila + mf
            nc = u.col + mc
            if nf < 0 or nf >= FILAS or nc < 0 or nc >= COLUMNAS:
                continue

            destino = self.tablero[nf][nc]

            if destino == "BASE":
                dano = u.dano
                if ataque_doble:
                    dano = dano * 2
                self.base_vida -= dano
                self.dano_ronda += dano
                self.bono_atk += dano // 8
                self.escribir_log(TEXTO[u.tipo] + " ataca la BASE (-" +
                                  str(dano) + ")")
                return

            if isinstance(destino, Torre):
                dano = u.dano
                if ataque_doble:
                    dano = dano * 2
                destino.vida -= dano
                self.dano_ronda += dano
                self.bono_atk += dano // 8
                self.escribir_log(TEXTO[u.tipo] + " ataca " +
                                  TEXTO[destino.tipo])
                if destino.vida <= 0:
                    bono_destruccion = destino.costo // 2
                    self.bono_atk += bono_destruccion
                    self.escribir_log(TEXTO[destino.tipo] + " destruida (+" +
                                      str(bono_destruccion) + " al atacante)")
                    self.tablero[destino.fila][destino.col] = None
                return

            if destino is None:
                self.tablero[u.fila][u.col] = None
                u.fila = nf
                u.col = nc
                self.tablero[nf][nc] = u
                return


    def signo(self, n):
        if n > 0:
            return 1
        if n < 0:
            return -1
        return 0

    def limpiar_muertos(self):
        nuevas = []
        for u in self.unidades:
            if u.vida > 0:
                nuevas.append(u)
            else:
                if self.tablero[u.fila][u.col] is u:
                    self.tablero[u.fila][u.col] = None
        self.unidades = nuevas

        nuevas_def = []
        for t in self.defensas:
            if t.vida > 0:
                nuevas_def.append(t)
        self.defensas = nuevas_def

    def combatir_todo(self):
   
        limite = 100
        while self.fase == "combate" and limite > 0:
            self.turno()
            if self.fase != "combate":
                break  
            self.dibujar_tablero()
            self.root.update()
            time.sleep(0.25)
            limite -= 1


    def fin_ronda(self, ganador):
        self.fase = "fin"

        if ganador == "def":
            self.ganadas_def += 1
        else:
            self.ganadas_atk += 1

        self.ganador_ronda = ganador

        self.actualizar_controles()
        self.actualizar_info()

    def continuar_resultado(self):
        ganador = self.ganador_ronda

        if self.ganadas_def == 3:
            self.fin_partida("def")
            return
        if self.ganadas_atk == 3:
            self.fin_partida("atk")
            return

        self.pantalla_fin_ronda(ganador)

    def pantalla_fin_ronda(self, ganador):
        self.limpiar()

        if ganador == "def":
            texto_ganador = "Gano la ronda el DEFENSOR"
            color = C_AZUL
        else:
            texto_ganador = "Gano la ronda el ATACANTE"
            color = C_ROJO

        self.banner("FIN DE LA RONDA " + str(self.ronda))

        tk.Label(self.root, text=texto_ganador, font=("Arial", 18, "bold"),
                 bg=C_FONDO, fg=color).pack(pady=15)
        tk.Label(self.root,
                 text="Marcador:   Defensor " + str(self.ganadas_def) +
                      "   -   " + str(self.ganadas_atk) + " Atacante",
                 font=("Arial", 14, "bold"), bg=C_FONDO, fg=C_TEXTO).pack(pady=5)
        tk.Label(self.root, text="(El primero en ganar 3 rondas gana la partida)",
                 font=("Arial", 10), bg=C_FONDO, fg=C_GRIS).pack(pady=5)

        marco = tk.Frame(self.root, bg=C_FONDO)
        marco.pack(pady=20)
        self.boton(marco, "Siguiente ronda",
                   self.siguiente_ronda, C_VERDE).grid(row=0, column=0, padx=10)
        self.boton(marco, "Volver al menu",
                   self.pantalla_login, C_GRIS).grid(row=0, column=1, padx=10)

    def siguiente_ronda(self):
        self.ronda += 1
        self.iniciar_ronda()

    def fin_partida(self, ganador):
        if ganador == "def":
            self.jugadores[self.jugador_def]["vic_def"] += 1
            campeon = self.jugador_def + " (Defensor)"
        else:
            self.jugadores[self.jugador_atk]["vic_atk"] += 1
            campeon = self.jugador_atk + " (Atacante)"

        self.guardar_jugadores()

        # pantalla de fin de partida
        self.limpiar()
        self.banner("FIN DE LA PARTIDA")
        tk.Label(self.root, text="El ganador de la partida es:",
                 font=("Arial", 14), bg=C_FONDO, fg=C_TEXTO).pack(pady=(20, 5))
        tk.Label(self.root, text=campeon, font=("Arial", 20, "bold"),
                 bg=C_FONDO, fg=C_VERDE).pack(pady=5)
        tk.Label(self.root,
                 text="Marcador final:   Defensor " + str(self.ganadas_def) +
                      "   -   " + str(self.ganadas_atk) + " Atacante",
                 font=("Arial", 13, "bold"), bg=C_FONDO, fg=C_TEXTO).pack(pady=10)

        abajo = tk.Frame(self.root, bg=C_FONDO)
        abajo.pack(pady=20)
        self.boton(abajo, "Volver al menu",
                   self.pantalla_login, C_AZUL).grid(row=0, column=0, padx=10)
        self.boton(abajo, "Ver Top de jugadores",
                   self.pantalla_top, C_GRIS).grid(row=0, column=1, padx=10)

    def pantalla_top(self):
        self.limpiar()
        self.banner("TOP DE JUGADORES")

        marco = tk.Frame(self.root, bg=C_FONDO)
        marco.pack(pady=15)

        # top defensores
        f1 = tk.Frame(marco, bg=C_CARD, bd=2, relief="ridge", padx=20, pady=15)
        f1.grid(row=0, column=0, padx=15)
        tk.Label(f1, text="Mejores DEFENSORES", bg=C_CARD, fg=C_AZUL,
                 font=("Arial", 12, "bold")).pack(pady=(0, 6))
        lista_def = sorted(self.jugadores.items(),
                           key=lambda x: x[1]["vic_def"], reverse=True)
        i = 1
        for nombre, datos in lista_def[:5]:
            tk.Label(f1, text=str(i) + ". " + nombre + " - " +
                     str(datos["vic_def"]) + " victorias",
                     bg=C_CARD, fg=C_TEXTO).pack(anchor="w")
            i += 1

        # top atacantes
        f2 = tk.Frame(marco, bg=C_CARD, bd=2, relief="ridge", padx=20, pady=15)
        f2.grid(row=0, column=1, padx=15)
        tk.Label(f2, text="Mejores ATACANTES", bg=C_CARD, fg=C_ROJO,
                 font=("Arial", 12, "bold")).pack(pady=(0, 6))
        lista_atk = sorted(self.jugadores.items(),
                           key=lambda x: x[1]["vic_atk"], reverse=True)
        i = 1
        for nombre, datos in lista_atk[:5]:
            tk.Label(f2, text=str(i) + ". " + nombre + " - " +
                     str(datos["vic_atk"]) + " victorias",
                     bg=C_CARD, fg=C_TEXTO).pack(anchor="w")
            i += 1

        self.boton(self.root, "Volver", self.pantalla_login, C_GRIS).pack(pady=15)



if __name__ == "__main__":
    ventana = tk.Tk()
    juego = Juego(ventana)
    ventana.mainloop()