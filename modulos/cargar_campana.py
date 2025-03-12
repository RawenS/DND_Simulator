#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo para cargar una campaña existente en la aplicación D&D Combat Manager.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os

def mostrar_cargar_campana(root, directorio_campanas, callback_menu, callback_cargar_campana=None):
    """
    Muestra la pantalla para cargar una campaña existente
    
    Args:
        root: La ventana principal de la aplicación
        directorio_campanas: Directorio donde se guardan las campañas
        callback_menu: Función para volver al menú principal
        callback_cargar_campana: Función para cargar la campaña en la aplicación principal
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
    cargar_campana_frame = ttk.Frame(canvas)
    
    # Configurar canvas y scrollbar
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Crear ventana dentro del canvas para el frame
    def configure_frame(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.itemconfig(frame_id, width=event.width)
    
    frame_id = canvas.create_window((0, 0), window=cargar_campana_frame, anchor="nw")
    cargar_campana_frame.bind("<Configure>", configure_frame)
    canvas.bind("<Configure>", lambda e: configure_frame(e))
    
    # Título
    titulo = ttk.Label(cargar_campana_frame, text="Cargar Campaña", style="Title.TLabel")
    titulo.pack(pady=(20, 10))
    
    # Frame para la lista de campañas
    lista_frame = ttk.Frame(cargar_campana_frame)
    lista_frame.pack(fill="both", expand=True, padx=50, pady=10)
    
    # Configurar grid para que se expanda
    for i in range(4):  # 4 columnas
        lista_frame.columnconfigure(i, weight=1)
    
    # Obtener lista de campañas guardadas
    campanas = []
    try:
        for archivo in os.listdir(directorio_campanas):
            if archivo.endswith('.json'):
                ruta = os.path.join(directorio_campanas, archivo)
                with open(ruta, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
                    campanas.append({
                        "nombre": datos.get("nombre", "Sin nombre"),
                        "ambientacion": datos.get("ambientacion", ""),
                        "jugadores": len(datos.get("jugadores", [])),
                        "ruta": ruta,
                        "datos_completos": datos  # Guardar todos los datos para usarlos después
                    })
    except Exception as e:
        messagebox.showerror("Error", f"Error al cargar las campañas: {str(e)}")
    
    # Mostrar campañas
    if not campanas:
        ttk.Label(lista_frame, text="No hay campañas guardadas").pack(pady=20)
    else:
        # Crear cabecera
        ttk.Label(lista_frame, text="Nombre", font=('Helvetica', 11, 'bold')).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Label(lista_frame, text="Ambientación", font=('Helvetica', 11, 'bold')).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ttk.Label(lista_frame, text="Jugadores", font=('Helvetica', 11, 'bold')).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        ttk.Label(lista_frame, text="Acciones", font=('Helvetica', 11, 'bold')).grid(row=0, column=3, padx=5, pady=5, sticky="w")
        
        # Mostrar campañas
        for i, campana in enumerate(campanas):
            ttk.Label(lista_frame, text=campana["nombre"]).grid(row=i+1, column=0, padx=5, pady=3, sticky="w")
            ttk.Label(lista_frame, text=campana["ambientacion"]).grid(row=i+1, column=1, padx=5, pady=3, sticky="w")
            ttk.Label(lista_frame, text=str(campana["jugadores"])).grid(row=i+1, column=2, padx=5, pady=3, sticky="w")
            
            # Botones de acción
            acciones_frame = ttk.Frame(lista_frame)
            acciones_frame.grid(row=i+1, column=3, padx=5, pady=3, sticky="w")
            
            # Datos para la lambda
            campana_actual = campana["datos_completos"]
            ruta = campana["ruta"]
            
            # Botón para cargar directamente la campaña (vuelve al menú principal)
            ttk.Button(acciones_frame, text="Cargar", 
                      command=lambda c=campana_actual, r=ruta: cargar_y_volver(c, r)).pack(side="left", padx=2)
            
            # Botón para ver detalles
            ttk.Button(acciones_frame, text="Ver Detalles", 
                      command=lambda c=campana_actual, r=ruta: mostrar_detalles_campana(root, c, r, callback_menu, callback_cargar_campana)).pack(side="left", padx=2)
    
    def cargar_y_volver(campana, ruta):
        """Carga la campaña y vuelve al menú principal directamente"""
        if callback_cargar_campana:
            # Desenlazar eventos de scroll
            canvas.unbind_all("<MouseWheel>")
            # Destruir el contenedor
            main_container.destroy()
            # Cargar la campaña y volver al menú principal
            callback_cargar_campana(campana, ruta)
        else:
            messagebox.showinfo("Información", "La función de cargar campaña no está disponible.")
    
    def cargar_archivo():
        """Abre un diálogo para seleccionar un archivo de campaña"""
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo de campaña",
            filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")],
            initialdir=directorio_campanas
        )
        
        if ruta:
            try:
                with open(ruta, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
                    
                # Cargar directamente la campaña y volver al menú principal
                cargar_y_volver(datos, ruta)
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar el archivo: {str(e)}")
    
    # Frame para botones
    botones_frame = ttk.Frame(cargar_campana_frame)
    botones_frame.pack(fill="x", padx=50, pady=10)
    
    # Función modificada para asegurar la limpieza adecuada
    def volver_menu():
        # Desenlazar eventos de scroll
        canvas.unbind_all("<MouseWheel>")
        # Destruir el contenedor principal por completo
        main_container.destroy()
        # Llamar al callback del menú principal
        callback_menu()
    
    # Botón para cargar desde archivo
    ttk.Button(botones_frame, text="Cargar desde archivo", 
              command=cargar_archivo).pack(side="left", padx=5, pady=10)
    
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

def mostrar_detalles_campana(root, campana, ruta, callback_menu, callback_cargar_campana=None):
    """
    Muestra los detalles de una campaña cargada
    
    Args:
        root: La ventana principal de la aplicación
        campana: Datos de la campaña
        ruta: Ruta del archivo de la campaña
        callback_menu: Función para volver al menú principal
        callback_cargar_campana: Función para cargar la campaña en la aplicación principal
    """
    # Ocultar frames existentes
    for widget in root.winfo_children():
        if isinstance(widget, ttk.Frame):
            widget.pack_forget()
    
    # Crear nuevo frame para detalles
    detalles_frame = ttk.Frame(root)
    detalles_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Crear canvas con scrollbar para contenido adaptable
    canvas_detalles = tk.Canvas(detalles_frame)
    scrollbar_detalles = ttk.Scrollbar(detalles_frame, orient="vertical", command=canvas_detalles.yview)
    detalles_content = ttk.Frame(canvas_detalles)
    
    # Configurar canvas y scrollbar
    canvas_detalles.configure(yscrollcommand=scrollbar_detalles.set)
    canvas_detalles.pack(side="left", fill="both", expand=True)
    scrollbar_detalles.pack(side="right", fill="y")
    
    # Crear ventana dentro del canvas para el frame
    def configure_detalles_frame(event):
        canvas_detalles.configure(scrollregion=canvas_detalles.bbox("all"))
        canvas_detalles.itemconfig(detalles_id, width=event.width)
    
    detalles_id = canvas_detalles.create_window((0, 0), window=detalles_content, anchor="nw")
    detalles_content.bind("<Configure>", configure_detalles_frame)
    canvas_detalles.bind("<Configure>", lambda e: configure_detalles_frame(e))
    
    # Título
    titulo = ttk.Label(detalles_content, text=f"Campaña: {campana['nombre']}", style="Title.TLabel")
    titulo.pack(pady=(20, 10))
    
    # Frame para detalles
    info_frame = ttk.Frame(detalles_content)
    info_frame.pack(fill="x", padx=50, pady=10)
    
    # Mostrar detalles básicos
    ttk.Label(info_frame, text="Ambientación:", font=('Helvetica', 11, 'bold')).grid(row=0, column=0, sticky="w", pady=5)
    ttk.Label(info_frame, text=campana.get("ambientacion", "No especificada")).grid(row=0, column=1, sticky="w", pady=5)
    
    ttk.Label(info_frame, text="Dificultad:", font=('Helvetica', 11, 'bold')).grid(row=1, column=0, sticky="w", pady=5)
    ttk.Label(info_frame, text=campana.get("dificultad", "Normal")).grid(row=1, column=1, sticky="w", pady=5)
    
    # Opciones especiales
    opciones = []
    if campana.get("sin_muerte", False):
        opciones.append("Sin muerte súbita")
    if campana.get("exp_modificada", False):
        opciones.append("Experiencia modificada")
    
    ttk.Label(info_frame, text="Opciones especiales:", font=('Helvetica', 11, 'bold')).grid(row=2, column=0, sticky="nw", pady=5)
    ttk.Label(info_frame, text=", ".join(opciones) if opciones else "Ninguna").grid(row=2, column=1, sticky="w", pady=5)
    
    # Reglas especiales
    ttk.Label(info_frame, text="Reglas especiales:", font=('Helvetica', 11, 'bold')).grid(row=3, column=0, sticky="nw", pady=5)
    
    reglas_text = tk.Text(info_frame, height=4, width=40)
    reglas_text.grid(row=3, column=1, sticky="ew", pady=5)
    reglas_text.insert("1.0", campana.get("reglas_especiales", ""))
    reglas_text.config(state="disabled")
    
    # Lista de jugadores
    jugadores_titulo = ttk.Label(detalles_content, text="Jugadores", style="Subtitle.TLabel")
    jugadores_titulo.pack(pady=(20, 10))
    
    jugadores_frame = ttk.Frame(detalles_content)
    jugadores_frame.pack(fill="both", expand=True, padx=50, pady=5)
    
    jugadores = campana.get("jugadores", [])
    
    if not jugadores:
        ttk.Label(jugadores_frame, text="No hay jugadores en esta campaña").pack(pady=10)
    else:
        # Crear cabecera
        ttk.Label(jugadores_frame, text="Nombre", font=('Helvetica', 11, 'bold')).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Label(jugadores_frame, text="Clase", font=('Helvetica', 11, 'bold')).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ttk.Label(jugadores_frame, text="Raza", font=('Helvetica', 11, 'bold')).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        ttk.Label(jugadores_frame, text="Nivel/XP", font=('Helvetica', 11, 'bold')).grid(row=0, column=3, padx=5, pady=5, sticky="w")
        ttk.Label(jugadores_frame, text="Acciones", font=('Helvetica', 11, 'bold')).grid(row=0, column=4, padx=5, pady=5, sticky="w")
        
        # Mostrar jugadores
        for i, jugador in enumerate(jugadores):
            ttk.Label(jugadores_frame, text=jugador.get("nombre", "")).grid(row=i+1, column=0, padx=5, pady=3, sticky="w")
            ttk.Label(jugadores_frame, text=jugador.get("clase", "")).grid(row=i+1, column=1, padx=5, pady=3, sticky="w")
            ttk.Label(jugadores_frame, text=jugador.get("raza", "")).grid(row=i+1, column=2, padx=5, pady=3, sticky="w")
            # Mostrar nivel con formato más claro e incluir experiencia
            nivel = jugador.get("nivel", 1)
            experiencia = jugador.get("experiencia", 0)
            ttk.Label(jugadores_frame, text=f"Nivel {nivel} ({experiencia} XP)").grid(row=i+1, column=3, padx=5, pady=3, sticky="w")
            
            # Botones de acción para cada jugador
            acciones_frame = ttk.Frame(jugadores_frame)
            acciones_frame.grid(row=i+1, column=4, padx=5, pady=3, sticky="w")
            
            # Personaje actual e índice para la lambda
            personaje_actual = jugador
            idx = i
            
            ttk.Button(acciones_frame, text="Ver Detalles", 
                      command=lambda p=personaje_actual: ver_detalles_personaje(p)).pack(side="left", padx=2)
            
            ttk.Button(acciones_frame, text="Editar", 
                      command=lambda p=personaje_actual, i=idx: editar_personaje(p, i)).pack(side="left", padx=2)
    
    def editar_personaje(personaje, indice):
        """Editar un personaje de la campaña"""
        # Verificar si existe el archivo del personaje
        archivo_personaje = personaje.get("archivo", "")
        if not archivo_personaje:
            messagebox.showinfo("Información", "No se encuentra la información detallada del personaje.")
            return
        
        directorio_personajes = "personajes"
        ruta_personaje = os.path.join(directorio_personajes, archivo_personaje)
        
        if not os.path.exists(ruta_personaje):
            messagebox.showinfo("Información", f"El archivo del personaje '{personaje.get('nombre', '')}' no existe.")
            return
        
        # Cargar datos completos del personaje
        try:
            with open(ruta_personaje, 'r', encoding='utf-8') as f:
                datos_personaje = json.load(f)
            
            # Guardar referencia a la campaña para actualizar después
            datos_campaña_actual = campana
            ruta_campaña_actual = ruta
            
            # Función de callback para cuando se termina de editar el personaje
            def callback_edicion():
                # Actualizar datos del personaje en la campaña
                try:
                    # Recargar el personaje editado
                    with open(ruta_personaje, 'r', encoding='utf-8') as f:
                        personaje_actualizado = json.load(f)
                    
                    # Actualizar datos básicos en la campaña
                    actualizar_personaje_en_campaña(personaje_actualizado, indice)
                    
                    # Volver a mostrar detalles de la campaña
                    mostrar_detalles_campana(root, datos_campaña_actual, ruta_campaña_actual, 
                                           callback_menu, callback_cargar_campana)
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Error al actualizar el personaje en la campaña: {str(e)}")
                    mostrar_detalles_campana(root, datos_campaña_actual, ruta_campaña_actual, 
                                           callback_menu, callback_cargar_campana)
            
            # Mostrar pantalla de edición de personaje
            from modulos.gestor_personajes import mostrar_crear_editar_personaje
            mostrar_crear_editar_personaje(root, datos_personaje, directorio_personajes, callback_edicion)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar los detalles del personaje: {str(e)}")
    
    def actualizar_personaje_en_campaña(personaje_actualizado, indice):
        """Actualiza los datos del personaje en la campaña"""
        if 0 <= indice < len(campana.get("jugadores", [])):
            # Actualizar datos básicos necesarios
            campana["jugadores"][indice].update({
                "nombre": personaje_actualizado.get("nombre", ""),
                "clase": personaje_actualizado.get("clase", ""),
                "raza": personaje_actualizado.get("raza", ""),
                "nivel": personaje_actualizado.get("nivel", 1),
                "experiencia": personaje_actualizado.get("experiencia", 0),
                "archivo": personaje_actualizado.get("archivo", ""),
                "estadisticas": personaje_actualizado.get("estadisticas", {}),
                "competencias": personaje_actualizado.get("competencias", [])
            })
            
            # Guardar los cambios en el archivo de la campaña
            try:
                with open(ruta, 'w', encoding='utf-8') as f:
                    json.dump(campana, f, ensure_ascii=False, indent=4)
                    
                # Mostrar mensaje de éxito
                messagebox.showinfo("Éxito", "Personaje actualizado correctamente en la campaña.")
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar los cambios en la campaña: {str(e)}")
    
    def ver_detalles_personaje(personaje):
        """Muestra los detalles de un personaje"""
        # Verificar si existe el archivo del personaje
        archivo_personaje = personaje.get("archivo", "")
        if not archivo_personaje:
            messagebox.showinfo("Información", "No se encuentra la información detallada del personaje.")
            return
        
        directorio_personajes = "personajes"
        ruta_personaje = os.path.join(directorio_personajes, archivo_personaje)
        
        if not os.path.exists(ruta_personaje):
            messagebox.showinfo("Información", f"El archivo del personaje '{personaje.get('nombre', '')}' no existe.")
            return
        
        # Cargar datos completos del personaje
        try:
            with open(ruta_personaje, 'r', encoding='utf-8') as f:
                datos_personaje = json.load(f)
            
            # Crear diálogo con detalles
            dialogo = tk.Toplevel(root)
            dialogo.title(f"Detalles de {personaje.get('nombre', '')}")
            dialogo.geometry("600x500")
            dialogo.transient(root)
            dialogo.grab_set()
            
            # Centrar diálogo
            dialogo.geometry("+%d+%d" % (
                root.winfo_rootx() + (root.winfo_width() // 2) - 300,
                root.winfo_rooty() + (root.winfo_height() // 2) - 250
            ))
            
            # Frame con scroll
            dialog_main = ttk.Frame(dialogo)
            dialog_main.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Resto del código para mostrar detalles del personaje (omitido para brevedad)
            # ...
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar los detalles del personaje: {str(e)}")
    
    # Botones de acción
    botones_frame = ttk.Frame(detalles_content)
    botones_frame.pack(fill="x", padx=50, pady=(20, 30))
    
    def cargar_y_volver():
        """Función para cargar la campaña y volver al menú principal"""
        if callback_cargar_campana:
            # Desenlazar eventos de scroll
            canvas_detalles.unbind_all("<MouseWheel>")
            # Destruir el frame de detalles
            detalles_frame.destroy()
            # Cargar la campaña y volver al menú principal
            callback_cargar_campana(campana, ruta)
        else:
            messagebox.showinfo("Información", "La función de cargar campaña no está disponible.")
    
    def editar_campana():
        """Función para editar la campaña actual"""
        # Importar función para editar campaña
        from editores.editar_campana import mostrar_editar_campana
        # Directorio donde se guardan las campañas
        directorio_campanas = os.path.dirname(ruta)
        # Desenlazar eventos de scroll
        canvas_detalles.unbind_all("<MouseWheel>")
        # Mostrar pantalla de edición
        mostrar_editar_campana(root, campana, ruta, directorio_campanas, 
                             callback_cargar_campana, callback_menu)
    
    def volver_lista():
        """Vuelve a la lista de campañas"""
        # Desenlazar eventos de scroll
        canvas_detalles.unbind_all("<MouseWheel>")
        # Destruir frame actual
        detalles_frame.destroy()
        # Mostrar lista de campañas
        mostrar_cargar_campana(root, os.path.dirname(ruta), callback_menu, callback_cargar_campana)
    
    ttk.Button(botones_frame, text="Continuar Partida", command=cargar_y_volver).pack(side="right", padx=5)
    ttk.Button(botones_frame, text="Editar Campaña", command=editar_campana).pack(side="right", padx=5)
    ttk.Button(botones_frame, text="Volver", command=volver_lista).pack(side="right", padx=5)
    
    # Permitir rueda del ratón para scroll
    def _on_mousewheel(event):
        canvas_detalles.yview_scroll(int(-1*(event.delta/120)), "units")
    
    canvas_detalles.bind_all("<MouseWheel>", _on_mousewheel)