#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo para editar un personaje desde la campaña en la aplicación D&D Combat Manager.
Este es un puente para utilizar el gestor de personajes existente.
"""

import os
import json
from tkinter import messagebox

def mostrar_editar_personaje(root, personaje, callback_edicion=None):
    """
    Abre el editor de personajes para editar un personaje desde la campaña
    
    Args:
        root: La ventana principal de la aplicación
        personaje: Datos básicos del personaje a editar
        callback_edicion: Función a llamar después de editar el personaje
    """
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
        
        # Mostrar pantalla de edición de personaje
        from modulos.gestor_personajes import mostrar_crear_editar_personaje
        mostrar_crear_editar_personaje(root, datos_personaje, directorio_personajes, callback_edicion)
        
    except Exception as e:
        messagebox.showerror("Error", f"Error al cargar los detalles del personaje: {str(e)}")