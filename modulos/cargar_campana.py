#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo para cargar una campaña existente en la aplicación D&D Combat Manager.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os

def mostrar_cargar_campana(root, directorio_campanas, callback_menu):
    """
    Muestra la pantalla para cargar una campaña existente
    
    Args:
        root: La ventana principal de la aplicación
        directorio_campanas: Directorio donde se guardan las campañas
        callback_menu: Función para volver al menú principal
    """
    # Ocultar frames existentes
    for widget in root.winfo_children():
        if isinstance(widget, ttk.Frame):
            widget.pack_forget()
    
    # Crear nuevo frame para cargar campaña
    cargar_campana_frame = ttk.Frame(root)
    
    # Título
    titulo = ttk.Label(cargar_campana_frame, text="Cargar Campaña", style="Title.TLabel")
    titulo.pack(pady=(20, 10))
    
    # Frame para la lista de campañas
    lista_frame = ttk.Frame(cargar_campana_frame)
    lista_frame.pack(fill="both", expand=True, padx=50, pady=10)
    
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
                        "ruta": ruta
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
            
            # Ruta para la lambda
            ruta = campana["ruta"]
            ttk.Button(acciones_frame, text="Cargar", 
                      command=lambda r=ruta: cargar_detalles_campana(r)).pack(side="left", padx=2)
    
    def cargar_archivo():
        """Abre un diálogo para seleccionar un archivo de campaña"""
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo de campaña",
            filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")],
            initialdir=directorio_campanas
        )
        
        if ruta:
            cargar_detalles_campana(ruta)
    
    def cargar_detalles_campana(ruta):
        """Carga los detalles de una campaña seleccionada"""
        try:
            with open(ruta, 'r', encoding='utf-8') as f:
                campana = json.load(f)
            
            # Mostrar detalles de la campaña
            mostrar_detalles_campana(campana, ruta)
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar la campaña: {str(e)}")
    
    def mostrar_detalles_campana(campana, ruta):
        """Muestra los detalles de una campaña cargada"""
        # Ocultar frames existentes
        for widget in root.winfo_children():
            if isinstance(widget, ttk.Frame):
                widget.pack_forget()
        
        # Crear nuevo frame para detalles
        detalles_frame = ttk.Frame(root)
        
        # Título
        titulo = ttk.Label(detalles_frame, text=f"Campaña: {campana['nombre']}", style="Title.TLabel")
        titulo.pack(pady=(20, 10))
        
        # Frame para detalles
        info_frame = ttk.Frame(detalles_frame)
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
        jugadores_titulo = ttk.Label(detalles_frame, text="Jugadores", style="Subtitle.TLabel")
        jugadores_titulo.pack(pady=(20, 10))
        
        jugadores_frame = ttk.Frame(detalles_frame)
        jugadores_frame.pack(fill="both", expand=True, padx=50, pady=5)
        
        jugadores = campana.get("jugadores", [])
        
        if not jugadores:
            ttk.Label(jugadores_frame, text="No hay jugadores en esta campaña").pack(pady=10)
        else:
            # Crear cabecera
            ttk.Label(jugadores_frame, text="Nombre", font=('Helvetica', 11, 'bold')).grid(row=0, column=0, padx=5, pady=5, sticky="w")
            ttk.Label(jugadores_frame, text="Clase", font=('Helvetica', 11, 'bold')).grid(row=0, column=1, padx=5, pady=5, sticky="w")
            ttk.Label(jugadores_frame, text="Raza", font=('Helvetica', 11, 'bold')).grid(row=0, column=2, padx=5, pady=5, sticky="w")
            ttk.Label(jugadores_frame, text="Nivel", font=('Helvetica', 11, 'bold')).grid(row=0, column=3, padx=5, pady=5, sticky="w")
            
            # Mostrar jugadores
            for i, jugador in enumerate(jugadores):
                ttk.Label(jugadores_frame, text=jugador.get("nombre", "")).grid(row=i+1, column=0, padx=5, pady=3, sticky="w")
                ttk.Label(jugadores_frame, text=jugador.get("clase", "")).grid(row=i+1, column=1, padx=5, pady=3, sticky="w")
                ttk.Label(jugadores_frame, text=jugador.get("raza", "")).grid(row=i+1, column=2, padx=5, pady=3, sticky="w")
                ttk.Label(jugadores_frame, text=str(jugador.get("nivel", 1))).grid(row=i+1, column=3, padx=5, pady=3, sticky="w")
        
        # Botones de acción
        botones_frame = ttk.Frame(detalles_frame)
        botones_frame.pack(fill="x", padx=50, pady=(20, 30))
        
        def no_implementado():
            """Función temporal para opciones no implementadas"""
            messagebox.showinfo("Información", "No implementado")
        
        ttk.Button(botones_frame, text="Continuar Partida", command=no_implementado).pack(side="right", padx=5)
        ttk.Button(botones_frame, text="Editar Campaña", command=no_implementado).pack(side="right", padx=5)
        ttk.Button(botones_frame, text="Volver", 
                  command=lambda: mostrar_cargar_campana(root, directorio_campanas, callback_menu)).pack(side="right", padx=5)
        
        # Mostrar el frame
        detalles_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Botón para cargar desde archivo
    ttk.Button(cargar_campana_frame, text="Cargar desde archivo", 
              command=cargar_archivo).pack(pady=10)
    
    # Botón para volver al menú
    ttk.Button(cargar_campana_frame, text="Volver al Menú", 
              command=callback_menu).pack(pady=(10, 30))
    
    # Mostrar el frame
    cargar_campana_frame.pack(fill="both", expand=True, padx=10, pady=10)