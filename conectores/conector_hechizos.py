#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo para integrar el gestor de hechizos con el gestor de personajes.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import os
import json
from . import gestor_hechizos

def mostrar_selector_hechizos_personaje(root, personaje, callback_seleccion):
    """
    Muestra un selector de hechizos para añadir al personaje
    
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
    
    # Crear ventana de diálogo
    dialogo = tk.Toplevel(root)
    dialogo.title(f"Seleccionar Hechizos para {personaje.get('nombre', '')}")
    dialogo.geometry("800x600")
    dialogo.transient(root)
    dialogo.grab_set()
    
    # Centrar diálogo
    dialogo.geometry("+%d+%d" % (
        root.winfo_rootx() + (root.winfo_width() // 2) - 400,
        root.winfo_rooty() + (root.winfo_height() // 2) - 300
    ))
    
    # Contenedor principal con scroll
    dialog_main = ttk.Frame(dialogo)
    dialog_main.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Título
    ttk.Label(dialog_main, text=f"Seleccionar Hechizos para {personaje.get('nombre', '')}", 
              font=('Helvetica', 16, 'bold')).pack(pady=(0, 10))
    
    # Frame para filtros
    filtro_frame = ttk.Frame(dialog_main)
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
    
    # Frame para lista de hechizos
    lista_frame = ttk.Frame(dialog_main)
    lista_frame.pack(fill="both", expand=True, padx=5, pady=5)
    
    # Crear Treeview para hechizos
    columnas = ("seleccion", "nombre", "nivel", "escuela", "tipo")
    tree = ttk.Treeview(lista_frame, columns=columnas, show='headings', height=15)
    
    # Configurar columnas
    tree.heading("seleccion", text="Seleccionar")
    tree.heading("nombre", text="Nombre")
    tree.heading("nivel", text="Nivel")
    tree.heading("escuela", text="Escuela")
    tree.heading("tipo", text="Tipo")
    
    tree.column("seleccion", width=80, anchor="center")
    tree.column("nombre", width=180)
    tree.column("nivel", width=50, anchor="center")
    tree.column("escuela", width=120)
    tree.column("tipo", width=140)
    
    # Añadir scrollbar
    scrollbar_tree = ttk.Scrollbar(lista_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar_tree.set)
    
    # Ubicar componentes
    tree.pack(side="left", fill="both", expand=True)
    scrollbar_tree.pack(side="right", fill="y")
    
    # Panel de detalles del hechizo
    detalles_frame = ttk.LabelFrame(dialog_main, text="Detalles del Hechizo")
    detalles_frame.pack(fill="x", padx=5, pady=5)
    
    # Scrollable text para mostrar detalles
    detalles_text = scrolledtext.ScrolledText(detalles_frame, wrap=tk.WORD, width=80, height=8)
    detalles_text.pack(fill="both", expand=True, padx=5, pady=5)
    detalles_text.config(state=tk.DISABLED)
    
    # Marco para botones
    botones_frame = ttk.Frame(dialog_main)
    botones_frame.pack(fill="x", padx=5, pady=10)
    
    # Obtener hechizos actuales del personaje
    hechizos_actuales = personaje.get("hechizos", [])
    
    # Diccionario para mantener el estado de selección
    seleccion = {}
    
    # Pre-seleccionar hechizos que ya tiene el personaje
    for hechizo in hechizos_actuales:
        hechizo_id = f"{hechizo.get('nombre', '')}_{hechizo.get('nivel', '0')}"
        seleccion[hechizo_id] = True
    
    # Función para actualizar la lista de hechizos según los filtros
    def actualizar_lista_hechizos():
        # Limpiar lista actual
        for item in tree.get_children():
            tree.delete(item)
        
        # Obtener filtros
        nivel = None if nivel_filtro_var.get() == "Todos" else nivel_filtro_var.get()
        escuela = None if escuela_filtro_var.get() == "Todas" else escuela_filtro_var.get()
        nombre = nombre_filtro_var.get()
        
        # Buscar hechizos
        hechizos_filtrados = gestor_hechizos.buscar_hechizos(
            filtro=nombre, nivel=nivel, escuela=escuela, clase=clase
        )
        
        # Mostrar hechizos en la tabla
        for hechizo in hechizos_filtrados:
            # Determinar tipo de hechizo
            tipo = "Ataque"
            if hechizo.get("requiere_salvacion", False):
                tipo = f"Salvación ({hechizo.get('tipo_salvacion', 'Ninguna')})"
            elif hechizo.get("tipo_ataque", "Ninguno") == "Ninguno":
                tipo = "Utilidad"
                if hechizo.get("curacion_base", ""):
                    tipo = "Curación"
            
            # Obtener ID único para el hechizo
            hechizo_id = f"{hechizo.get('nombre', '')}_{hechizo.get('nivel', '0')}"
            
            # Obtener estado de selección
            check_value = "✓" if seleccion.get(hechizo_id, False) else ""
            
            # Insertar en el árbol
            tree.insert("", "end", values=(
                check_value,
                hechizo.get("nombre", ""),
                hechizo.get("nivel", "0"),
                hechizo.get("escuela", ""),
                tipo
            ), tags=(hechizo_id,))
    
    # Función para mostrar detalles del hechizo seleccionado
    def mostrar_detalles(event):
        # Obtener ítem seleccionado
        seleccion_actual = tree.selection()
        if not seleccion_actual:
            return
        
        # Obtener valores del ítem
        item = tree.item(seleccion_actual[0])
        nombre_hechizo = item["values"][1]
        nivel_hechizo = item["values"][2]
        
        # Buscar hechizo en la base de datos
        hechizo = gestor_hechizos.obtener_hechizo_por_nombre(nombre_hechizo, nivel_hechizo)
        
        if not hechizo:
            return
        
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
    
    # Función para manejar la selección/deselección
    def alternar_seleccion(event):
        # Obtener ítem seleccionado
        seleccion_actual = tree.selection()
        if not seleccion_actual:
            return
        
        # Obtener valores del ítem
        item = tree.item(seleccion_actual[0])
        hechizo_id = tree.item(seleccion_actual[0], "tags")[0]
        valores = list(item["values"])
        
        # Cambiar estado de selección
        if valores[0] == "✓":
            valores[0] = ""
            seleccion[hechizo_id] = False
        else:
            valores[0] = "✓"
            seleccion[hechizo_id] = True
        
        # Actualizar ítem
        tree.item(seleccion_actual[0], values=valores)
    
    # Vincular eventos
    tree.bind("<<TreeviewSelect>>", mostrar_detalles)
    tree.bind("<Double-1>", alternar_seleccion)
    
    # Simular lanzamiento de un hechizo seleccionado
    def simular_lanzamiento():
        # Obtener ítem seleccionado
        seleccion_actual = tree.selection()
        if not seleccion_actual:
            messagebox.showinfo("Información", "Por favor, seleccione un hechizo para simular.")
            return
        
        # Obtener valores del ítem
        item = tree.item(seleccion_actual[0])
        nombre_hechizo = item["values"][1]
        nivel_hechizo = item["values"][2]
        
        # Buscar hechizo en la base de datos
        hechizo = gestor_hechizos.obtener_hechizo_por_nombre(nombre_hechizo, nivel_hechizo)
        
        if not hechizo:
            messagebox.showinfo("Información", "No se pudo encontrar el hechizo seleccionado.")
            return
        
        # Determinar estadística de lanzamiento según la clase
        estadistica_principal = "Inteligencia"  # Por defecto para magos
        if clase in ["Clérigo", "Druida", "Explorador"]:
            estadistica_principal = "Sabiduría"
        elif clase in ["Bardo", "Brujo", "Paladín", "Hechicero"]:
            estadistica_principal = "Carisma"
        
        # Obtener modificador del atributo principal
        estadisticas = personaje.get("estadisticas", {})
        mod_atributo = 0
        if estadistica_principal in estadisticas:
            valor = estadisticas.get(estadistica_principal, 10)
            mod_atributo = (valor - 10) // 2
        
        # Obtener nivel de personaje y calcular bonificador de competencia
        nivel_personaje = personaje.get("nivel", 1)
        bono_comp = 2 + ((nivel_personaje - 1) // 4)
        
        # Ventana para elegir nivel de lanzamiento
        nivel_dialogo = tk.Toplevel(dialogo)
        nivel_dialogo.title("Nivel de Lanzamiento")
        nivel_dialogo.geometry("300x200")
        nivel_dialogo.transient(dialogo)
        nivel_dialogo.grab_set()
        
        # Centrar diálogo
        nivel_dialogo.geometry("+%d+%d" % (
            dialogo.winfo_rootx() + (dialogo.winfo_width() // 2) - 150,
            dialogo.winfo_rooty() + (dialogo.winfo_height() // 2) - 100
        ))
        
        ttk.Label(nivel_dialogo, text="Simular Lanzamiento", font=('Helvetica', 12, 'bold')).pack(pady=(10, 20))
        
        # Frame para nivel de lanzamiento
        nivel_frame = ttk.Frame(nivel_dialogo)
        nivel_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Label(nivel_frame, text="Nivel de lanzamiento:").pack(side="left", padx=5)
        
        # Determinar niveles disponibles
        nivel_min = int(nivel_hechizo)
        nivel_max = min(9, nivel_personaje)  # Limitar por nivel del personaje
        
        if nivel_min > nivel_max:
            messagebox.showinfo("Información", 
                               f"El personaje no tiene nivel suficiente para lanzar este hechizo (nivel {nivel_min}).")
            nivel_dialogo.destroy()
            return
        
        nivel_lanz_var = tk.StringVar(value=str(nivel_min))
        nivel_values = [str(i) for i in range(nivel_min, nivel_max + 1)]
        ttk.Combobox(nivel_frame, textvariable=nivel_lanz_var, values=nivel_values, width=5).pack(side="left", padx=5)
        
        # Función para completar simulación
        def ejecutar_simulacion():
            try:
                nivel_lanzamiento = int(nivel_lanz_var.get())
                
                # Simular lanzamiento
                resultado = gestor_hechizos.simular_lanzamiento_hechizo(
                    hechizo, 
                    nivel_lanzamiento=nivel_lanzamiento,
                    estadistica_conjuros=mod_atributo,
                    bono_competencia=bono_comp
                )
                
                # Mostrar resultados
                resultado_dialogo = tk.Toplevel(dialogo)
                resultado_dialogo.title("Resultado de Lanzamiento")
                resultado_dialogo.geometry("400x400")
                resultado_dialogo.transient(dialogo)
                resultado_dialogo.grab_set()
                
                # Centrar diálogo
                resultado_dialogo.geometry("+%d+%d" % (
                    dialogo.winfo_rootx() + (dialogo.winfo_width() // 2) - 200,
                    dialogo.winfo_rooty() + (dialogo.winfo_height() // 2) - 200
                ))
                
                ttk.Label(resultado_dialogo, text=f"Lanzamiento de {resultado['nombre']}", 
                         font=('Helvetica', 14, 'bold')).pack(pady=(10, 5))
                ttk.Label(resultado_dialogo, text=f"Nivel {resultado['nivel_lanzamiento']} ({resultado['nivel_hechizo']} + {resultado['nivel_lanzamiento'] - resultado['nivel_hechizo']})").pack(pady=(0, 10))
                
                # Valores de lanzamiento
                info_frame = ttk.LabelFrame(resultado_dialogo, text="Información de Lanzamiento")
                info_frame.pack(fill="x", padx=20, pady=5)
                
                ttk.Label(info_frame, text=f"CD de Salvación: {resultado['cd_salvacion']}").pack(anchor="w", padx=10, pady=2)
                ttk.Label(info_frame, text=f"Bono de Ataque: +{resultado['bono_ataque']}").pack(anchor="w", padx=10, pady=2)
                
                # Tirada de ataque si hay
                if resultado['tirada_ataque']:
                    ataque_frame = ttk.LabelFrame(resultado_dialogo, text="Tirada de Ataque")
                    ataque_frame.pack(fill="x", padx=20, pady=5)
                    
                    ttk.Label(ataque_frame, text=f"Tirada: {resultado['tirada_ataque']['d20']} (d20) + {resultado['tirada_ataque']['bono']} = {resultado['tirada_ataque']['total']}").pack(anchor="w", padx=10, pady=2)
                    
                    if resultado['tirada_ataque']['critico']:
                        ttk.Label(ataque_frame, text="¡CRÍTICO!", foreground="green").pack(anchor="w", padx=10, pady=2)
                    if resultado['tirada_ataque']['pifia']:
                        ttk.Label(ataque_frame, text="¡PIFIA!", foreground="red").pack(anchor="w", padx=10, pady=2)
                
                # Salvación si hay
                if resultado['exito_salvacion']:
                    salv_frame = ttk.LabelFrame(resultado_dialogo, text=f"Salvación de {resultado['exito_salvacion']['tipo']}")
                    salv_frame.pack(fill="x", padx=20, pady=5)
                    
                    ttk.Label(salv_frame, text=f"CD: {resultado['exito_salvacion']['cd']}").pack(anchor="w", padx=10, pady=2)
                    ttk.Label(salv_frame, text=f"Tirada: {resultado['exito_salvacion']['d20']} (d20) + {resultado['exito_salvacion']['bono']} = {resultado['exito_salvacion']['total']}").pack(anchor="w", padx=10, pady=2)
                    
                    if resultado['exito_salvacion']['exito']:
                        ttk.Label(salv_frame, text=f"¡ÉXITO! {resultado['exito_salvacion']['efecto']}").pack(anchor="w", padx=10, pady=2)
                    else:
                        ttk.Label(salv_frame, text="¡FALLO!").pack(anchor="w", padx=10, pady=2)
                
                # Daño si hay
                if resultado['daño']['resultado'] > 0:
                    daño_frame = ttk.LabelFrame(resultado_dialogo, text="Daño")
                    daño_frame.pack(fill="x", padx=20, pady=5)
                    
                    ttk.Label(daño_frame, text=f"Tipo: {resultado['daño']['tipo']}").pack(anchor="w", padx=10, pady=2)
                    ttk.Label(daño_frame, text=f"Resultado: {resultado['daño']['resultado']} puntos de daño").pack(anchor="w", padx=10, pady=2)
                
                # Curación si hay
                if resultado['curacion']['resultado'] > 0:
                    cur_frame = ttk.LabelFrame(resultado_dialogo, text="Curación")
                    cur_frame.pack(fill="x", padx=20, pady=5)
                    
                    ttk.Label(cur_frame, text=f"Resultado: {resultado['curacion']['resultado']} puntos de golpe").pack(anchor="w", padx=10, pady=2)
                
                # Botón para cerrar
                ttk.Button(resultado_dialogo, text="Cerrar", 
                          command=resultado_dialogo.destroy).pack(pady=20)
                
                # Cerrar diálogo de nivel
                nivel_dialogo.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error en la simulación: {str(e)}")
                nivel_dialogo.destroy()
        
        # Botones
        ttk.Button(nivel_dialogo, text="Simular", command=ejecutar_simulacion).pack(pady=20)
        ttk.Button(nivel_dialogo, text="Cancelar", command=nivel_dialogo.destroy).pack(pady=5)
    
    # Función para completar la selección
    def completar_seleccion():
        # Obtener hechizos seleccionados
        hechizos_seleccionados = []
        
        for hechizo_id, seleccionado in seleccion.items():
            if seleccionado:
                # Extraer nombre y nivel del ID
                nombre, nivel = hechizo_id.rsplit("_", 1)
                
                # Buscar hechizo completo
                hechizo = gestor_hechizos.obtener_hechizo_por_nombre(nombre, nivel)
                if hechizo:
                    hechizos_seleccionados.append(hechizo)
        
        # Cerrar diálogo
        dialogo.destroy()
        
        # Llamar a callback con los hechizos seleccionados
        callback_seleccion(hechizos_seleccionados)
    
    # Botones de acción
    ttk.Button(botones_frame, text="Gestionar Hechizos", 
              command=lambda: gestor_hechizos.mostrar_gestor_hechizos(root, lambda: mostrar_selector_hechizos_personaje(root, personaje, callback_seleccion))).pack(side="left", padx=5)
    
    ttk.Button(botones_frame, text="Simular Lanzamiento", 
              command=simular_lanzamiento).pack(side="left", padx=5)
    
    ttk.Button(botones_frame, text="Aceptar", 
              command=completar_seleccion).pack(side="right", padx=5)
    
    ttk.Button(botones_frame, text="Cancelar", 
              command=lambda: (dialogo.destroy(), callback_seleccion(hechizos_actuales))).pack(side="right", padx=5)
    
    # Inicializar lista
    actualizar_lista_hechizos()