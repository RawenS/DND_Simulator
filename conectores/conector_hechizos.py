#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo para integrar el gestor de hechizos con el gestor de personajes.
Versión simplificada para selección directa de hechizos.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from editores import gestor_hechizos

def mostrar_selector_hechizos_personaje(root, personaje, callback_seleccion):
    """
    Muestra un selector simplificado de hechizos para añadir al personaje
    
    Args:
        root: La ventana principal de la aplicación
        personaje (dict): Datos del personaje
        callback_seleccion: Función para procesar los hechizos seleccionados
    """
    # Verificar que la clase del personaje use magia
    clase = personaje.get("clase", "")
    if clase not in gestor_hechizos.CLASES_MAGICAS:
        messagebox.showinfo("Información", 
                           f"La clase {clase} no puede lanzar hechizos.")
        return
    
    # Verificar si hay hechizos disponibles
    hay_hechizos = gestor_hechizos.inicializar_directorios()
    hechizos = gestor_hechizos.cargar_hechizos()
    
    hechizos_disponibles = gestor_hechizos.obtener_hechizos_por_clase_y_nivel(
        clase, 
        nivel_max=min(9, personaje.get("nivel", 1) // 2 + 1)  # Limitar por nivel del personaje
    )
    
    if not hechizos_disponibles:
        if messagebox.askyesno("Sin hechizos", 
                              f"No hay hechizos disponibles para {clase}. ¿Desea crear algunos hechizos de ejemplo?"):
            gestor_hechizos.crear_hechizos_ejemplo()
            hechizos_disponibles = gestor_hechizos.obtener_hechizos_por_clase_y_nivel(
                clase, 
                nivel_max=min(9, personaje.get("nivel", 1) // 2 + 1)
            )
        else:
            return
    
    # Crear ventana de diálogo simplificada
    dialogo = tk.Toplevel(root)
    dialogo.title(f"Seleccionar Hechizos para {personaje.get('nombre', '')}")
    dialogo.geometry("850x600")
    dialogo.transient(root)
    dialogo.grab_set()
    
    # Centrar diálogo
    dialogo.geometry("+%d+%d" % (
        root.winfo_rootx() + (root.winfo_width() // 2) - 425,
        root.winfo_rooty() + (root.winfo_height() // 2) - 300
    ))
    
    # Contenedor principal
    main_frame = ttk.Frame(dialogo)
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Título
    ttk.Label(main_frame, text=f"Seleccionar Hechizos para {personaje.get('nombre', '')}", 
              font=('Helvetica', 16, 'bold')).pack(pady=(0, 10))
    
    # Frame para filtros
    filtro_frame = ttk.Frame(main_frame)
    filtro_frame.pack(fill="x", padx=5, pady=5)
    
    # Filtro por nivel
    ttk.Label(filtro_frame, text="Nivel:").pack(side="left", padx=5)
    nivel_filtro_var = tk.StringVar(value="Todos")
    nivel_valores = ["Todos"] + [str(i) for i in range(min(10, personaje.get("nivel", 1) // 2 + 1))]
    ttk.Combobox(filtro_frame, textvariable=nivel_filtro_var, values=nivel_valores, width=10).pack(side="left", padx=5)
    
    # Filtro por escuela
    ttk.Label(filtro_frame, text="Escuela:").pack(side="left", padx=(20, 5))
    escuela_filtro_var = tk.StringVar(value="Todas")
    escuela_valores = ["Todas"] + gestor_hechizos.ESCUELAS
    ttk.Combobox(filtro_frame, textvariable=escuela_filtro_var, values=escuela_valores, width=15).pack(side="left", padx=5)
    
    # Filtro por nombre
    ttk.Label(filtro_frame, text="Nombre:").pack(side="left", padx=(20, 5))
    nombre_filtro_var = tk.StringVar()
    ttk.Entry(filtro_frame, textvariable=nombre_filtro_var, width=20).pack(side="left", padx=5)
    
    # Botón de filtrar
    ttk.Button(filtro_frame, text="Filtrar", command=lambda: actualizar_lista_hechizos()).pack(side="left", padx=20)
    
    # Frame para lista de hechizos con scroll
    lista_container = ttk.Frame(main_frame)
    lista_container.pack(fill="both", expand=True, padx=5, pady=5)
    
    # Crear canvas con scrollbar
    lista_canvas = tk.Canvas(lista_container)
    lista_scrollbar = ttk.Scrollbar(lista_container, orient="vertical", command=lista_canvas.yview)
    lista_frame = ttk.Frame(lista_canvas)
    
    # Configurar canvas y scrollbar
    lista_canvas.configure(yscrollcommand=lista_scrollbar.set)
    lista_canvas.pack(side="left", fill="both", expand=True)
    lista_scrollbar.pack(side="right", fill="y")
    
    # Añadir evento para redimensionar el frame en el canvas
    def configure_lista_frame(event):
        lista_canvas.configure(scrollregion=lista_canvas.bbox("all"))
        lista_canvas.itemconfig(lista_frame_id, width=event.width)
    
    lista_frame_id = lista_canvas.create_window((0, 0), window=lista_frame, anchor="nw")
    lista_frame.bind("<Configure>", configure_lista_frame)
    lista_canvas.bind("<Configure>", lambda e: configure_lista_frame(e))
    
    # Panel de detalles del hechizo
    detalles_frame = ttk.LabelFrame(main_frame, text="Detalles del Hechizo")
    detalles_frame.pack(fill="x", padx=5, pady=5)
    
    # Scrollable text para mostrar detalles
    detalles_text = scrolledtext.ScrolledText(detalles_frame, wrap=tk.WORD, width=80, height=8)
    detalles_text.pack(fill="both", expand=True, padx=5, pady=5)
    detalles_text.config(state=tk.DISABLED)
    
    # Marco para botones
    botones_frame = ttk.Frame(main_frame)
    botones_frame.pack(fill="x", padx=5, pady=10)
    
    # Obtener hechizos actuales del personaje
    hechizos_actuales = personaje.get("hechizos", [])
    
    # Diccionario para mantener el estado de selección y los widgets de checkbox
    seleccion = {}
    checkbox_vars = {}
    
    # Función para actualizar la lista de hechizos según los filtros
    def actualizar_lista_hechizos():
        # Limpiar lista actual
        for widget in lista_frame.winfo_children():
            widget.destroy()
        
        # Obtener filtros
        nivel = None if nivel_filtro_var.get() == "Todos" else nivel_filtro_var.get()
        escuela = None if escuela_filtro_var.get() == "Todas" else escuela_filtro_var.get()
        nombre = nombre_filtro_var.get()
        
        # Buscar hechizos
        hechizos_filtrados = gestor_hechizos.buscar_hechizos(
            filtro=nombre, nivel=nivel, escuela=escuela, clase=clase
        )
        
        # Crear encabezados
        ttk.Label(lista_frame, text="Seleccionar", 
                 font=("Helvetica", 11, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Label(lista_frame, text="Nombre", 
                 font=("Helvetica", 11, "bold")).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ttk.Label(lista_frame, text="Nivel", 
                 font=("Helvetica", 11, "bold")).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        ttk.Label(lista_frame, text="Escuela", 
                 font=("Helvetica", 11, "bold")).grid(row=0, column=3, padx=5, pady=5, sticky="w")
        ttk.Label(lista_frame, text="Tipo", 
                 font=("Helvetica", 11, "bold")).grid(row=0, column=4, padx=5, pady=5, sticky="w")
        
        # Si no hay hechizos, mostrar mensaje
        if not hechizos_filtrados:
            ttk.Label(lista_frame, text="No se encontraron hechizos con esos filtros", 
                     font=("Helvetica", 10, "italic")).grid(row=1, column=0, columnspan=5, padx=5, pady=10)
            return
        
        # Mostrar hechizos en filas con checkboxes
        for i, hechizo in enumerate(hechizos_filtrados):
            # Obtener ID único para el hechizo
            hechizo_id = f"{hechizo.get('nombre', '')}_{hechizo.get('nivel', '0')}"
            
            # Crear checkbox
            checkbox_vars[hechizo_id] = tk.BooleanVar(value=False)
            
            # Pre-seleccionar si ya está en hechizos actuales
            for h in hechizos_actuales:
                if h.get("nombre") == hechizo.get("nombre") and h.get("nivel") == hechizo.get("nivel"):
                    checkbox_vars[hechizo_id].set(True)
                    seleccion[hechizo_id] = hechizo
                    break
            
            # Añadir a selección si se marca
            def actualizar_seleccion(var, hechizo_id, hechizo):
                if var.get():
                    seleccion[hechizo_id] = hechizo
                else:
                    if hechizo_id in seleccion:
                        del seleccion[hechizo_id]
            
            # Checkbox vinculado a la función
            chk = ttk.Checkbutton(lista_frame, variable=checkbox_vars[hechizo_id], 
                                command=lambda v=checkbox_vars[hechizo_id], id=hechizo_id, h=hechizo: 
                                actualizar_seleccion(v, id, h))
            chk.grid(row=i+1, column=0, padx=5, pady=2)
            
            # Determinar tipo de hechizo
            tipo = "Ataque"
            if hechizo.get("requiere_salvacion", False):
                tipo = f"Salvación ({hechizo.get('tipo_salvacion', 'Ninguna')})"
            elif hechizo.get("tipo_ataque", "Ninguno") == "Ninguno":
                tipo = "Utilidad"
                if hechizo.get("curacion_base", ""):
                    tipo = "Curación"
            
            # Usar un botón normal sin estilos especiales
            nombre_btn = ttk.Button(lista_frame, text=hechizo.get("nombre", ""),
                                  command=lambda h=hechizo: mostrar_detalles_hechizo(h))
            nombre_btn.grid(row=i+1, column=1, padx=5, pady=2, sticky="w")
            
            ttk.Label(lista_frame, text=hechizo.get("nivel", "0")).grid(row=i+1, column=2, padx=5, pady=2, sticky="w")
            ttk.Label(lista_frame, text=hechizo.get("escuela", "")).grid(row=i+1, column=3, padx=5, pady=2, sticky="w")
            ttk.Label(lista_frame, text=tipo).grid(row=i+1, column=4, padx=5, pady=2, sticky="w")
    
    # Función para mostrar detalles del hechizo
    def mostrar_detalles_hechizo(hechizo):
        # Habilitar el widget para actualizar
        detalles_text.config(state=tk.NORMAL)
        detalles_text.delete(1.0, tk.END)
        
        # Formatear y mostrar detalles
        detalles = f"{hechizo.get('nombre', '')}\n"
        detalles += f"Nivel {hechizo.get('nivel', '0')} - {hechizo.get('escuela', '')}\n\n"
        detalles += f"Tiempo de lanzamiento: {hechizo.get('tiempo_lanzamiento', '')}\n"
        detalles += f"Alcance: {hechizo.get('alcance', '')}\n"
        detalles += f"Componentes: {hechizo.get('componentes', '')}\n"
        detalles += f"Duración: {hechizo.get('duracion', '')}\n\n"
        
        # Información de tirada de ataque o salvación
        if hechizo.get("tipo_ataque", "Ninguno") != "Ninguno":
            detalles += f"Ataque: {hechizo.get('tipo_ataque', '')}\n"
        
        if hechizo.get("requiere_salvacion", False):
            detalles += f"Salvación: {hechizo.get('tipo_salvacion', '')}\n"
            detalles += f"Efecto en salvación exitosa: {hechizo.get('efecto_salvacion', 'Ninguno')}\n"
        
        # Información de daño/curación
        if hechizo.get("daño_base", ""):
            detalles += f"Daño base: {hechizo.get('daño_base', '')} ({hechizo.get('tipo_daño', 'Ninguno')})\n"
        
        if hechizo.get("curacion_base", ""):
            detalles += f"Curación base: {hechizo.get('curacion_base', '')}\n"
        
        if hechizo.get("daño_nivel_superior", "") or hechizo.get("curacion_nivel_superior", ""):
            detalles += "\nA niveles superiores:\n"
            if hechizo.get("daño_nivel_superior", ""):
                detalles += f"Daño adicional: {hechizo.get('daño_nivel_superior', '')} por nivel\n"
            if hechizo.get("curacion_nivel_superior", ""):
                detalles += f"Curación adicional: {hechizo.get('curacion_nivel_superior', '')} por nivel\n"
        
        detalles += f"\nClases: {', '.join(hechizo.get('clases', []))}\n\n"
        detalles += f"Descripción:\n{hechizo.get('descripcion', '')}"
        
        detalles_text.insert(tk.END, detalles)
        detalles_text.config(state=tk.DISABLED)
    
    # Función para completar la selección
    def completar_seleccion():
        # Obtener hechizos seleccionados
        hechizos_seleccionados = list(seleccion.values())
        
        # Cerrar diálogo
        dialogo.destroy()
        
        # Llamar a callback con los hechizos seleccionados
        callback_seleccion(hechizos_seleccionados)
    
    # Función para seleccionar/deseleccionar todos
    def seleccionar_todos():
        for hechizo_id, var in checkbox_vars.items():
            var.set(True)
            # Encontrar y añadir el hechizo correspondiente
            for nivel, hechizos_nivel in hechizos.items():
                for h in hechizos_nivel:
                    if f"{h.get('nombre', '')}_{h.get('nivel', '0')}" == hechizo_id:
                        seleccion[hechizo_id] = h
                        break
    
    def deseleccionar_todos():
        for var in checkbox_vars.values():
            var.set(False)
        seleccion.clear()
    
    # Botones de selección múltiple
    select_frame = ttk.Frame(main_frame)
    select_frame.pack(fill="x", padx=5, pady=5)
    
    ttk.Button(select_frame, text="Seleccionar Todos", 
              command=seleccionar_todos).pack(side="left", padx=5)
    ttk.Button(select_frame, text="Deseleccionar Todos", 
              command=deseleccionar_todos).pack(side="left", padx=5)
    
    # Botones principales
    ttk.Button(botones_frame, text="Aceptar", 
              command=completar_seleccion).pack(side="right", padx=5)
    ttk.Button(botones_frame, text="Cancelar", 
              command=lambda: (dialogo.destroy(), callback_seleccion(hechizos_actuales))).pack(side="right", padx=5)
    
    # Inicializar lista de hechizos
    actualizar_lista_hechizos()
    
    # Permitir rueda del ratón para scroll en el canvas
    def _on_mousewheel(event):
        lista_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    lista_canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    # Cuando se cierra el diálogo, desenlazar eventos
    def on_dialog_close():
        lista_canvas.unbind_all("<MouseWheel>")
        dialogo.destroy()
        callback_seleccion(hechizos_actuales)
    
    dialogo.protocol("WM_DELETE_WINDOW", on_dialog_close)