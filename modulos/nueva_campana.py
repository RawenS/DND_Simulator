#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo para crear una nueva campaña en la aplicación D&D Combat Manager.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

def mostrar_nueva_campana(root, directorio_campanas, callback_menu):
    """
    Muestra la pantalla para crear una nueva campaña
    
    Args:
        root: La ventana principal de la aplicación
        directorio_campanas: Directorio donde se guardarán las campañas
        callback_menu: Función para volver al menú principal
    """
    # Ocultar frames existentes
    for widget in root.winfo_children():
        if isinstance(widget, ttk.Frame):
            widget.pack_forget()
    
    # Crear nuevo frame para la campaña
    nueva_campana_frame = ttk.Frame(root)
    
    # Lista de jugadores
    jugadores = []
    
    # Título y descripción
    titulo = ttk.Label(nueva_campana_frame, text="Crear Nueva Campaña", style="Title.TLabel")
    titulo.pack(pady=(20, 10))
    
    descripcion = ttk.Label(
        nueva_campana_frame, 
        text="Configure los parámetros iniciales de su nueva campaña.",
        wraplength=600
    )
    descripcion.pack(pady=(0, 20))
    
    # Frame para los parámetros básicos
    params_frame = ttk.Frame(nueva_campana_frame)
    params_frame.pack(fill="x", padx=50, pady=10)
    
    # Nombre de la campaña
    ttk.Label(params_frame, text="Nombre de la Campaña:").grid(row=0, column=0, sticky="w", pady=5)
    nombre_campana = tk.StringVar()
    ttk.Entry(params_frame, textvariable=nombre_campana, width=40).grid(row=0, column=1, sticky="ew", pady=5)
    
    # Ambientación
    ttk.Label(params_frame, text="Ambientación:").grid(row=1, column=0, sticky="w", pady=5)
    ambientacion = tk.StringVar()
    ambientaciones = ["Fantasía", "Terror", "Steampunk", "Sci-Fi", "Post-apocalíptico", "Otro"]
    ttk.Combobox(params_frame, textvariable=ambientacion, values=ambientaciones, width=38).grid(row=1, column=1, sticky="ew", pady=5)
    
    # Reglas especiales
    ttk.Label(params_frame, text="Reglas Especiales:").grid(row=2, column=0, sticky="nw", pady=5)
    reglas_frame = ttk.Frame(params_frame)
    reglas_frame.grid(row=2, column=1, sticky="ew", pady=5)
    
    reglas_text = tk.Text(reglas_frame, height=5, width=38)
    reglas_text.pack(side="left", fill="both", expand=True)
    
    # Scrollbar para reglas
    scrollbar = ttk.Scrollbar(reglas_frame, command=reglas_text.yview)
    scrollbar.pack(side="right", fill="y")
    reglas_text.config(yscrollcommand=scrollbar.set)
    
    # Opciones de reglas
    opciones_frame = ttk.Frame(params_frame)
    opciones_frame.grid(row=3, column=0, columnspan=2, sticky="w", pady=10)
    
    sin_muerte = tk.BooleanVar()
    ttk.Checkbutton(opciones_frame, text="Sin muerte súbita", variable=sin_muerte).pack(side="left", padx=5)
    
    exp_modificada = tk.BooleanVar()
    ttk.Checkbutton(opciones_frame, text="Experiencia modificada", variable=exp_modificada).pack(side="left", padx=5)
    
    # Dificultad
    ttk.Label(opciones_frame, text="Dificultad:").pack(side="left", padx=(20, 5))
    dificultad = tk.StringVar(value="Normal")
    dificultades = ["Fácil", "Normal", "Difícil", "Mortal"]
    ttk.Combobox(opciones_frame, textvariable=dificultad, values=dificultades, width=10).pack(side="left", padx=5)
    
    # Sección de jugadores
    jugadores_titulo = ttk.Label(nueva_campana_frame, text="Jugadores", style="Subtitle.TLabel")
    jugadores_titulo.pack(pady=(20, 10))
    
    # Frame para lista de jugadores
    jugadores_list_frame = ttk.Frame(nueva_campana_frame)
    jugadores_list_frame.pack(fill="both", expand=True, padx=50, pady=5)
    
    def actualizar_lista_jugadores():
        """Actualiza la lista de jugadores en la pantalla"""
        # Limpiar frame
        for widget in jugadores_list_frame.winfo_children():
            widget.destroy()
        
        # Si no hay jugadores
        if not jugadores:
            ttk.Label(jugadores_list_frame, text="No hay jugadores añadidos").pack(pady=10)
            return
        
        # Crear tabla
        cols = ["Nombre", "Clase", "Raza", "Nivel", "Acciones"]
        for i, col in enumerate(cols):
            ttk.Label(jugadores_list_frame, text=col, font=('Helvetica', 11, 'bold')).grid(row=0, column=i, padx=5, pady=5, sticky="w")
        
        # Añadir jugadores
        for i, jugador in enumerate(jugadores):
            ttk.Label(jugadores_list_frame, text=jugador["nombre"]).grid(row=i+1, column=0, padx=5, pady=3, sticky="w")
            ttk.Label(jugadores_list_frame, text=jugador["clase"]).grid(row=i+1, column=1, padx=5, pady=3, sticky="w")
            ttk.Label(jugadores_list_frame, text=jugador["raza"]).grid(row=i+1, column=2, padx=5, pady=3, sticky="w")
            ttk.Label(jugadores_list_frame, text=str(jugador["nivel"])).grid(row=i+1, column=3, padx=5, pady=3, sticky="w")
            
            # Botones de acción
            acciones_frame = ttk.Frame(jugadores_list_frame)
            acciones_frame.grid(row=i+1, column=4, padx=5, pady=3, sticky="w")
            
            # Índice actual para la lambda
            idx = i
            ttk.Button(acciones_frame, text="Eliminar", 
                      command=lambda idx=idx: eliminar_jugador(idx)).pack(side="left", padx=2)
    
    def eliminar_jugador(indice):
        """Elimina un jugador de la lista"""
        if 0 <= indice < len(jugadores):
            del jugadores[indice]
            actualizar_lista_jugadores()
    
    def mostrar_agregar_jugador():
        """Muestra un diálogo para agregar un jugador"""
        dialogo = tk.Toplevel(root)
        dialogo.title("Agregar Jugador")
        dialogo.geometry("400x300")
        dialogo.resizable(False, False)
        dialogo.transient(root)
        dialogo.grab_set()
        
        # Centrar la ventana
        dialogo.geometry("+%d+%d" % (
            root.winfo_rootx() + (root.winfo_width() // 2) - 200,
            root.winfo_rooty() + (root.winfo_height() // 2) - 150
        ))
        
        # Título
        ttk.Label(dialogo, text="Información del Jugador", style="Header.TLabel").pack(pady=(20, 10))
        
        # Frame para los campos
        campos_frame = ttk.Frame(dialogo)
        campos_frame.pack(fill="x", padx=20, pady=10)
        
        # Nombre del jugador
        ttk.Label(campos_frame, text="Nombre:").grid(row=0, column=0, sticky="w", pady=5)
        nombre_var = tk.StringVar()
        ttk.Entry(campos_frame, textvariable=nombre_var, width=30).grid(row=0, column=1, sticky="ew", pady=5)
        
        # Clase
        ttk.Label(campos_frame, text="Clase:").grid(row=1, column=0, sticky="w", pady=5)
        clase_var = tk.StringVar()
        clases = ["Bárbaro", "Bardo", "Clérigo", "Druida", "Guerrero", "Mago", "Monje", 
                 "Paladín", "Explorador", "Pícaro", "Hechicero", "Brujo"]
        ttk.Combobox(campos_frame, textvariable=clase_var, values=clases, width=28).grid(row=1, column=1, sticky="ew", pady=5)
        
        # Raza
        ttk.Label(campos_frame, text="Raza:").grid(row=2, column=0, sticky="w", pady=5)
        raza_var = tk.StringVar()
        razas = ["Humano", "Elfo", "Enano", "Halfling", "Gnomo", "Semielfo", "Semiorco", "Tiefling", "Draconido"]
        ttk.Combobox(campos_frame, textvariable=raza_var, values=razas, width=28).grid(row=2, column=1, sticky="ew", pady=5)
        
        # Nivel
        ttk.Label(campos_frame, text="Nivel:").grid(row=3, column=0, sticky="w", pady=5)
        nivel_var = tk.StringVar(value="1")
        ttk.Spinbox(campos_frame, from_=1, to=20, textvariable=nivel_var, width=5).grid(row=3, column=1, sticky="w", pady=5)
        
        # Botones
        botones_frame = ttk.Frame(dialogo)
        botones_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        def agregar():
            # Validar campos
            if not nombre_var.get().strip():
                messagebox.showwarning("Advertencia", "Debe ingresar un nombre.")
                return
            
            if not clase_var.get():
                messagebox.showwarning("Advertencia", "Debe seleccionar una clase.")
                return
            
            if not raza_var.get():
                messagebox.showwarning("Advertencia", "Debe seleccionar una raza.")
                return
            
            # Crear jugador
            jugador = {
                "nombre": nombre_var.get().strip(),
                "clase": clase_var.get(),
                "raza": raza_var.get(),
                "nivel": int(nivel_var.get())
            }
            
            # Añadir a la lista
            jugadores.append(jugador)
            
            # Actualizar lista
            actualizar_lista_jugadores()
            
            # Cerrar diálogo
            dialogo.destroy()
        
        ttk.Button(botones_frame, text="Agregar", command=agregar).pack(side="right", padx=5)
        ttk.Button(botones_frame, text="Cancelar", command=dialogo.destroy).pack(side="right", padx=5)
    
    # Frame para agregar jugadores
    agregar_frame = ttk.Frame(nueva_campana_frame)
    agregar_frame.pack(fill="x", padx=50, pady=10)
    
    ttk.Button(agregar_frame, text="Agregar Jugador", command=mostrar_agregar_jugador).pack(side="left", padx=5)
    
    # Actualizar lista de jugadores (inicialmente vacía)
    actualizar_lista_jugadores()
    
    def guardar_campana():
        """Guarda la campaña actual"""
        # Validar campos
        if not nombre_campana.get().strip():
            messagebox.showwarning("Advertencia", "Debe ingresar un nombre para la campaña.")
            return
        
        if not ambientacion.get():
            messagebox.showwarning("Advertencia", "Debe seleccionar una ambientación.")
            return
        
        # Crear diccionario de campaña
        campana = {
            "nombre": nombre_campana.get().strip(),
            "ambientacion": ambientacion.get(),
            "reglas_especiales": reglas_text.get("1.0", "end-1c"),
            "sin_muerte": sin_muerte.get(),
            "exp_modificada": exp_modificada.get(),
            "dificultad": dificultad.get(),
            "jugadores": jugadores,
            "fecha_creacion": None  # Se podría añadir la fecha actual
        }
        
        # Nombre del archivo
        nombre_archivo = nombre_campana.get().strip().replace(" ", "_").lower() + ".json"
        ruta_archivo = os.path.join(directorio_campanas, nombre_archivo)
        
        # Guardar en archivo
        try:
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                json.dump(campana, f, ensure_ascii=False, indent=4)
            
            messagebox.showinfo("Éxito", f"Campaña '{nombre_campana.get()}' guardada correctamente.")
            callback_menu()  # Volver al menú principal
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar la campaña: {str(e)}")
    
    # Botones finales
    botones_frame = ttk.Frame(nueva_campana_frame)
    botones_frame.pack(fill="x", padx=50, pady=(20, 30))
    
    ttk.Button(botones_frame, text="Guardar Campaña", command=guardar_campana).pack(side="right", padx=5)
    ttk.Button(botones_frame, text="Volver al Menú", command=callback_menu).pack(side="right", padx=5)
    
    # Mostrar el frame
    nueva_campana_frame.pack(fill="both", expand=True, padx=10, pady=10)