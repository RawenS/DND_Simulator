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
    
    # Crear nuevo frame para la campaña con scrollbar
    main_container = ttk.Frame(root)
    main_container.pack(fill="both", expand=True)
    main_container.columnconfigure(0, weight=1)
    main_container.rowconfigure(0, weight=1)
    
    # Crear canvas con scrollbar para manejo de contenido grande
    canvas = tk.Canvas(main_container)
    scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
    nueva_campana_frame = ttk.Frame(canvas)
    
    # Configurar canvas
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Añadir evento para redimensionar el frame en el canvas
    def configure_frame(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.itemconfig(frame_id, width=event.width)
    
    frame_id = canvas.create_window((0, 0), window=nueva_campana_frame, anchor="nw")
    nueva_campana_frame.bind("<Configure>", configure_frame)
    canvas.bind("<Configure>", lambda e: configure_frame(e))
    
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
    
    # Configurar columnas para adaptarse al contenido
    params_frame.columnconfigure(1, weight=1)
    
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
        """Muestra un mensaje de funcionalidad no implementada"""
        messagebox.showinfo("Información", "Esta funcionalidad requiere el Gestor de Personajes que aún no está implementado.")
    
    def mostrar_agregar_jugador():
        """Muestra un mensaje de funcionalidad no implementada"""
        messagebox.showinfo("Información", "Esta funcionalidad requiere el Gestor de Personajes que aún no está implementado. Debe crear los personajes primero para poder agregarlos a la campaña.")
    
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
            # Limpiar correctamente al guardar
            canvas.unbind_all("<MouseWheel>")
            main_container.destroy()
            callback_menu()  # Volver al menú principal
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar la campaña: {str(e)}")
    
    # Botones finales
    botones_frame = ttk.Frame(nueva_campana_frame)
    botones_frame.pack(fill="x", padx=50, pady=(20, 30))
    
    # Función modificada para asegurar la limpieza adecuada
    def volver_menu():
        # Desenlazar eventos de scroll
        canvas.unbind_all("<MouseWheel>")
        # Destruir el contenedor principal por completo
        main_container.destroy()
        # Llamar al callback del menú principal
        callback_menu()
    
    ttk.Button(botones_frame, text="Guardar Campaña", command=guardar_campana).pack(side="right", padx=5)
    ttk.Button(botones_frame, text="Volver al Menú", command=volver_menu).pack(side="right", padx=5)
    
    # Añadir atajos de teclado para navegación con scroll
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    # Configurar el tamaño mínimo del canvas
    canvas.update_idletasks()
    min_width = max(800, nueva_campana_frame.winfo_reqwidth())
    min_height = max(600, nueva_campana_frame.winfo_reqheight())
    canvas.config(width=min_width, height=min_height)
    
    # Actualizar el scrollregion
    canvas.configure(scrollregion=canvas.bbox("all"))