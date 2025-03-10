#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo para la gestión de personajes en la aplicación D&D Combat Manager.
"""

import tkinter as tk
from tkinter import ttk, messagebox, font
import json
import os
from tkinter import scrolledtext

# Definición de constantes
CLASES = ["Bárbaro", "Bardo", "Brujo", "Clérigo", "Druida", "Explorador", 
          "Guerrero", "Hechicero", "Mago", "Monje", "Paladín", "Pícaro"]

CLASES_MAGICAS = ["Bardo", "Brujo", "Clérigo", "Druida", "Explorador", 
                 "Hechicero", "Mago", "Paladín"]

RAZAS = ["Humano", "Elfo", "Enano", "Halfling", "Gnomo", "Semielfo", 
         "Semiorco", "Tiefling", "Draconido"]

ESTADISTICAS = ["Fuerza", "Destreza", "Constitución", "Inteligencia", "Sabiduría", "Carisma"]

COMPETENCIAS = [
    "Acrobacias", "Arcanos", "Atletismo", "Engaño", "Historia", 
    "Interpretación", "Intimidación", "Investigación", "Juego de Manos", 
    "Medicina", "Naturaleza", "Percepción", "Perspicacia", "Persuasión", 
    "Religión", "Sigilo", "Supervivencia", "Trato con Animales"
]

# Tabla de experiencia necesaria para cada nivel según D&D 5e
TABLA_EXPERIENCIA = {
    1: 0,
    2: 300,
    3: 900,
    4: 2700,
    5: 6500,
    6: 14000,
    7: 23000,
    8: 34000,
    9: 48000,
    10: 64000,
    11: 85000,
    12: 100000,
    13: 120000,
    14: 140000,
    15: 165000,
    16: 195000,
    17: 225000,
    18: 265000,
    19: 305000,
    20: 355000
}

def mostrar_gestor_personajes(root, callback_menu):
    """
    Muestra la pantalla principal del gestor de personajes
    
    Args:
        root: La ventana principal de la aplicación
        callback_menu: Función para volver al menú principal
    """
    # Ocultar frames existentes
    for widget in root.winfo_children():
        if isinstance(widget, ttk.Frame):
            widget.pack_forget()
    
    # Crear contenedor principal con scrollbar
    main_container = ttk.Frame(root)
    main_container.pack(fill="both", expand=True)
    
    # Crear canvas con scrollbar para contenido adaptable
    canvas = tk.Canvas(main_container)
    scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
    gestor_frame = ttk.Frame(canvas)
    
    # Configurar canvas y scrollbar
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Crear ventana dentro del canvas para el frame
    def configure_frame(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.itemconfig(frame_id, width=event.width)
    
    frame_id = canvas.create_window((0, 0), window=gestor_frame, anchor="nw")
    gestor_frame.bind("<Configure>", configure_frame)
    canvas.bind("<Configure>", lambda e: configure_frame(e))
    
    # Título
    titulo = ttk.Label(gestor_frame, text="Gestor de Personajes", style="Title.TLabel")
    titulo.pack(pady=(20, 10))
    
    # Directorio donde se guardarán los personajes
    directorio_personajes = "personajes"
    if not os.path.exists(directorio_personajes):
        os.makedirs(directorio_personajes)
    
    # Frame para la lista de personajes
    lista_frame = ttk.Frame(gestor_frame)
    lista_frame.pack(fill="both", expand=True, padx=50, pady=10)
    
    # Configurar grid para que se expanda
    for i in range(7):  # 7 columnas (añadida columna para nivel/XP)
        lista_frame.columnconfigure(i, weight=1)
    
    # Obtener lista de personajes guardados
    personajes = []
    try:
        for archivo in os.listdir(directorio_personajes):
            if archivo.endswith('.json'):
                ruta = os.path.join(directorio_personajes, archivo)
                with open(ruta, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
                    personajes.append(datos)
    except Exception as e:
        messagebox.showerror("Error", f"Error al cargar los personajes: {str(e)}")
    
    # Mostrar personajes
    if not personajes:
        ttk.Label(lista_frame, text="No hay personajes creados").pack(pady=20)
    else:
        # Crear cabecera
        ttk.Label(lista_frame, text="Nombre", font=('Helvetica', 11, 'bold')).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Label(lista_frame, text="Clase", font=('Helvetica', 11, 'bold')).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ttk.Label(lista_frame, text="Raza", font=('Helvetica', 11, 'bold')).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        ttk.Label(lista_frame, text="Nivel/XP", font=('Helvetica', 11, 'bold')).grid(row=0, column=3, padx=5, pady=5, sticky="w")
        ttk.Label(lista_frame, text="Estadísticas", font=('Helvetica', 11, 'bold')).grid(row=0, column=4, padx=5, pady=5, sticky="w")
        ttk.Label(lista_frame, text="Ataques", font=('Helvetica', 11, 'bold')).grid(row=0, column=5, padx=5, pady=5, sticky="w")
        ttk.Label(lista_frame, text="Acciones", font=('Helvetica', 11, 'bold')).grid(row=0, column=6, padx=5, pady=5, sticky="w")
        
        # Mostrar personajes
        for i, personaje in enumerate(personajes):
            ttk.Label(lista_frame, text=personaje.get("nombre", "")).grid(row=i+1, column=0, padx=5, pady=3, sticky="w")
            
            # Clase (con indicador de magia si corresponde)
            clase = personaje.get("clase", "")
            if clase in CLASES_MAGICAS:
                ttk.Label(lista_frame, text=f"{clase} ✨").grid(row=i+1, column=1, padx=5, pady=3, sticky="w")
            else:
                ttk.Label(lista_frame, text=clase).grid(row=i+1, column=1, padx=5, pady=3, sticky="w")
            
            ttk.Label(lista_frame, text=personaje.get("raza", "")).grid(row=i+1, column=2, padx=5, pady=3, sticky="w")
            
            # Nivel y experiencia
            nivel = personaje.get("nivel", 1)
            experiencia = personaje.get("experiencia", 0)
            ttk.Label(lista_frame, text=f"Nv.{nivel} ({experiencia} XP)").grid(row=i+1, column=3, padx=5, pady=3, sticky="w")
            
            # Estadísticas en formato resumido
            estadisticas = personaje.get("estadisticas", {})
            texto_stats = f"F:{estadisticas.get('Fuerza', '-')} "
            texto_stats += f"D:{estadisticas.get('Destreza', '-')} "
            texto_stats += f"C:{estadisticas.get('Constitución', '-')} "
            texto_stats += f"I:{estadisticas.get('Inteligencia', '-')} "
            texto_stats += f"S:{estadisticas.get('Sabiduría', '-')} "
            texto_stats += f"CA:{estadisticas.get('Carisma', '-')}"
            
            ttk.Label(lista_frame, text=texto_stats).grid(row=i+1, column=4, padx=5, pady=3, sticky="w")
            
            # Información de ataques
            ataque_info = ""
            if clase in CLASES_MAGICAS:
                ataque_info += f"Conj: {personaje.get('ataque_conjuro', '+0')} "
                ataque_info += f"CD: {personaje.get('cd_conjuro', '10')} "
            ataque_info += f"F: {personaje.get('ataque_fuerza', '+0')} "
            ataque_info += f"D: {personaje.get('ataque_destreza', '+0')}"
            
            ttk.Label(lista_frame, text=ataque_info, foreground="#8B0000").grid(row=i+1, column=5, padx=5, pady=3, sticky="w")
            
            # Botones de acción
            acciones_frame = ttk.Frame(lista_frame)
            acciones_frame.grid(row=i+1, column=6, padx=5, pady=3, sticky="w")
            
            # Índice actual para las lambdas
            idx = i
            personaje_actual = personaje
            ttk.Button(acciones_frame, text="Editar", 
                      command=lambda p=personaje_actual: editar_personaje(p)).pack(side="left", padx=2)
            
            ttk.Button(acciones_frame, text="Eliminar", 
                      command=lambda p=personaje_actual: eliminar_personaje(p)).pack(side="left", padx=2)
    
    def editar_personaje(personaje):
        """Muestra la pantalla de edición de personaje"""
        mostrar_crear_editar_personaje(root, personaje, directorio_personajes, 
                                      lambda: mostrar_gestor_personajes(root, callback_menu))
    
    def eliminar_personaje(personaje):
        """Elimina un personaje"""
        if messagebox.askyesno("Confirmar", f"¿Está seguro que desea eliminar el personaje '{personaje.get('nombre', '')}'?"):
            try:
                ruta = os.path.join(directorio_personajes, personaje.get("archivo", ""))
                if os.path.exists(ruta):
                    os.remove(ruta)
                    messagebox.showinfo("Éxito", "Personaje eliminado correctamente.")
                    mostrar_gestor_personajes(root, callback_menu)  # Actualizar vista
                else:
                    messagebox.showerror("Error", "El archivo del personaje no existe.")
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar el personaje: {str(e)}")
    
    # Frame para botones
    botones_frame = ttk.Frame(gestor_frame)
    botones_frame.pack(fill="x", padx=50, pady=10)
    
    # Función para volver al menú
    def volver_menu():
        # Desenlazar eventos de scroll
        canvas.unbind_all("<MouseWheel>")
        # Destruir el contenedor principal
        main_container.destroy()
        # Llamar al callback del menú principal
        callback_menu()
    
    # Botón para crear nuevo personaje
    ttk.Button(botones_frame, text="Crear Nuevo Personaje", 
              command=lambda: mostrar_crear_editar_personaje(root, None, directorio_personajes, 
                                                           lambda: mostrar_gestor_personajes(root, callback_menu))).pack(side="left", padx=5, pady=10)
    
    # Botón para volver al menú
    ttk.Button(botones_frame, text="Volver al Menú", 
              command=volver_menu).pack(side="right", padx=5, pady=10)
    
    # Añadir atajos de teclado para navegación con scroll
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    # Actualizar canvas después de que todo esté configurado
    canvas.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))

def mostrar_crear_editar_personaje(root, personaje, directorio_personajes, callback_volver):
    """
    Muestra la pantalla para crear o editar un personaje
    
    Args:
        root: La ventana principal de la aplicación
        personaje: Datos del personaje a editar o None para crear uno nuevo
        directorio_personajes: Directorio donde se guardarán los personajes
        callback_volver: Función para volver a la pantalla de gestor de personajes
    """
    # Ocultar frames existentes
    for widget in root.winfo_children():
        if isinstance(widget, ttk.Frame):
            widget.pack_forget()
    
    # Determinar si es creación o edición
    modo = "Editar" if personaje else "Crear"
    
    # Crear contenedor principal con scrollbar
    main_container = ttk.Frame(root)
    main_container.pack(fill="both", expand=True)
    
    # Crear canvas con scrollbar para contenido adaptable
    canvas = tk.Canvas(main_container)
    scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
    editar_frame = ttk.Frame(canvas)
    
    # Configurar canvas y scrollbar
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Crear ventana dentro del canvas para el frame
    def configure_frame(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.itemconfig(frame_id, width=event.width)
    
    frame_id = canvas.create_window((0, 0), window=editar_frame, anchor="nw")
    editar_frame.bind("<Configure>", configure_frame)
    canvas.bind("<Configure>", lambda e: configure_frame(e))
    
    # Título
    titulo = ttk.Label(editar_frame, text=f"{modo} Personaje", style="Title.TLabel")
    titulo.pack(pady=(20, 10))
    
    # Panel con pestañas
    notebook = ttk.Notebook(editar_frame)
    notebook.pack(fill="both", expand=True, padx=20, pady=10)
    
    # ===== DATOS BÁSICOS =====
    tab_basicos = ttk.Frame(notebook)
    notebook.add(tab_basicos, text="Datos Básicos")
    
    # Configurar tab
    tab_basicos.columnconfigure(1, weight=1)
    
    # Nombre
    ttk.Label(tab_basicos, text="Nombre:").grid(row=0, column=0, sticky="w", padx=10, pady=10)
    nombre_var = tk.StringVar(value=personaje.get("nombre", "") if personaje else "")
    ttk.Entry(tab_basicos, textvariable=nombre_var, width=40).grid(row=0, column=1, sticky="ew", padx=10, pady=10)
    
    # Clase
    ttk.Label(tab_basicos, text="Clase:").grid(row=1, column=0, sticky="w", padx=10, pady=10)
    clase_var = tk.StringVar(value=personaje.get("clase", "") if personaje else "")
    ttk.Combobox(tab_basicos, textvariable=clase_var, values=CLASES, width=38).grid(row=1, column=1, sticky="ew", padx=10, pady=10)
    
    # Raza
    ttk.Label(tab_basicos, text="Raza:").grid(row=2, column=0, sticky="w", padx=10, pady=10)
    raza_var = tk.StringVar(value=personaje.get("raza", "") if personaje else "")
    ttk.Combobox(tab_basicos, textvariable=raza_var, values=RAZAS, width=38).grid(row=2, column=1, sticky="ew", padx=10, pady=10)
    
    # Nivel y Experiencia
    nivel_frame = ttk.Frame(tab_basicos)
    nivel_frame.grid(row=3, column=0, columnspan=2, sticky="w", padx=10, pady=10)
    
    ttk.Label(nivel_frame, text="Nivel:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
    nivel_var = tk.StringVar(value=str(personaje.get("nivel", 1)) if personaje else "1")
    nivel_entry = ttk.Spinbox(nivel_frame, from_=1, to=20, textvariable=nivel_var, width=5)
    nivel_entry.grid(row=0, column=1, padx=5, pady=5)
    
    ttk.Label(nivel_frame, text="Experiencia:").grid(row=0, column=2, sticky="w", padx=20, pady=5)
    experiencia_var = tk.StringVar(value=str(personaje.get("experiencia", 0)) if personaje else "0")
    experiencia_entry = ttk.Entry(nivel_frame, textvariable=experiencia_var, width=10)
    experiencia_entry.grid(row=0, column=3, padx=5, pady=5)
    
    # Información sobre experiencia
    exp_info_frame = ttk.Frame(tab_basicos)
    exp_info_frame.grid(row=4, column=0, columnspan=2, sticky="w", padx=10, pady=0)
    
    ttk.Label(exp_info_frame, text="Experiencia para siguiente nivel:", font=('Helvetica', 10)).grid(row=0, column=0, sticky="w", padx=10, pady=2)
    exp_siguiente_var = tk.StringVar(value="")
    ttk.Label(exp_info_frame, textvariable=exp_siguiente_var, width=10).grid(row=0, column=1, sticky="w", padx=5, pady=2)
    
    ttk.Label(exp_info_frame, text="Experiencia restante:", font=('Helvetica', 10)).grid(row=1, column=0, sticky="w", padx=10, pady=2)
    exp_restante_var = tk.StringVar(value="")
    ttk.Label(exp_info_frame, textvariable=exp_restante_var, width=10).grid(row=1, column=1, sticky="w", padx=5, pady=2)
    
    # Función para actualizar nivel basado en la experiencia
    def calcular_nivel_desde_experiencia():
        try:
            experiencia = int(experiencia_var.get())
            # Encontrar el nivel correspondiente a la experiencia
            nuevo_nivel = 1
            for lvl, exp_needed in sorted(TABLA_EXPERIENCIA.items()):
                if experiencia >= exp_needed:
                    nuevo_nivel = lvl
                else:
                    break
            
            # Actualizar nivel
            nivel_var.set(str(nuevo_nivel))
            
            # Calcular experiencia para siguiente nivel y restante
            if nuevo_nivel < 20:
                exp_siguiente = TABLA_EXPERIENCIA[nuevo_nivel + 1]
                exp_restante = exp_siguiente - experiencia
                exp_siguiente_var.set(str(exp_siguiente))
                exp_restante_var.set(str(exp_restante))
            else:
                exp_siguiente_var.set("Máx.")
                exp_restante_var.set("Máx.")
            
            # Actualizar bonificadores relacionados con el nivel
            calcular_modificador()
            
        except ValueError:
            experiencia_var.set("0")
            nivel_var.set("1")
            exp_siguiente_var.set("300")
            exp_restante_var.set("300")
    
    # Función para actualizar experiencia basada en el nivel
    def calcular_experiencia_desde_nivel():
        try:
            nivel = int(nivel_var.get())
            if nivel < 1:
                nivel = 1
                nivel_var.set("1")
            elif nivel > 20:
                nivel = 20
                nivel_var.set("20")
            
            # Establecer experiencia mínima para el nivel
            experiencia = TABLA_EXPERIENCIA[nivel]
            experiencia_var.set(str(experiencia))
            
            # Calcular experiencia para siguiente nivel y restante
            if nivel < 20:
                exp_siguiente = TABLA_EXPERIENCIA[nivel + 1]
                exp_restante = exp_siguiente - experiencia
                exp_siguiente_var.set(str(exp_siguiente))
                exp_restante_var.set(str(exp_restante))
            else:
                exp_siguiente_var.set("Máx.")
                exp_restante_var.set("Máx.")
            
            # Actualizar bonificadores relacionados con el nivel
            calcular_modificador()
            
        except (ValueError, KeyError):
            nivel_var.set("1")
            experiencia_var.set("0")
            exp_siguiente_var.set("300")
            exp_restante_var.set("300")
    
    # Vincular eventos para nivel y experiencia
    nivel_entry.bind("<KeyRelease>", lambda e: calcular_experiencia_desde_nivel())
    nivel_entry.bind("<<Increment>>", lambda e: calcular_experiencia_desde_nivel())
    nivel_entry.bind("<<Decrement>>", lambda e: calcular_experiencia_desde_nivel())
    
    experiencia_entry.bind("<KeyRelease>", lambda e: calcular_nivel_desde_experiencia())
    
    # ===== ESTADÍSTICAS Y COMPETENCIAS =====
    tab_estadisticas = ttk.Frame(notebook)
    notebook.add(tab_estadisticas, text="Estadísticas y Competencias")
    
    # Frame para estadísticas
    stats_frame = ttk.LabelFrame(tab_estadisticas, text="Estadísticas")
    stats_frame.pack(fill="x", padx=10, pady=10)
    
    # Variables para estadísticas
    stats_vars = {}
    mod_vars = {}
    stats_datos = personaje.get("estadisticas", {}) if personaje else {}
    
    # Función para calcular modificador
    def calcular_modificador(event=None):
        for stat in ESTADISTICAS:
            try:
                valor = int(stats_vars[stat].get())
                mod = (valor - 10) // 2
                mod_vars[stat].set(f"{'+' if mod >= 0 else ''}{mod}")
            except (ValueError, KeyError):
                mod_vars[stat].set("")
        
        # Actualizar bonificador de competencia basado en nivel
        try:
            nivel = int(nivel_var.get())
            comp = 2 + ((nivel - 1) // 4)
            bonif_comp_var.set(f"+{comp}")
        except (ValueError, KeyError):
            bonif_comp_var.set("+2")
        
        # Actualizar valores calculados para conjuros
        actualizar_ataques_conjuro()
    
    # Crear campos para estadísticas
    for i, stat in enumerate(ESTADISTICAS):
        ttk.Label(stats_frame, text=stat).grid(row=i, column=0, sticky="w", padx=10, pady=5)
        
        # Valor de estadística
        stats_vars[stat] = tk.StringVar(value=stats_datos.get(stat, "10"))
        entrada = ttk.Spinbox(stats_frame, from_=1, to=30, textvariable=stats_vars[stat], width=5)
        entrada.grid(row=i, column=1, padx=5, pady=5)
        entrada.bind("<KeyRelease>", calcular_modificador)
        entrada.bind("<<Increment>>", calcular_modificador)
        entrada.bind("<<Decrement>>", calcular_modificador)
        
        # Modificador
        ttk.Label(stats_frame, text="Mod:").grid(row=i, column=2, padx=5, pady=5)
        mod_vars[stat] = tk.StringVar()
        ttk.Label(stats_frame, textvariable=mod_vars[stat], width=3).grid(row=i, column=3, padx=5, pady=5)
    
    # Frame para bonificador de competencia
    comp_bonus_frame = ttk.Frame(stats_frame)
    comp_bonus_frame.grid(row=len(ESTADISTICAS), column=0, columnspan=4, sticky="w", padx=10, pady=10)
    ttk.Label(comp_bonus_frame, text="Bonif. Competencia:").pack(side="left", padx=5)
    bonif_comp_var = tk.StringVar(value="+2")
    ttk.Label(comp_bonus_frame, textvariable=bonif_comp_var, width=3).pack(side="left", padx=5)
    
    # Frame para CD de conjuro y ataque
    conjuro_frame = ttk.Frame(stats_frame)
    conjuro_frame.grid(row=len(ESTADISTICAS)+1, column=0, columnspan=4, sticky="w", padx=10, pady=10)
    
    ttk.Label(conjuro_frame, text="CD de Conjuro:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
    cd_conjuro_var = tk.StringVar(value="10")
    ttk.Label(conjuro_frame, textvariable=cd_conjuro_var, width=3).grid(row=0, column=1, sticky="w", padx=5, pady=2)
    
    ttk.Label(conjuro_frame, text="Bonificador de Conjuro:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
    ataque_conjuro_var = tk.StringVar(value="+0")
    ttk.Label(conjuro_frame, textvariable=ataque_conjuro_var, width=3).grid(row=1, column=1, sticky="w", padx=5, pady=2)
    
    # Nota sobre tiradas manuales
    ttk.Label(conjuro_frame, text="(Sumar al d20 para tiradas de ataque con conjuros)", 
             font=("Helvetica", 9, "italic")).grid(row=2, column=0, columnspan=2, sticky="w", padx=5, pady=2)
    
    def actualizar_ataques_conjuro(*args):
        """Actualiza los valores calculados para ataques de conjuro y CD"""
        try:
            # Determinar el atributo principal basado en la clase
            clase_actual = clase_var.get()
            atributo_principal = "Inteligencia"  # Por defecto para magos
            
            if clase_actual in ["Clérigo", "Druida", "Explorador"]:
                atributo_principal = "Sabiduría"
            elif clase_actual in ["Bardo", "Brujo", "Paladín", "Hechicero"]:
                atributo_principal = "Carisma"
            
            # Obtener modificador del atributo principal
            if atributo_principal in mod_vars:
                mod_texto = mod_vars[atributo_principal].get()
                mod = int(mod_texto) if mod_texto else 0
            else:
                mod = 0
            
            # Obtener bonificador de competencia
            comp_texto = bonif_comp_var.get()
            comp = int(comp_texto.replace("+", "")) if comp_texto else 2
            
            # Calcular CD de conjuro: 8 + mod + comp
            cd = 8 + mod + comp
            cd_conjuro_var.set(str(cd))
            
            # Calcular ataque de conjuro: mod + comp
            ataque = mod + comp
            ataque_conjuro_var.set(f"+{ataque}" if ataque >= 0 else str(ataque))
            
            # Mostrar u ocultar frame de conjuros según la clase
            if clase_actual in CLASES_MAGICAS:
                conjuro_frame.grid()
            else:
                conjuro_frame.grid_remove()
                
        except Exception as e:
            # En caso de error, usar valores por defecto
            cd_conjuro_var.set("10")
            ataque_conjuro_var.set("+0")
    
    # Vincular cambio de clase con actualización de valores de conjuro
    clase_var.trace_add("write", actualizar_ataques_conjuro)
    
    # Frame para competencias
    comp_frame = ttk.LabelFrame(tab_estadisticas, text="Competencias en Habilidades")
    comp_frame.pack(fill="x", padx=10, pady=10)
    
    # Variables para competencias
    comp_vars = {}
    comp_datos = personaje.get("competencias", []) if personaje else []
    
    # Crear checkboxes para competencias (en 3 columnas)
    for i, comp in enumerate(COMPETENCIAS):
        fila = i % 6
        columna = i // 6
        comp_vars[comp] = tk.BooleanVar(value=comp in comp_datos)
        ttk.Checkbutton(comp_frame, text=comp, variable=comp_vars[comp]).grid(
            row=fila, column=columna, sticky="w", padx=10, pady=5
        )
    
    # Frame para competencias con armas y armaduras
    comp_armas_frame = ttk.LabelFrame(tab_estadisticas, text="Competencias con Armas y Armaduras")
    comp_armas_frame.pack(fill="x", padx=10, pady=10)
    
    # Variables para competencias con armas y armaduras
    armadura_vars = {}
    armas_vars = {}
    
    comp_armadura_datos = personaje.get("comp_armaduras", []) if personaje else []
    comp_armas_datos = personaje.get("comp_armas", []) if personaje else []
    
    # Frame para armaduras
    armaduras_frame = ttk.Frame(comp_armas_frame)
    armaduras_frame.pack(fill="x", padx=10, pady=5)
    
    ttk.Label(armaduras_frame, text="Armaduras:", font=('Helvetica', 10, 'bold')).grid(row=0, column=0, sticky="w", padx=5, pady=5)
    
    # Tipos de armaduras
    armaduras = ["Ligeras", "Medias", "Pesadas", "Escudos"]
    
    for i, armadura in enumerate(armaduras):
        armadura_vars[armadura] = tk.BooleanVar(value=armadura in comp_armadura_datos)
        ttk.Checkbutton(armaduras_frame, text=armadura, variable=armadura_vars[armadura]).grid(
            row=0, column=i+1, sticky="w", padx=10, pady=5
        )
    
    # Frame para armas
    armas_frame = ttk.Frame(comp_armas_frame)
    armas_frame.pack(fill="x", padx=10, pady=5)
    
    ttk.Label(armas_frame, text="Armas:", font=('Helvetica', 10, 'bold')).grid(row=0, column=0, sticky="w", padx=5, pady=5)
    
    # Tipos de armas
    armas = ["Simples", "Marciales"]
    
    for i, arma in enumerate(armas):
        armas_vars[arma] = tk.BooleanVar(value=arma in comp_armas_datos)
        ttk.Checkbutton(armas_frame, text=arma, variable=armas_vars[arma]).grid(
            row=0, column=i+1, sticky="w", padx=10, pady=5
        )
    
    # Frame para armas específicas
    armas_esp_frame = ttk.Frame(comp_armas_frame)
    armas_esp_frame.pack(fill="x", padx=10, pady=5)
    
    ttk.Label(armas_esp_frame, text="Armas Específicas:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
    
    armas_especificas_var = tk.StringVar(value=personaje.get("armas_especificas", "") if personaje else "")
    ttk.Entry(armas_esp_frame, textvariable=armas_especificas_var, width=50).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
    ttk.Label(armas_esp_frame, text="(separadas por comas)").grid(row=0, column=2, sticky="w", padx=5, pady=5)
    
    # Frame para cálculo de ataques
    ataques_frame = ttk.LabelFrame(tab_estadisticas, text="Bonificadores para Tiradas")
    ataques_frame.pack(fill="x", padx=10, pady=10)
    
    ttk.Label(ataques_frame, text="Ataque con Fuerza:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
    ataque_fuerza_var = tk.StringVar(value="+0")
    ttk.Label(ataques_frame, textvariable=ataque_fuerza_var, width=5).grid(row=0, column=1, sticky="w", padx=5, pady=5)
    
    ttk.Label(ataques_frame, text="Ataque con Destreza:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
    ataque_destreza_var = tk.StringVar(value="+0")
    ttk.Label(ataques_frame, textvariable=ataque_destreza_var, width=5).grid(row=1, column=1, sticky="w", padx=5, pady=5)
    
    # Nota informativa sobre tiradas manuales
    ttk.Label(ataques_frame, text="(Estos valores se suman a la tirada manual de d20)", 
             font=("Helvetica", 9, "italic")).grid(row=2, column=0, columnspan=2, sticky="w", padx=10, pady=5)
    
    # Actualizar bonificadores de ataque cuando cambian estadísticas o competencias
    def actualizar_bonificadores_ataque(*args):
        try:
            # Obtener modificadores
            mod_fuerza = int(mod_vars["Fuerza"].get()) if mod_vars["Fuerza"].get() else 0
            mod_destreza = int(mod_vars["Destreza"].get()) if mod_vars["Destreza"].get() else 0
            
            # Obtener bonificador de competencia
            comp_texto = bonif_comp_var.get()
            comp = int(comp_texto.replace("+", "")) if comp_texto else 2
            
            # Verificar competencias con armas
            tiene_comp_simple = armas_vars["Simples"].get()
            tiene_comp_marcial = armas_vars["Marciales"].get()
            
            # Bonificador con competencia
            bonif_fuerza = mod_fuerza + (comp if tiene_comp_simple or tiene_comp_marcial else 0)
            bonif_destreza = mod_destreza + (comp if tiene_comp_simple or tiene_comp_marcial else 0)
            
            # Actualizar valores
            ataque_fuerza_var.set(f"+{bonif_fuerza}" if bonif_fuerza >= 0 else str(bonif_fuerza))
            ataque_destreza_var.set(f"+{bonif_destreza}" if bonif_destreza >= 0 else str(bonif_destreza))
            
        except Exception:
            ataque_fuerza_var.set("+0")
            ataque_destreza_var.set("+0")
    
    # Vincular eventos para actualizar bonificadores
    def actualizar_todo(*args):
        calcular_modificador()
        actualizar_ataques_conjuro()
        actualizar_bonificadores_ataque()
    
    # Vincular eventos para estadísticas
    for stat, var in stats_vars.items():
        var.trace_add("write", actualizar_todo)
    
    # Vincular eventos para competencias con armas
    for arma, var in armas_vars.items():
        var.trace_add("write", actualizar_bonificadores_ataque)
    
    # Inicializar modificadores y cálculos
    actualizar_todo()
    
    # Inicializar información de nivel/experiencia
    calcular_experiencia_desde_nivel()
    
    # ===== INVENTARIO Y EQUIPAMIENTO =====
    tab_inventario = ttk.Frame(notebook)
    notebook.add(tab_inventario, text="Inventario y Equipamiento")
    
    # Frame para inventario
    inv_frame = ttk.LabelFrame(tab_inventario, text="Inventario Personal")
    inv_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    ttk.Label(inv_frame, text="No implementado", font=("Helvetica", 12, "italic")).pack(pady=20)
    
    # Botones de inventario (deshabilitados)
    inv_botones = ttk.Frame(inv_frame)
    inv_botones.pack(pady=10)
    
    ttk.Button(inv_botones, text="Agregar objeto", command=lambda: messagebox.showinfo("Información", "No implementado")).pack(side="left", padx=5)
    ttk.Button(inv_botones, text="Editar objeto", command=lambda: messagebox.showinfo("Información", "No implementado")).pack(side="left", padx=5)
    ttk.Button(inv_botones, text="Eliminar objeto", command=lambda: messagebox.showinfo("Información", "No implementado")).pack(side="left", padx=5)
    
    # Frame para equipamiento
    equip_frame = ttk.LabelFrame(tab_inventario, text="Gestor de Armadura y Accesorios")
    equip_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    ttk.Label(equip_frame, text="No implementado", font=("Helvetica", 12, "italic")).pack(pady=20)
    
    # Slots de equipamiento (slots básicos)
    equip_slots = ttk.Frame(equip_frame)
    equip_slots.pack(pady=10)
    
    slots = ["Armadura", "Escudo", "Anillo 1", "Anillo 2", "Amuleto"]
    for slot in slots:
        slot_frame = ttk.Frame(equip_slots)
        slot_frame.pack(side="left", padx=10, pady=5)
        
        ttk.Label(slot_frame, text=slot).pack()
        ttk.Button(slot_frame, text="Equipar", command=lambda: messagebox.showinfo("Información", "No implementado")).pack(fill="x", pady=2)
        ttk.Button(slot_frame, text="Desequipar", command=lambda: messagebox.showinfo("Información", "No implementado")).pack(fill="x", pady=2)
    
    # Frame para hechizos
    hechizos_frame = ttk.LabelFrame(tab_inventario, text="Hechizos")
    hechizos_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Contenido del frame de hechizos
    hechizos_content = ttk.Frame(hechizos_frame)
    hechizos_content.pack(fill="both", expand=True)
    
    # Tabla de hechizos
    hechizos_table_frame = ttk.Frame(hechizos_content)
    hechizos_table_frame.pack(fill="both", expand=True, padx=5, pady=5)
    
    # Cabecera de tabla
    ttk.Label(hechizos_table_frame, text="Nombre", width=25, font=("Helvetica", 10, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")
    ttk.Label(hechizos_table_frame, text="Daño", width=10, font=("Helvetica", 10, "bold")).grid(row=0, column=1, padx=5, pady=5, sticky="w")
    ttk.Label(hechizos_table_frame, text="Nivel", width=5, font=("Helvetica", 10, "bold")).grid(row=0, column=2, padx=5, pady=5, sticky="w")
    
    # Cargar hechizos si existen
    hechizos = personaje.get("hechizos", []) if personaje else []
    
    # Mostrar hechizos o mensaje de clase no mágica
    if clase_var.get() not in CLASES_MAGICAS:
        mensaje = "Esta clase no tiene acceso a hechizos"
        ttk.Label(hechizos_table_frame, text=mensaje, font=("Helvetica", 10, "italic")).grid(row=1, column=0, columnspan=3, padx=5, pady=10)
    elif not hechizos:
        ttk.Label(hechizos_table_frame, text="No hay hechizos añadidos").grid(row=1, column=0, columnspan=3, padx=5, pady=10)
    else:
        for i, hechizo in enumerate(hechizos):
            ttk.Label(hechizos_table_frame, text=hechizo.get("nombre", "")).grid(row=i+1, column=0, padx=5, pady=3, sticky="w")
            ttk.Label(hechizos_table_frame, text=hechizo.get("daño", "")).grid(row=i+1, column=1, padx=5, pady=3, sticky="w")
            ttk.Label(hechizos_table_frame, text=str(hechizo.get("nivel", ""))).grid(row=i+1, column=2, padx=5, pady=3, sticky="w")
    
    # Botón para añadir hechizo
    ttk.Button(hechizos_content, text="Agregar Hechizo", 
              command=lambda: messagebox.showinfo("Información", "No implementado")).pack(pady=10)
    
    # Vincular cambio de clase para actualizar mensaje
    def actualizar_mensaje_hechizos(*args):
        # Limpiar tabla
        for widget in hechizos_table_frame.winfo_children():
            if int(widget.grid_info().get("row", 0)) > 0:  # Mantener cabecera
                widget.destroy()
        
        # Mostrar mensaje según clase
        if clase_var.get() not in CLASES_MAGICAS:
            mensaje = "Esta clase no tiene acceso a hechizos"
            ttk.Label(hechizos_table_frame, text=mensaje, font=("Helvetica", 10, "italic")).grid(row=1, column=0, columnspan=3, padx=5, pady=10)
        elif not hechizos:
            ttk.Label(hechizos_table_frame, text="No hay hechizos añadidos").grid(row=1, column=0, columnspan=3, padx=5, pady=10)
        else:
            for i, hechizo in enumerate(hechizos):
                ttk.Label(hechizos_table_frame, text=hechizo.get("nombre", "")).grid(row=i+1, column=0, padx=5, pady=3, sticky="w")
                ttk.Label(hechizos_table_frame, text=hechizo.get("daño", "")).grid(row=i+1, column=1, padx=5, pady=3, sticky="w")
                ttk.Label(hechizos_table_frame, text=str(hechizo.get("nivel", ""))).grid(row=i+1, column=2, padx=5, pady=3, sticky="w")
    
    # Vincular actualización de mensaje al cambio de clase
    clase_var.trace_add("write", actualizar_mensaje_hechizos)
    
    # ===== HECHIZOS =====
    # Esta pestaña solo aparece para clases mágicas
    tab_hechizos = ttk.Frame(notebook)
    
    def actualizar_tabs_hechizos(*args):
        # Muestra u oculta la pestaña de hechizos basado en la clase
        if clase_var.get() in CLASES_MAGICAS:
            # Verificar si la pestaña ya existe
            tabs = notebook.tabs()
            if tab_hechizos not in tabs:
                notebook.add(tab_hechizos, text="Hechizos")
        else:
            # Verificar si la pestaña existe y quitarla
            tabs = notebook.tabs()
            if tab_hechizos in tabs:
                notebook.forget(tab_hechizos)
    
    # Vincular cambio de clase con actualización de pestañas
    clase_var.trace_add("write", actualizar_tabs_hechizos)
    
    # Configurar pestaña de hechizos
    hechizos_frame = ttk.Frame(tab_hechizos)
    hechizos_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Tabla de hechizos
    ttk.Label(hechizos_frame, text="Hechizos Conocidos", font=("Helvetica", 12, "bold")).pack(pady=(0, 10))
    
    hechizos_table_frame = ttk.Frame(hechizos_frame)
    hechizos_table_frame.pack(fill="both", expand=True)
    
    # Cabecera de tabla
    ttk.Label(hechizos_table_frame, text="Nombre", width=25, font=("Helvetica", 10, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")
    ttk.Label(hechizos_table_frame, text="Daño", width=10, font=("Helvetica", 10, "bold")).grid(row=0, column=1, padx=5, pady=5, sticky="w")
    ttk.Label(hechizos_table_frame, text="Nivel", width=5, font=("Helvetica", 10, "bold")).grid(row=0, column=2, padx=5, pady=5, sticky="w")
    ttk.Label(hechizos_table_frame, text="Acciones", width=10, font=("Helvetica", 10, "bold")).grid(row=0, column=3, padx=5, pady=5, sticky="w")
    
    # Lista para almacenar hechizos
    hechizos = personaje.get("hechizos", []) if personaje else []
    
    def actualizar_tabla_hechizos():
        """Actualiza la tabla de hechizos"""
        # Limpiar tabla
        for widget in hechizos_table_frame.winfo_children():
            if int(widget.grid_info().get("row", 0)) > 0:  # Mantener cabecera
                widget.destroy()
        
        if not hechizos:
            ttk.Label(hechizos_table_frame, text="No hay hechizos añadidos").grid(row=1, column=0, columnspan=4, padx=5, pady=10)
        else:
            for i, hechizo in enumerate(hechizos):
                ttk.Label(hechizos_table_frame, text=hechizo.get("nombre", "")).grid(row=i+1, column=0, padx=5, pady=3, sticky="w")
                ttk.Label(hechizos_table_frame, text=hechizo.get("daño", "")).grid(row=i+1, column=1, padx=5, pady=3, sticky="w")
                ttk.Label(hechizos_table_frame, text=str(hechizo.get("nivel", ""))).grid(row=i+1, column=2, padx=5, pady=3, sticky="w")
                
                # Botones de acción
                accion_frame = ttk.Frame(hechizos_table_frame)
                accion_frame.grid(row=i+1, column=3, padx=5, pady=3, sticky="w")
                
                ttk.Button(accion_frame, text="Eliminar", 
                          command=lambda idx=i: eliminar_hechizo(idx)).pack(side="left", padx=2)
    
    def eliminar_hechizo(indice):
        """Elimina un hechizo de la lista"""
        if 0 <= indice < len(hechizos):
            del hechizos[indice]
            actualizar_tabla_hechizos()
    
    def mostrar_form_hechizo():
        """Muestra el formulario para añadir un hechizo"""
        dialogo = tk.Toplevel(root)
        dialogo.title("Añadir Hechizo")
        dialogo.geometry("400x350")
        dialogo.resizable(False, False)
        dialogo.transient(root)
        dialogo.grab_set()
        
        # Centrar la ventana
        dialogo.geometry("+%d+%d" % (
            root.winfo_rootx() + (root.winfo_width() // 2) - 200,
            root.winfo_rooty() + (root.winfo_height() // 2) - 175
        ))
        
        # Contenido del diálogo
        ttk.Label(dialogo, text="Añadir Nuevo Hechizo", style="Header.TLabel").pack(pady=(20, 10))
        
        # Frame para los campos
        form_frame = ttk.Frame(dialogo)
        form_frame.pack(fill="x", padx=20, pady=10)
        
        # Nombre del hechizo
        ttk.Label(form_frame, text="Nombre:").grid(row=0, column=0, sticky="w", pady=5)
        nombre_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=nombre_var, width=30).grid(row=0, column=1, sticky="ew", pady=5)
        
        # Nivel
        ttk.Label(form_frame, text="Nivel:").grid(row=1, column=0, sticky="w", pady=5)
        nivel_var = tk.StringVar(value="0")
        nivel_combo = ttk.Combobox(form_frame, textvariable=nivel_var, values=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"], width=5)
        nivel_combo.grid(row=1, column=1, sticky="w", pady=5)
        nivel_combo.current(0)
        
        # Daño
        ttk.Label(form_frame, text="Daño:").grid(row=2, column=0, sticky="w", pady=5)
        dano_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=dano_var, width=15).grid(row=2, column=1, sticky="w", pady=5)
        ttk.Label(form_frame, text="(ej: 2d6, 1d8+3)").grid(row=2, column=2, sticky="w", pady=5)
        
        # Escuela
        ttk.Label(form_frame, text="Escuela:").grid(row=3, column=0, sticky="w", pady=5)
        escuela_var = tk.StringVar()
        escuelas = ["Abjuración", "Adivinación", "Conjuración", "Encantamiento", 
                    "Evocación", "Ilusión", "Nigromancia", "Transmutación"]
        ttk.Combobox(form_frame, textvariable=escuela_var, values=escuelas, width=28).grid(row=3, column=1, sticky="ew", pady=5)
        
        # Tiempo de lanzamiento
        ttk.Label(form_frame, text="Tiempo:").grid(row=4, column=0, sticky="w", pady=5)
        tiempo_var = tk.StringVar(value="1 acción")
        ttk.Entry(form_frame, textvariable=tiempo_var, width=20).grid(row=4, column=1, sticky="w", pady=5)
        
        # Alcance
        ttk.Label(form_frame, text="Alcance:").grid(row=5, column=0, sticky="w", pady=5)
        alcance_var = tk.StringVar(value="30 pies")
        ttk.Entry(form_frame, textvariable=alcance_var, width=20).grid(row=5, column=1, sticky="w", pady=5)
        
        # Descripción
        ttk.Label(form_frame, text="Descripción:").grid(row=6, column=0, sticky="nw", pady=5)
        descripcion_text = tk.Text(form_frame, height=4, width=30)
        descripcion_text.grid(row=6, column=1, columnspan=2, sticky="ew", pady=5)
        
        # Botones
        botones_frame = ttk.Frame(dialogo)
        botones_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        def validar_y_agregar():
            # Validar campos obligatorios
            if not nombre_var.get().strip():
                messagebox.showwarning("Advertencia", "Debe ingresar un nombre para el hechizo.")
                return
            
            try:
                nivel = int(nivel_var.get())
                if nivel < 0 or nivel > 9:
                    messagebox.showwarning("Advertencia", "El nivel del hechizo debe estar entre 0 y 9.")
                    return
            except ValueError:
                messagebox.showwarning("Advertencia", "El nivel debe ser un número.")
                return
            
            # Crear hechizo
            hechizo = {
                "nombre": nombre_var.get().strip(),
                "nivel": nivel,
                "daño": dano_var.get().strip(),
                "escuela": escuela_var.get(),
                "tiempo": tiempo_var.get().strip(),
                "alcance": alcance_var.get().strip(),
                "descripcion": descripcion_text.get("1.0", "end-1c")
            }
            
            # Añadir a la lista
            hechizos.append(hechizo)
            
            # Actualizar tabla
            actualizar_tabla_hechizos()
            
            # Cerrar diálogo
            dialogo.destroy()
        
        ttk.Button(botones_frame, text="Añadir", command=validar_y_agregar).pack(side="right", padx=5)
        ttk.Button(botones_frame, text="Cancelar", command=dialogo.destroy).pack(side="right", padx=5)
    
    # Inicializar tabla de hechizos
    actualizar_tabla_hechizos()
    
    # Botón para añadir hechizo
    ttk.Button(hechizos_frame, text="Añadir Hechizo", 
              command=mostrar_form_hechizo).pack(pady=10)
    
    # Actualizar pestañas según la clase inicial
    actualizar_tabs_hechizos()
    
    # ===== PESTAÑA DE PROGRESIÓN =====
    tab_progresion = ttk.Frame(notebook)
    notebook.add(tab_progresion, text="Progresión")
    
    # Título
    ttk.Label(tab_progresion, text="Gestión de Experiencia y Nivel", font=('Helvetica', 14, 'bold')).pack(pady=(20, 10))
    
    # Frame para información de nivel actual
    nivel_info_frame = ttk.LabelFrame(tab_progresion, text="Nivel Actual")
    nivel_info_frame.pack(fill="x", padx=20, pady=10)
    
    # Grid para organizar información
    for i in range(2):
        nivel_info_frame.columnconfigure(i, weight=1)
    
    ttk.Label(nivel_info_frame, text="Nivel:", font=('Helvetica', 12, 'bold')).grid(row=0, column=0, padx=10, pady=5, sticky="w")
    nivel_actual_var = tk.StringVar()
    nivel_actual_label = ttk.Label(nivel_info_frame, textvariable=nivel_actual_var, font=('Helvetica', 12))
    nivel_actual_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")
    
    ttk.Label(nivel_info_frame, text="Experiencia:", font=('Helvetica', 12, 'bold')).grid(row=1, column=0, padx=10, pady=5, sticky="w")
    exp_actual_var = tk.StringVar()
    exp_actual_label = ttk.Label(nivel_info_frame, textvariable=exp_actual_var, font=('Helvetica', 12))
    exp_actual_label.grid(row=1, column=1, padx=10, pady=5, sticky="w")
    
    ttk.Label(nivel_info_frame, text="Experiencia para el siguiente nivel:", font=('Helvetica', 12, 'bold')).grid(row=2, column=0, padx=10, pady=5, sticky="w")
    exp_siguiente_nivel_var = tk.StringVar()
    exp_siguiente_label = ttk.Label(nivel_info_frame, textvariable=exp_siguiente_nivel_var, font=('Helvetica', 12))
    exp_siguiente_label.grid(row=2, column=1, padx=10, pady=5, sticky="w")
    
    ttk.Label(nivel_info_frame, text="Experiencia restante:", font=('Helvetica', 12, 'bold')).grid(row=3, column=0, padx=10, pady=5, sticky="w")
    exp_restante_var = tk.StringVar()
    exp_restante_label = ttk.Label(nivel_info_frame, textvariable=exp_restante_var, font=('Helvetica', 12))
    exp_restante_label.grid(row=3, column=1, padx=10, pady=5, sticky="w")
    
    # Frame para añadir experiencia
    add_exp_frame = ttk.LabelFrame(tab_progresion, text="Añadir Experiencia")
    add_exp_frame.pack(fill="x", padx=20, pady=10)
    
    # Grid para organizar inputs
    add_exp_frame.columnconfigure(1, weight=1)
    
    ttk.Label(add_exp_frame, text="Cantidad de Experiencia:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
    add_exp_var = tk.StringVar(value="0")
    ttk.Entry(add_exp_frame, textvariable=add_exp_var, width=10).grid(row=0, column=1, padx=10, pady=10, sticky="w")
    
    # Botones para añadir experiencia predefinida
    exp_buttons_frame = ttk.Frame(add_exp_frame)
    exp_buttons_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="w")
    
    # Botones con cantidades comunes de experiencia
    exp_values = [100, 250, 500, 1000, 2000, 5000]
    for i, value in enumerate(exp_values):
        ttk.Button(exp_buttons_frame, text=f"+{value} XP", 
                  command=lambda v=value: add_exp_var.set(str(v))).pack(side="left", padx=5)
    
    # Botón para añadir experiencia
    def add_experience():
        try:
            # Obtener experiencia actual
            current_exp = int(experiencia_var.get())
            # Obtener cantidad a añadir
            add_amount = int(add_exp_var.get())
            
            if add_amount < 0:
                messagebox.showwarning("Advertencia", "La cantidad de experiencia a añadir debe ser positiva.")
                return
            
            # Calcular nueva experiencia
            new_exp = current_exp + add_amount
            
            # Actualizar campo
            experiencia_var.set(str(new_exp))
            
            # Actualizar nivel basado en la nueva experiencia
            calcular_nivel_desde_experiencia()
            
            # Mostrar mensaje
            messagebox.showinfo("Éxito", f"Se han añadido {add_amount} puntos de experiencia.\nExperiencia total: {new_exp}\nNivel actual: {nivel_var.get()}")
            
            # Actualizar displays
            actualizar_displays_progresion()
            
        except ValueError:
            messagebox.showwarning("Advertencia", "Debe ingresar un número válido.")
    
    ttk.Button(add_exp_frame, text="Añadir Experiencia", 
              command=add_experience).grid(row=2, column=0, columnspan=2, padx=10, pady=10)
    
    # Frame para cambio directo de nivel
    nivel_frame = ttk.LabelFrame(tab_progresion, text="Cambiar Nivel Directamente")
    nivel_frame.pack(fill="x", padx=20, pady=10)
    
    # Grid para organizar inputs
    nivel_frame.columnconfigure(1, weight=1)
    
    ttk.Label(nivel_frame, text="Nuevo Nivel:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
    nuevo_nivel_var = tk.StringVar(value="1")
    nivel_spinner = ttk.Spinbox(nivel_frame, from_=1, to=20, textvariable=nuevo_nivel_var, width=5)
    nivel_spinner.grid(row=0, column=1, padx=10, pady=10, sticky="w")
    
    # Botón para cambiar nivel
    def change_level():
        try:
            # Obtener nuevo nivel
            new_level = int(nuevo_nivel_var.get())
            
            if new_level < 1 or new_level > 20:
                messagebox.showwarning("Advertencia", "El nivel debe estar entre 1 y 20.")
                return
            
            # Actualizar nivel
            nivel_var.set(str(new_level))
            
            # Actualizar experiencia basada en el nuevo nivel
            calcular_experiencia_desde_nivel()
            
            # Mostrar mensaje
            messagebox.showinfo("Éxito", f"Nivel actualizado a {new_level}.\nExperiencia ajustada a {experiencia_var.get()} puntos.")
            
            # Actualizar displays
            actualizar_displays_progresion()
            
        except ValueError:
            messagebox.showwarning("Advertencia", "Debe ingresar un número válido.")
    
    ttk.Button(nivel_frame, text="Cambiar Nivel", 
              command=change_level).grid(row=1, column=0, columnspan=2, padx=10, pady=10)
    
    # Tabla de experiencia
    exp_table_frame = ttk.LabelFrame(tab_progresion, text="Tabla de Experiencia (D&D 5e)")
    exp_table_frame.pack(fill="x", padx=20, pady=10)
    
    # Grid para la tabla
    exp_table = ttk.Frame(exp_table_frame)
    exp_table.pack(fill="both", padx=10, pady=10)
    
    # Encabezados de la tabla
    ttk.Label(exp_table, text="Nivel", font=('Helvetica', 10, 'bold')).grid(row=0, column=0, padx=5, pady=2, sticky="w")
    ttk.Label(exp_table, text="Experiencia", font=('Helvetica', 10, 'bold')).grid(row=0, column=1, padx=5, pady=2, sticky="w")
    ttk.Label(exp_table, text="Bonif. Comp.", font=('Helvetica', 10, 'bold')).grid(row=0, column=2, padx=5, pady=2, sticky="w")
    ttk.Label(exp_table, text="Nivel", font=('Helvetica', 10, 'bold')).grid(row=0, column=3, padx=5, pady=2, sticky="w")
    ttk.Label(exp_table, text="Experiencia", font=('Helvetica', 10, 'bold')).grid(row=0, column=4, padx=5, pady=2, sticky="w")
    ttk.Label(exp_table, text="Bonif. Comp.", font=('Helvetica', 10, 'bold')).grid(row=0, column=5, padx=5, pady=2, sticky="w")
    
    # Rellenar tabla
    for lvl in range(1, 11):
        # Bonificador de competencia
        comp = 2 + ((lvl - 1) // 4)
        
        # Primera columna (niveles 1-10)
        ttk.Label(exp_table, text=str(lvl)).grid(row=lvl, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(exp_table, text=str(TABLA_EXPERIENCIA[lvl])).grid(row=lvl, column=1, padx=5, pady=2, sticky="w")
        ttk.Label(exp_table, text=f"+{comp}").grid(row=lvl, column=2, padx=5, pady=2, sticky="w")
        
        # Segunda columna (niveles 11-20)
        lvl2 = lvl + 10
        comp2 = 2 + ((lvl2 - 1) // 4)
        
        ttk.Label(exp_table, text=str(lvl2)).grid(row=lvl, column=3, padx=5, pady=2, sticky="w")
        ttk.Label(exp_table, text=str(TABLA_EXPERIENCIA[lvl2])).grid(row=lvl, column=4, padx=5, pady=2, sticky="w")
        ttk.Label(exp_table, text=f"+{comp2}").grid(row=lvl, column=5, padx=5, pady=2, sticky="w")
    
    # Función para actualizar displays de progresión
    def actualizar_displays_progresion():
        try:
            nivel_actual_var.set(nivel_var.get())
            exp_actual_var.set(experiencia_var.get())
            
            nivel = int(nivel_var.get())
            if nivel < 20:
                exp_siguiente_nivel_var.set(str(TABLA_EXPERIENCIA[nivel + 1]))
                exp_restante_var.set(str(TABLA_EXPERIENCIA[nivel + 1] - int(experiencia_var.get())))
            else:
                exp_siguiente_nivel_var.set("Máximo")
                exp_restante_var.set("Máximo")
        except (ValueError, KeyError):
            nivel_actual_var.set("1")
            exp_actual_var.set("0")
            exp_siguiente_nivel_var.set("300")
            exp_restante_var.set("300")
    
    # Inicializar displays
    actualizar_displays_progresion()
    
    # Vincular cambios de nivel/experiencia con actualización de displays
    nivel_var.trace_add("write", lambda *args: actualizar_displays_progresion())
    experiencia_var.trace_add("write", lambda *args: actualizar_displays_progresion())
    
    # Botones de acción
    botones_frame = ttk.Frame(editar_frame)
    botones_frame.pack(fill="x", padx=20, pady=(20, 30))
    
    def volver():
        """Vuelve a la pantalla del gestor de personajes"""
        # Desenlazar eventos de scroll
        canvas.unbind_all("<MouseWheel>")
        # Destruir el contenedor principal
        main_container.destroy()
        # Volver a la pantalla anterior
        callback_volver()
    
    def guardar():
        """Guarda los datos del personaje"""
        # Validar campos obligatorios
        if not nombre_var.get().strip():
            messagebox.showwarning("Advertencia", "Debe ingresar un nombre para el personaje.")
            notebook.select(0)  # Seleccionar pestaña de datos básicos
            return
        
        if not clase_var.get():
            messagebox.showwarning("Advertencia", "Debe seleccionar una clase.")
            notebook.select(0)
            return
        
        if not raza_var.get():
            messagebox.showwarning("Advertencia", "Debe seleccionar una raza.")
            notebook.select(0)
            return
        
        # Validar estadísticas
        for stat in ESTADISTICAS:
            try:
                valor = int(stats_vars[stat].get())
                if valor < 1 or valor > 30:
                    messagebox.showwarning("Advertencia", f"El valor de {stat} debe estar entre 1 y 30.")
                    notebook.select(1)  # Seleccionar pestaña de estadísticas
                    return
            except ValueError:
                messagebox.showwarning("Advertencia", f"El valor de {stat} debe ser un número.")
                notebook.select(1)
                return
        
        # Validar nivel y experiencia
        try:
            nivel = int(nivel_var.get())
            experiencia = int(experiencia_var.get())
            
            if nivel < 1 or nivel > 20:
                messagebox.showwarning("Advertencia", "El nivel debe estar entre 1 y 20.")
                notebook.select(0)
                return
            
            if experiencia < 0:
                messagebox.showwarning("Advertencia", "La experiencia no puede ser negativa.")
                notebook.select(0)
                return
            
            # Verificar coherencia entre nivel y experiencia
            if experiencia < TABLA_EXPERIENCIA[nivel]:
                respuesta = messagebox.askyesno("Advertencia", 
                    f"La experiencia actual ({experiencia}) es menor que la mínima requerida para el nivel {nivel} ({TABLA_EXPERIENCIA[nivel]}).\n"
                    f"¿Desea ajustar la experiencia al mínimo requerido para el nivel {nivel}?")
                if respuesta:
                    experiencia = TABLA_EXPERIENCIA[nivel]
                    experiencia_var.set(str(experiencia))
        except ValueError:
            messagebox.showwarning("Advertencia", "El nivel y la experiencia deben ser números.")
            notebook.select(0)
            return
        
        # Recopilar datos de competencias con armas y armaduras
        comp_armaduras = [armadura for armadura, var in armadura_vars.items() if var.get()]
        comp_armas = [arma for arma, var in armas_vars.items() if var.get()]
        armas_especificas = [arma.strip() for arma in armas_especificas_var.get().split(",") if arma.strip()]
        
        # Recopilar datos
        datos_personaje = {
            "nombre": nombre_var.get().strip(),
            "clase": clase_var.get(),
            "raza": raza_var.get(),
            "nivel": nivel,
            "experiencia": experiencia,
            "estadisticas": {stat: int(stats_vars[stat].get()) for stat in ESTADISTICAS},
            "competencias": [comp for comp, var in comp_vars.items() if var.get()],
            "comp_armaduras": comp_armaduras,
            "comp_armas": comp_armas,
            "armas_especificas": armas_especificas_var.get(),
            "inventario": [],  # Vacío por ahora
            "equipamiento": {},  # Vacío por ahora
            "hechizos": hechizos  # Mantener hechizos existentes
        }
        
        # Valores calculados
        datos_personaje["bonif_comp"] = bonif_comp_var.get()
        datos_personaje["cd_conjuro"] = cd_conjuro_var.get()
        datos_personaje["ataque_conjuro"] = ataque_conjuro_var.get()
        datos_personaje["ataque_fuerza"] = ataque_fuerza_var.get()
        datos_personaje["ataque_destreza"] = ataque_destreza_var.get()
        
        # Nombre del archivo
        nombre_archivo = nombre_var.get().strip().replace(" ", "_").lower() + ".json"
        datos_personaje["archivo"] = nombre_archivo
        ruta_archivo = os.path.join(directorio_personajes, nombre_archivo)
        
        # Guardar en archivo
        try:
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                json.dump(datos_personaje, f, ensure_ascii=False, indent=4)
            
            messagebox.showinfo("Éxito", f"Personaje '{nombre_var.get()}' guardado correctamente.")
            volver()  # Volver a la pantalla del gestor
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar el personaje: {str(e)}")
    
    ttk.Button(botones_frame, text="Guardar", command=guardar).pack(side="right", padx=5)
    ttk.Button(botones_frame, text="Cancelar", command=volver).pack(side="right", padx=5)
    
    # Añadir atajos de teclado para navegación con scroll
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    # Actualizar canvas después de que todo esté configurado
    canvas.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))