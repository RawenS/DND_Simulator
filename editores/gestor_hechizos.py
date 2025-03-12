#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo para la gestión de hechizos en la aplicación D&D Combat Manager.
Incluye lógica completa para manejar tiradas de ataque, salvación y daño según las reglas de D&D 5e.
"""

import tkinter as tk
from tkinter import ttk, messagebox, font, filedialog, scrolledtext
import json
import os
import re
from PIL import Image, ImageTk
import random

# Constantes para hechizos
ESCUELAS = ["Abjuración", "Adivinación", "Conjuración", "Encantamiento", 
            "Evocación", "Ilusión", "Nigromancia", "Transmutación"]

CLASES_MAGICAS = ["Bardo", "Brujo", "Clérigo", "Druida", "Explorador", 
                 "Hechicero", "Mago", "Paladín"]

ATRIBUTOS = ["Fuerza", "Destreza", "Constitución", "Inteligencia", "Sabiduría", "Carisma"]

TIEMPOS_LANZAMIENTO = [
    "1 acción", "1 acción adicional", "1 reacción", "1 minuto",
    "10 minutos", "1 hora", "8 horas", "12 horas", "24 horas", "Ritual (10 minutos)"
]

DURACIONES = [
    "Instantáneo", "1 round", "1 minuto", "10 minutos", "1 hora", 
    "8 horas", "24 horas", "7 días", "30 días", "Hasta disiparse", 
    "Concentración (hasta 1 minuto)", "Concentración (hasta 10 minutos)", 
    "Concentración (hasta 1 hora)", "Concentración (hasta 8 horas)", "Permanente"
]

ALCANCES = [
    "Personal", "Toque", "5 pies", "10 pies", "15 pies", "30 pies", "60 pies", 
    "90 pies", "120 pies", "150 pies", "300 pies", "500 pies", "1 milla", "A la vista"
]

TIPOS_DADO = ["d4", "d6", "d8", "d10", "d12", "d20"]

TIPOS_SALVACION = ["Ninguna", "Fuerza", "Destreza", "Constitución", "Inteligencia", "Sabiduría", "Carisma"]

TIPOS_ATAQUE = ["Ninguno", "Cuerpo a cuerpo", "A distancia"]

TIPOS_DAÑO = [
    "Ninguno", "Ácido", "Contundente", "Frío", "Fuego", "Fuerza", "Necrótico", 
    "Perforante", "Psíquico", "Radiante", "Relámpago", "Cortante", "Trueno", "Veneno"
]

# Directorio para almacenar datos de hechizos
DIRECTORIO_HECHIZOS = "data/hechizos"
ARCHIVO_HECHIZOS = "hechizos.json"

def inicializar_directorios():
    """Crea el directorio para hechizos si no existe"""
    if not os.path.exists(DIRECTORIO_HECHIZOS):
        os.makedirs(DIRECTORIO_HECHIZOS, exist_ok=True)

def cargar_hechizos():
    """
    Carga la base de datos de hechizos
    
    Returns:
        dict: Diccionario con todos los hechizos organizados por nivel
    """
    inicializar_directorios()
    
    # Comprobar si existe el archivo principal de hechizos
    ruta_hechizos = os.path.join(DIRECTORIO_HECHIZOS, ARCHIVO_HECHIZOS)
    if not os.path.exists(ruta_hechizos):
        # Si no existe, crear uno vacío con estructura para todos los niveles (0-9)
        hechizos_vacios = {str(nivel): [] for nivel in range(10)}
        with open(ruta_hechizos, 'w', encoding='utf-8') as f:
            json.dump(hechizos_vacios, f, ensure_ascii=False, indent=4)
        return hechizos_vacios
    
    # Cargar hechizos
    try:
        with open(ruta_hechizos, 'r', encoding='utf-8') as f:
            hechizos = json.load(f)
        
        # Asegurarse de que todos los niveles estén presentes
        for nivel in range(10):
            if str(nivel) not in hechizos:
                hechizos[str(nivel)] = []
        
        return hechizos
    except Exception as e:
        messagebox.showerror("Error", f"Error al cargar los hechizos: {str(e)}")
        return {str(nivel): [] for nivel in range(10)}

def guardar_hechizos(hechizos):
    """
    Guarda la base de datos de hechizos
    
    Args:
        hechizos (dict): Diccionario con todos los hechizos organizados por nivel
    """
    inicializar_directorios()
    
    # Guardar hechizos
    ruta_hechizos = os.path.join(DIRECTORIO_HECHIZOS, ARCHIVO_HECHIZOS)
    try:
        with open(ruta_hechizos, 'w', encoding='utf-8') as f:
            json.dump(hechizos, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Error al guardar los hechizos: {str(e)}")
        return False

def validar_formato_dados(formato):
    """
    Valida que el formato de dados sea correcto (ej: 2d6, 1d8+3, 3d4-2)
    
    Args:
        formato (str): Formato de dados a validar
    
    Returns:
        bool: True si el formato es válido, False en caso contrario
    """
    if not formato or formato.strip() == "":
        return True  # Formato vacío es válido (no hay daño/curación)
    
    # Patrón para validar formatos como 2d6, 1d8+3, 3d4-2
    patron = r'^(\d+)d(\d+)([+-]\d+)?$'
    return bool(re.match(patron, formato))

def validar_hechizo(hechizo):
    """
    Valida que los datos del hechizo sean correctos
    
    Args:
        hechizo (dict): Datos del hechizo a validar
    
    Returns:
        tuple: (bool, str) - Indicador de validez y mensaje de error si lo hay
    """
    # Validar nombre
    if not hechizo.get("nombre", "").strip():
        return False, "El hechizo debe tener un nombre."
    
    # Validar nivel
    try:
        nivel = int(hechizo.get("nivel", "0"))
        if nivel < 0 or nivel > 9:
            return False, "El nivel del hechizo debe estar entre 0 y 9."
    except (ValueError, TypeError):
        return False, "El nivel del hechizo debe ser un número entre 0 y 9."
    
    # Validar formato de daño base
    if not validar_formato_dados(hechizo.get("daño_base", "")):
        return False, "El formato de daño base debe ser NdM+K o NdM-K (ej: 2d6, 1d8+3, 3d4-2) o vacío."
    
    # Validar formato de curación base
    if not validar_formato_dados(hechizo.get("curacion_base", "")):
        return False, "El formato de curación base debe ser NdM+K o NdM-K (ej: 2d6, 1d8+3, 3d4-2) o vacío."
    
    # Validar formato de daño por nivel superior
    if not validar_formato_dados(hechizo.get("daño_nivel_superior", "")):
        return False, "El formato de daño por nivel superior debe ser NdM+K o NdM-K (ej: 2d6, 1d8+3, 3d4-2) o vacío."
    
    # Validar formato de curación por nivel superior
    if not validar_formato_dados(hechizo.get("curacion_nivel_superior", "")):
        return False, "El formato de curación por nivel superior debe ser NdM+K o NdM-K (ej: 2d6, 1d8+3, 3d4-2) o vacío."
    
    # Validar que tenga al menos una clase asignada
    if not hechizo.get("clases", []):
        return False, "Debe seleccionar al menos una clase para el hechizo."
    
    # Si todo está correcto
    return True, ""

def agregar_hechizo(hechizo):
    """
    Agrega un nuevo hechizo a la base de datos
    
    Args:
        hechizo (dict): Datos del hechizo a agregar
    
    Returns:
        tuple: (bool, str) - Indicador de éxito y mensaje
    """
    # Validar hechizo
    es_valido, mensaje = validar_hechizo(hechizo)
    if not es_valido:
        return False, mensaje
    
    # Cargar hechizos actuales
    hechizos = cargar_hechizos()
    
    # Verificar si ya existe un hechizo con el mismo nombre
    nivel = str(hechizo.get("nivel", "0"))
    for h in hechizos.get(nivel, []):
        if h.get("nombre", "").lower() == hechizo.get("nombre", "").lower():
            return False, f"Ya existe un hechizo con el nombre '{hechizo['nombre']}' en el nivel {nivel}."
    
    # Agregar hechizo
    if nivel not in hechizos:
        hechizos[nivel] = []
    hechizos[nivel].append(hechizo)
    
    # Guardar hechizos
    if guardar_hechizos(hechizos):
        return True, f"Hechizo '{hechizo['nombre']}' agregado correctamente al nivel {nivel}."
    else:
        return False, "Error al guardar el hechizo."

def editar_hechizo(hechizo_original, hechizo_nuevo):
    """
    Edita un hechizo existente
    
    Args:
        hechizo_original (dict): Datos originales del hechizo
        hechizo_nuevo (dict): Nuevos datos del hechizo
    
    Returns:
        tuple: (bool, str) - Indicador de éxito y mensaje
    """
    # Validar hechizo nuevo
    es_valido, mensaje = validar_hechizo(hechizo_nuevo)
    if not es_valido:
        return False, mensaje
    
    # Cargar hechizos actuales
    hechizos = cargar_hechizos()
    
    # Nivel original y nuevo
    nivel_original = str(hechizo_original.get("nivel", "0"))
    nivel_nuevo = str(hechizo_nuevo.get("nivel", "0"))
    
    # Verificar si el nombre ha cambiado y ya existe otro hechizo con el nuevo nombre
    if hechizo_original.get("nombre", "") != hechizo_nuevo.get("nombre", ""):
        for h in hechizos.get(nivel_nuevo, []):
            if h.get("nombre", "").lower() == hechizo_nuevo.get("nombre", "").lower():
                return False, f"Ya existe un hechizo con el nombre '{hechizo_nuevo['nombre']}' en el nivel {nivel_nuevo}."
    
    # Buscar y eliminar el hechizo original
    encontrado = False
    for i, h in enumerate(hechizos.get(nivel_original, [])):
        if h.get("nombre", "") == hechizo_original.get("nombre", ""):
            del hechizos[nivel_original][i]
            encontrado = True
            break
    
    if not encontrado:
        return False, f"No se encontró el hechizo '{hechizo_original.get('nombre', '')}' para editar."
    
    # Agregar el hechizo nuevo
    if nivel_nuevo not in hechizos:
        hechizos[nivel_nuevo] = []
    hechizos[nivel_nuevo].append(hechizo_nuevo)
    
    # Guardar hechizos
    if guardar_hechizos(hechizos):
        return True, f"Hechizo '{hechizo_nuevo['nombre']}' actualizado correctamente."
    else:
        return False, "Error al guardar los cambios del hechizo."

def eliminar_hechizo(hechizo):
    """
    Elimina un hechizo de la base de datos
    
    Args:
        hechizo (dict): Datos del hechizo a eliminar
    
    Returns:
        tuple: (bool, str) - Indicador de éxito y mensaje
    """
    # Cargar hechizos actuales
    hechizos = cargar_hechizos()
    
    # Nivel del hechizo
    nivel = str(hechizo.get("nivel", "0"))
    
    # Buscar y eliminar el hechizo
    encontrado = False
    for i, h in enumerate(hechizos.get(nivel, [])):
        if h.get("nombre", "") == hechizo.get("nombre", ""):
            del hechizos[nivel][i]
            encontrado = True
            break
    
    if not encontrado:
        return False, f"No se encontró el hechizo '{hechizo.get('nombre', '')}' para eliminar."
    
    # Guardar hechizos
    if guardar_hechizos(hechizos):
        return True, f"Hechizo '{hechizo.get('nombre', '')}' eliminado correctamente."
    else:
        return False, "Error al eliminar el hechizo."

def buscar_hechizos(filtro=None, nivel=None, escuela=None, clase=None):
    """
    Busca hechizos en la base de datos según filtros
    
    Args:
        filtro (str, optional): Texto para filtrar por nombre. Por defecto None.
        nivel (str/int, optional): Nivel para filtrar. Por defecto None.
        escuela (str, optional): Escuela para filtrar. Por defecto None.
        clase (str, optional): Clase para filtrar hechizos disponibles. Por defecto None.
    
    Returns:
        list: Lista de hechizos que cumplen con los filtros
    """
    # Cargar hechizos
    hechizos_por_nivel = cargar_hechizos()
    
    # Lista para almacenar resultados
    resultados = []
    
    # Filtrar por nivel si se especifica
    if nivel is not None:
        nivel_str = str(nivel)
        if nivel_str in hechizos_por_nivel:
            hechizos_lista = hechizos_por_nivel[nivel_str]
        else:
            return []
    else:
        # Si no se especifica nivel, incluir todos
        hechizos_lista = []
        for nivel_hechizos in hechizos_por_nivel.values():
            hechizos_lista.extend(nivel_hechizos)
    
    # Aplicar filtros adicionales
    for hechizo in hechizos_lista:
        # Filtrar por nombre
        if filtro and filtro.lower() not in hechizo.get("nombre", "").lower():
            continue
        
        # Filtrar por escuela
        if escuela and hechizo.get("escuela", "") != escuela:
            continue
        
        # Filtrar por clase
        if clase and clase not in hechizo.get("clases", []):
            continue
        
        # Si pasa todos los filtros, agregar a resultados
        resultados.append(hechizo)
    
    return resultados

def calcular_daño(formula, nivel_lanzado=None, modificador=0):
    """
    Calcula el daño o curación según una fórmula de dados
    
    Args:
        formula (str): Fórmula de dados (ej: "2d6+3")
        nivel_lanzado (int, optional): Nivel al que se lanza el hechizo. Por defecto None.
        modificador (int, optional): Modificador adicional a aplicar. Por defecto 0.
    
    Returns:
        tuple: (mínimo, promedio, máximo, resultado aleatorio)
    """
    if not formula or formula.strip() == "":
        return (0, 0, 0, 0)
    
    # Extraer componentes de la fórmula
    patron = r'^(\d+)d(\d+)([+-]\d+)?$'
    match = re.match(patron, formula)
    
    if not match:
        return (0, 0, 0, 0)
    
    num_dados = int(match.group(1))
    tipo_dado = int(match.group(2))
    mod_adicional = 0
    
    if match.group(3):
        mod_adicional = int(match.group(3))
    
    # Valores base
    minimo = num_dados + mod_adicional + modificador
    maximo = num_dados * tipo_dado + mod_adicional + modificador
    promedio = (minimo + maximo) / 2
    
    # Tirada aleatoria
    resultado = sum(random.randint(1, tipo_dado) for _ in range(num_dados)) + mod_adicional + modificador
    
    return (minimo, promedio, maximo, resultado)

def mostrar_gestor_hechizos(root, callback_volver):
    """
    Muestra la interfaz gráfica para gestionar hechizos
    
    Args:
        root: La ventana principal de la aplicación
        callback_volver: Función para volver a la pantalla anterior
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
    
    # Añadir evento para redimensionar el frame en el canvas
    def configure_frame(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.itemconfig(frame_id, width=event.width)
    
    frame_id = canvas.create_window((0, 0), window=gestor_frame, anchor="nw")
    gestor_frame.bind("<Configure>", configure_frame)
    canvas.bind("<Configure>", lambda e: configure_frame(e))
    
    # Título y descripción
    titulo = ttk.Label(gestor_frame, text="Gestor de Hechizos", style="Title.TLabel")
    titulo.pack(pady=(20, 10))
    
    descripcion = ttk.Label(
        gestor_frame, 
        text="Crea, edita y gestiona los hechizos disponibles para tus personajes.",
        wraplength=600
    )
    descripcion.pack(pady=(0, 20))
    
    # Marco para opciones de búsqueda y filtrado
    filtro_frame = ttk.LabelFrame(gestor_frame, text="Filtrar Hechizos")
    filtro_frame.pack(fill="x", padx=20, pady=10)
    
    # Configurar grid para el frame de filtro
    for i in range(4):
        filtro_frame.columnconfigure(i, weight=1)
    
    # Campo de búsqueda
    ttk.Label(filtro_frame, text="Buscar:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    busqueda_var = tk.StringVar()
    ttk.Entry(filtro_frame, textvariable=busqueda_var, width=20).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
    
    # Filtro por nivel
    ttk.Label(filtro_frame, text="Nivel:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
    nivel_filtro_var = tk.StringVar(value="Todos")
    nivel_filtro_values = ["Todos"] + [str(i) for i in range(10)]
    ttk.Combobox(filtro_frame, textvariable=nivel_filtro_var, values=nivel_filtro_values, width=10).grid(row=0, column=3, padx=5, pady=5, sticky="ew")
    
    # Filtro por escuela
    ttk.Label(filtro_frame, text="Escuela:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    escuela_filtro_var = tk.StringVar(value="Todas")
    escuela_filtro_values = ["Todas"] + ESCUELAS
    ttk.Combobox(filtro_frame, textvariable=escuela_filtro_var, values=escuela_filtro_values, width=15).grid(row=1, column=1, padx=5, pady=5, sticky="ew")
    
    # Filtro por clase
    ttk.Label(filtro_frame, text="Clase:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
    clase_filtro_var = tk.StringVar(value="Todas")
    clase_filtro_values = ["Todas"] + CLASES_MAGICAS
    ttk.Combobox(filtro_frame, textvariable=clase_filtro_var, values=clase_filtro_values, width=15).grid(row=1, column=3, padx=5, pady=5, sticky="ew")
    
    # Botón de filtrar
    ttk.Button(filtro_frame, text="Aplicar Filtros", command=lambda: actualizar_lista_hechizos()).grid(row=2, column=0, columnspan=4, padx=5, pady=10)
    
    # Marco para lista de hechizos
    lista_frame = ttk.LabelFrame(gestor_frame, text="Hechizos Disponibles")
    lista_frame.pack(fill="both", expand=True, padx=20, pady=10)
    
    # Crear Treeview para mostrar los hechizos
    columnas = ("nombre", "nivel", "escuela", "tipo", "clases")
    tree = ttk.Treeview(lista_frame, columns=columnas, show='headings', height=15)
    
    # Configurar columnas
    tree.heading("nombre", text="Nombre")
    tree.heading("nivel", text="Nivel")
    tree.heading("escuela", text="Escuela")
    tree.heading("tipo", text="Tipo")
    tree.heading("clases", text="Clases")
    
    tree.column("nombre", width=180)
    tree.column("nivel", width=50, anchor="center")
    tree.column("escuela", width=120)
    tree.column("tipo", width=100)
    tree.column("clases", width=200)
    
    # Añadir scrollbar
    scrollbar_tree = ttk.Scrollbar(lista_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar_tree.set)
    
    # Ubicar componentes
    tree.pack(side="left", fill="both", expand=True)
    scrollbar_tree.pack(side="right", fill="y")
    
    # Panel de detalles del hechizo
    detalles_frame = ttk.LabelFrame(gestor_frame, text="Detalles del Hechizo")
    detalles_frame.pack(fill="x", padx=20, pady=10)
    
    # Scrollable text para mostrar detalles
    detalles_text = scrolledtext.ScrolledText(detalles_frame, wrap=tk.WORD, width=80, height=8)
    detalles_text.pack(fill="both", expand=True, padx=5, pady=5)
    detalles_text.config(state=tk.DISABLED)
    
    # Marco para botones de acción
    botones_frame = ttk.Frame(gestor_frame)
    botones_frame.pack(fill="x", padx=20, pady=10)
    
    # Función para actualizar la lista de hechizos según los filtros
    def actualizar_lista_hechizos():
        # Limpiar lista actual
        for item in tree.get_children():
            tree.delete(item)
        
        # Obtener filtros
        texto_busqueda = busqueda_var.get()
        nivel = None if nivel_filtro_var.get() == "Todos" else nivel_filtro_var.get()
        escuela = None if escuela_filtro_var.get() == "Todas" else escuela_filtro_var.get()
        clase = None if clase_filtro_var.get() == "Todas" else clase_filtro_var.get()
        
        # Buscar hechizos
        hechizos_filtrados = buscar_hechizos(filtro=texto_busqueda, nivel=nivel, escuela=escuela, clase=clase)
        
        # Mostrar hechizos en la tabla
        for hechizo in hechizos_filtrados:
            # Determinar tipo de hechizo
            tipo = "Ataque"
            if hechizo.get("requiere_salvacion", False):
                tipo = f"Salvación ({hechizo.get('tipo_salvacion', 'Ninguna')})"
            elif hechizo.get("tipo_ataque", "Ninguno") == "Ninguno":
                tipo = "Utilidad"
            
            # Mostrar clases abreviadas
            clases_abr = []
            for c in hechizo.get("clases", []):
                if c == "Bardo": clases_abr.append("Brd")
                elif c == "Brujo": clases_abr.append("Brj")
                elif c == "Clérigo": clases_abr.append("Clr")
                elif c == "Druida": clases_abr.append("Drd")
                elif c == "Explorador": clases_abr.append("Exp")
                elif c == "Hechicero": clases_abr.append("Hch")
                elif c == "Mago": clases_abr.append("Mag")
                elif c == "Paladín": clases_abr.append("Pld")
            
            clases_texto = ", ".join(clases_abr)
            
            tree.insert("", "end", values=(
                hechizo.get("nombre", ""),
                hechizo.get("nivel", "0"),
                hechizo.get("escuela", ""),
                tipo,
                clases_texto
            ), tags=(hechizo.get("nombre", "")))
    
    # Función para mostrar detalles del hechizo seleccionado
    def mostrar_detalles(event):
        # Obtener ítem seleccionado
        seleccion = tree.selection()
        if not seleccion:
            return
        
        # Obtener valores del ítem
        item = tree.item(seleccion[0])
        nombre_hechizo = item["values"][0]
        nivel_hechizo = item["values"][1]
        
        # Buscar hechizo en la base de datos
        hechizos = cargar_hechizos()
        hechizo = None
        
        for h in hechizos.get(str(nivel_hechizo), []):
            if h.get("nombre", "") == nombre_hechizo:
                hechizo = h
                break
        
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
    
    # Vincular evento de selección
    tree.bind("<<TreeviewSelect>>", mostrar_detalles)
    
    # Función para crear un nuevo hechizo
    def nuevo_hechizo():
        mostrar_form_hechizo(None)
    
    # Función para editar hechizo seleccionado
    def editar_hechizo_seleccionado():
        seleccion = tree.selection()
        if not seleccion:
            messagebox.showinfo("Información", "Por favor, seleccione un hechizo para editar.")
            return
        
        # Obtener valores del ítem
        item = tree.item(seleccion[0])
        nombre_hechizo = item["values"][0]
        nivel_hechizo = item["values"][1]
        
        # Buscar hechizo en la base de datos
        hechizos = cargar_hechizos()
        hechizo = None
        
        for h in hechizos.get(str(nivel_hechizo), []):
            if h.get("nombre", "") == nombre_hechizo:
                hechizo = h
                break
        
        if not hechizo:
            messagebox.showinfo("Información", "No se pudo encontrar el hechizo seleccionado.")
            return
        
        # Mostrar formulario de edición
        mostrar_form_hechizo(hechizo)
    
    # Función para eliminar hechizo seleccionado
    def eliminar_hechizo_seleccionado():
        seleccion = tree.selection()
        if not seleccion:
            messagebox.showinfo("Información", "Por favor, seleccione un hechizo para eliminar.")
            return
        
        # Obtener valores del ítem
        item = tree.item(seleccion[0])
        nombre_hechizo = item["values"][0]
        nivel_hechizo = item["values"][1]
        
        # Confirmar eliminación
        if not messagebox.askyesno("Confirmar", f"¿Está seguro que desea eliminar el hechizo '{nombre_hechizo}'?"):
            return
        
        # Buscar hechizo en la base de datos
        hechizos = cargar_hechizos()
        hechizo = None
        
        for h in hechizos.get(str(nivel_hechizo), []):
            if h.get("nombre", "") == nombre_hechizo:
                hechizo = h
                break
        
        if not hechizo:
            messagebox.showinfo("Información", "No se pudo encontrar el hechizo seleccionado.")
            return
        
        # Eliminar hechizo
        exito, mensaje = eliminar_hechizo(hechizo)
        messagebox.showinfo("Información", mensaje)
        
        if exito:
            # Actualizar lista
            actualizar_lista_hechizos()
    
    # Funciones para importar/exportar hechizos
    def importar_hechizos():
        ruta_archivo = filedialog.askopenfilename(
            title="Importar Hechizos",
            filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")],
            initialdir=DIRECTORIO_HECHIZOS
        )
        
        if not ruta_archivo:
            return
        
        try:
            # Leer archivo
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                nuevos_hechizos = json.load(f)
            
            # Validar estructura
            if not isinstance(nuevos_hechizos, dict):
                messagebox.showwarning("Advertencia", "El archivo no tiene el formato correcto.")
                return
            
            # Cargar hechizos actuales
            hechizos_actuales = cargar_hechizos()
            
            # Contador de hechizos importados
            contador = 0
            
            # Recorrer nuevos hechizos
            for nivel, lista_hechizos in nuevos_hechizos.items():
                if not nivel.isdigit() or int(nivel) < 0 or int(nivel) > 9:
                    continue
                    
                if nivel not in hechizos_actuales:
                    hechizos_actuales[nivel] = []
                    
                for hechizo in lista_hechizos:
                    # Verificar si ya existe
                    existe = False
                    for h in hechizos_actuales[nivel]:
                        if h.get("nombre", "") == hechizo.get("nombre", ""):
                            existe = True
                            break
                    
                    if not existe:
                        hechizos_actuales[nivel].append(hechizo)
                        contador += 1
            
            # Guardar hechizos actualizados
            if guardar_hechizos(hechizos_actuales):
                messagebox.showinfo("Éxito", f"Se importaron {contador} hechizos correctamente.")
                # Actualizar lista
                actualizar_lista_hechizos()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al importar hechizos: {str(e)}")
    
    def exportar_hechizos():
        ruta_archivo = filedialog.asksaveasfilename(
            title="Exportar Hechizos",
            defaultextension=".json",
            filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")],
            initialdir=DIRECTORIO_HECHIZOS
        )
        
        if not ruta_archivo:
            return
        
        try:
            # Cargar hechizos
            hechizos = cargar_hechizos()
            
            # Guardar en archivo
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                json.dump(hechizos, f, ensure_ascii=False, indent=4)
            
            messagebox.showinfo("Éxito", "Hechizos exportados correctamente.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar hechizos: {str(e)}")
    
    # Función para mostrar el formulario de hechizo (crear/editar)
    def mostrar_form_hechizo(hechizo_actual):
        # Determinar modo
        modo = "Editar" if hechizo_actual else "Crear"
        
        # Crear ventana de diálogo
        dialogo = tk.Toplevel(root)
        dialogo.title(f"{modo} Hechizo")
        dialogo.geometry("800x650")
        dialogo.transient(root)
        dialogo.grab_set()
        
        # Centrar diálogo
        dialogo.geometry("+%d+%d" % (
            root.winfo_rootx() + (root.winfo_width() // 2) - 400,
            root.winfo_rooty() + (root.winfo_height() // 2) - 325
        ))
        
        # Contenedor principal con scroll
        dialog_main = ttk.Frame(dialogo)
        dialog_main.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Canvas con scroll
        dialog_canvas = tk.Canvas(dialog_main)
        dialog_scrollbar = ttk.Scrollbar(dialog_main, orient="vertical", command=dialog_canvas.yview)
        dialog_frame = ttk.Frame(dialog_canvas)
        
        dialog_canvas.configure(yscrollcommand=dialog_scrollbar.set)
        dialog_canvas.pack(side="left", fill="both", expand=True)
        dialog_scrollbar.pack(side="right", fill="y")
        
        dialog_canvas_id = dialog_canvas.create_window((0, 0), window=dialog_frame, anchor="nw")
        
        def configure_dialog_frame(event):
            dialog_canvas.configure(scrollregion=dialog_canvas.bbox("all"))
            dialog_canvas.itemconfig(dialog_canvas_id, width=event.width)
        
        dialog_frame.bind("<Configure>", configure_dialog_frame)
        dialog_canvas.bind("<Configure>", lambda e: configure_dialog_frame(e))
        
        # Título
        ttk.Label(dialog_frame, text=f"{modo} Hechizo", font=('Helvetica', 16, 'bold')).pack(pady=(10, 20))
        
        # Notebook para organizar información
        notebook = ttk.Notebook(dialog_frame)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # ----- PESTAÑA INFORMACIÓN BÁSICA -----
        tab_basico = ttk.Frame(notebook)
        notebook.add(tab_basico, text="Información Básica")
        
        # Configurar grid
        for i in range(2):
            tab_basico.columnconfigure(i, weight=1)
        
        # Nombre del hechizo
        ttk.Label(tab_basico, text="Nombre:").grid(row=0, column=0, sticky="w", padx=10, pady=10)
        nombre_var = tk.StringVar(value=hechizo_actual.get("nombre", "") if hechizo_actual else "")
        ttk.Entry(tab_basico, textvariable=nombre_var, width=40).grid(row=0, column=1, sticky="ew", padx=10, pady=10)
        
        # Nivel
        ttk.Label(tab_basico, text="Nivel:").grid(row=1, column=0, sticky="w", padx=10, pady=10)
        nivel_var = tk.StringVar(value=str(hechizo_actual.get("nivel", "0")) if hechizo_actual else "0")
        nivel_combo = ttk.Combobox(tab_basico, textvariable=nivel_var, values=[str(i) for i in range(10)], width=5)
        nivel_combo.grid(row=1, column=1, sticky="w", padx=10, pady=10)
        
        # Escuela
        ttk.Label(tab_basico, text="Escuela:").grid(row=2, column=0, sticky="w", padx=10, pady=10)
        escuela_var = tk.StringVar(value=hechizo_actual.get("escuela", "") if hechizo_actual else "")
        ttk.Combobox(tab_basico, textvariable=escuela_var, values=ESCUELAS, width=20).grid(row=2, column=1, sticky="w", padx=10, pady=10)
        
        # Tiempo de lanzamiento
        ttk.Label(tab_basico, text="Tiempo de lanzamiento:").grid(row=3, column=0, sticky="w", padx=10, pady=10)
        tiempo_var = tk.StringVar(value=hechizo_actual.get("tiempo_lanzamiento", "1 acción") if hechizo_actual else "1 acción")
        ttk.Combobox(tab_basico, textvariable=tiempo_var, values=TIEMPOS_LANZAMIENTO, width=20).grid(row=3, column=1, sticky="w", padx=10, pady=10)
        
        # Alcance
        ttk.Label(tab_basico, text="Alcance:").grid(row=4, column=0, sticky="w", padx=10, pady=10)
        alcance_var = tk.StringVar(value=hechizo_actual.get("alcance", "30 pies") if hechizo_actual else "30 pies")
        ttk.Combobox(tab_basico, textvariable=alcance_var, values=ALCANCES, width=20).grid(row=4, column=1, sticky="w", padx=10, pady=10)
        
        # Componentes
        ttk.Label(tab_basico, text="Componentes:").grid(row=5, column=0, sticky="w", padx=10, pady=10)
        componentes_var = tk.StringVar(value=hechizo_actual.get("componentes", "V, S") if hechizo_actual else "V, S")
        ttk.Entry(tab_basico, textvariable=componentes_var, width=40).grid(row=5, column=1, sticky="ew", padx=10, pady=10)
        
        # Duración
        ttk.Label(tab_basico, text="Duración:").grid(row=6, column=0, sticky="w", padx=10, pady=10)
        duracion_var = tk.StringVar(value=hechizo_actual.get("duracion", "Instantáneo") if hechizo_actual else "Instantáneo")
        ttk.Combobox(tab_basico, textvariable=duracion_var, values=DURACIONES, width=30).grid(row=6, column=1, sticky="w", padx=10, pady=10)
        
        # Descripción
        ttk.Label(tab_basico, text="Descripción:").grid(row=7, column=0, sticky="nw", padx=10, pady=10)
        descripcion_text = scrolledtext.ScrolledText(tab_basico, wrap=tk.WORD, width=40, height=8)
        descripcion_text.grid(row=7, column=1, sticky="ew", padx=10, pady=10)
        if hechizo_actual:
            descripcion_text.insert("1.0", hechizo_actual.get("descripcion", ""))
        
        # ----- PESTAÑA ATAQUES Y SALVACIONES -----
        tab_ataque = ttk.Frame(notebook)
        notebook.add(tab_ataque, text="Ataques y Salvaciones")
        
        # Configurar grid
        for i in range(2):
            tab_ataque.columnconfigure(i, weight=1)
        
        # Tipo de ataque
        ttk.Label(tab_ataque, text="Tipo de ataque:").grid(row=0, column=0, sticky="w", padx=10, pady=10)
        tipo_ataque_var = tk.StringVar(value=hechizo_actual.get("tipo_ataque", "Ninguno") if hechizo_actual else "Ninguno")
        ttk.Combobox(tab_ataque, textvariable=tipo_ataque_var, values=TIPOS_ATAQUE, width=20).grid(row=0, column=1, sticky="w", padx=10, pady=10)
        
        # Salvación
        ttk.Label(tab_ataque, text="Requiere tirada de salvación:").grid(row=1, column=0, sticky="w", padx=10, pady=10)
        requiere_salv_var = tk.BooleanVar(value=hechizo_actual.get("requiere_salvacion", False) if hechizo_actual else False)
        ttk.Checkbutton(tab_ataque, variable=requiere_salv_var).grid(row=1, column=1, sticky="w", padx=10, pady=10)
        
        # Tipo de salvación
        ttk.Label(tab_ataque, text="Tipo de salvación:").grid(row=2, column=0, sticky="w", padx=10, pady=10)
        tipo_salv_var = tk.StringVar(value=hechizo_actual.get("tipo_salvacion", "Destreza") if hechizo_actual else "Destreza")
        tipo_salv_combo = ttk.Combobox(tab_ataque, textvariable=tipo_salv_var, values=TIPOS_SALVACION, width=20)
        tipo_salv_combo.grid(row=2, column=1, sticky="w", padx=10, pady=10)
        
        # Efecto de salvación exitosa
        ttk.Label(tab_ataque, text="Efecto en salvación exitosa:").grid(row=3, column=0, sticky="w", padx=10, pady=10)
        efecto_salv_var = tk.StringVar(value=hechizo_actual.get("efecto_salvacion", "Mitad de daño") if hechizo_actual else "Mitad de daño")
        efecto_salv_combo = ttk.Combobox(tab_ataque, textvariable=efecto_salv_var, 
                                        values=["Ningún daño", "Mitad de daño", "Efecto reducido"], width=20)
        efecto_salv_combo.grid(row=3, column=1, sticky="w", padx=10, pady=10)
        
        # Habilitar/deshabilitar campos según la opción de salvación
        def actualizar_campos_salvacion():
            if requiere_salv_var.get():
                tipo_salv_combo.config(state="readonly")
                efecto_salv_combo.config(state="readonly")
            else:
                tipo_salv_combo.config(state="disabled")
                efecto_salv_combo.config(state="disabled")
        
        # Vincular función a cambios en la opción de salvación
        requiere_salv_var.trace_add("write", lambda *args: actualizar_campos_salvacion())
        
        # Inicializar estado de campos
        actualizar_campos_salvacion()
        
        # ----- PESTAÑA DAÑO Y CURACIÓN -----
        tab_daño = ttk.Frame(notebook)
        notebook.add(tab_daño, text="Daño y Curación")
        
        # Configurar grid
        for i in range(2):
            tab_daño.columnconfigure(i, weight=1)
        
        # Daño base
        ttk.Label(tab_daño, text="Daño base:").grid(row=0, column=0, sticky="w", padx=10, pady=10)
        daño_base_var = tk.StringVar(value=hechizo_actual.get("daño_base", "") if hechizo_actual else "")
        ttk.Entry(tab_daño, textvariable=daño_base_var, width=20).grid(row=0, column=1, sticky="w", padx=10, pady=10)
        ttk.Label(tab_daño, text="(ej: 2d6, 1d8+3)").grid(row=0, column=2, sticky="w", padx=0, pady=10)
        
        # Tipo de daño
        ttk.Label(tab_daño, text="Tipo de daño:").grid(row=1, column=0, sticky="w", padx=10, pady=10)
        tipo_daño_var = tk.StringVar(value=hechizo_actual.get("tipo_daño", "Fuego") if hechizo_actual else "Fuego")
        ttk.Combobox(tab_daño, textvariable=tipo_daño_var, values=TIPOS_DAÑO, width=20).grid(row=1, column=1, sticky="w", padx=10, pady=10)
        
        # Curación base
        ttk.Label(tab_daño, text="Curación base:").grid(row=2, column=0, sticky="w", padx=10, pady=10)
        curacion_base_var = tk.StringVar(value=hechizo_actual.get("curacion_base", "") if hechizo_actual else "")
        ttk.Entry(tab_daño, textvariable=curacion_base_var, width=20).grid(row=2, column=1, sticky="w", padx=10, pady=10)
        ttk.Label(tab_daño, text="(ej: 1d8+3)").grid(row=2, column=2, sticky="w", padx=0, pady=10)
        
        # Daño a nivel superior
        ttk.Label(tab_daño, text="Daño adicional por nivel:").grid(row=3, column=0, sticky="w", padx=10, pady=10)
        daño_nivel_var = tk.StringVar(value=hechizo_actual.get("daño_nivel_superior", "") if hechizo_actual else "")
        ttk.Entry(tab_daño, textvariable=daño_nivel_var, width=20).grid(row=3, column=1, sticky="w", padx=10, pady=10)
        ttk.Label(tab_daño, text="(ej: 1d6)").grid(row=3, column=2, sticky="w", padx=0, pady=10)
        
        # Curación a nivel superior
        ttk.Label(tab_daño, text="Curación adicional por nivel:").grid(row=4, column=0, sticky="w", padx=10, pady=10)
        curacion_nivel_var = tk.StringVar(value=hechizo_actual.get("curacion_nivel_superior", "") if hechizo_actual else "")
        ttk.Entry(tab_daño, textvariable=curacion_nivel_var, width=20).grid(row=4, column=1, sticky="w", padx=10, pady=10)
        ttk.Label(tab_daño, text="(ej: 1d4)").grid(row=4, column=2, sticky="w", padx=0, pady=10)
        
        # Simulador de daño/curación
        ttk.Label(tab_daño, text="Simulador de daño/curación:", font=('Helvetica', 11, 'bold')).grid(row=5, column=0, columnspan=3, sticky="w", padx=10, pady=(20, 10))
        
        # Marco para simulador
        sim_frame = ttk.Frame(tab_daño)
        sim_frame.grid(row=6, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
        
        # Nivel de lanzamiento
        ttk.Label(sim_frame, text="Nivel de lanzamiento:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        nivel_lanz_var = tk.StringVar(value="1")
        ttk.Combobox(sim_frame, textvariable=nivel_lanz_var, values=[str(i) for i in range(1, 10)], width=5).grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # Modificador de atributo
        ttk.Label(sim_frame, text="Modificador de atributo:").grid(row=0, column=2, sticky="w", padx=(20, 5), pady=5)
        mod_attr_var = tk.StringVar(value="3")
        ttk.Spinbox(sim_frame, from_=0, to=10, textvariable=mod_attr_var, width=5).grid(row=0, column=3, sticky="w", padx=5, pady=5)
        
        # Resultados
        ttk.Label(sim_frame, text="Resultados:", font=('Helvetica', 10, 'bold')).grid(row=1, column=0, columnspan=4, sticky="w", padx=5, pady=(10, 5))
        
        # Marco para resultados
        res_frame = ttk.LabelFrame(sim_frame, text="Simulación")
        res_frame.grid(row=2, column=0, columnspan=4, sticky="ew", padx=5, pady=5)
        
        # Variables para resultados
        dc_var = tk.StringVar(value="")
        ataque_var = tk.StringVar(value="")
        daño_min_var = tk.StringVar(value="")
        daño_max_var = tk.StringVar(value="")
        daño_prom_var = tk.StringVar(value="")
        curacion_min_var = tk.StringVar(value="")
        curacion_max_var = tk.StringVar(value="")
        curacion_prom_var = tk.StringVar(value="")
        
        # Mostrar CD y bono de ataque
        ttk.Label(res_frame, text="CD de Salvación:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Label(res_frame, textvariable=dc_var, width=5).grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(res_frame, text="Bono de Ataque:").grid(row=0, column=2, sticky="w", padx=(20, 5), pady=2)
        ttk.Label(res_frame, textvariable=ataque_var, width=5).grid(row=0, column=3, sticky="w", padx=5, pady=2)
        
        # Mostrar daño
        ttk.Label(res_frame, text="Daño:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        ttk.Label(res_frame, text="Mín:").grid(row=1, column=1, sticky="e", padx=5, pady=2)
        ttk.Label(res_frame, textvariable=daño_min_var, width=5).grid(row=1, column=2, sticky="w", padx=0, pady=2)
        
        ttk.Label(res_frame, text="Máx:").grid(row=1, column=3, sticky="e", padx=5, pady=2)
        ttk.Label(res_frame, textvariable=daño_max_var, width=5).grid(row=1, column=4, sticky="w", padx=0, pady=2)
        
        ttk.Label(res_frame, text="Prom:").grid(row=1, column=5, sticky="e", padx=5, pady=2)
        ttk.Label(res_frame, textvariable=daño_prom_var, width=5).grid(row=1, column=6, sticky="w", padx=0, pady=2)
        
        # Mostrar curación
        ttk.Label(res_frame, text="Curación:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        ttk.Label(res_frame, text="Mín:").grid(row=2, column=1, sticky="e", padx=5, pady=2)
        ttk.Label(res_frame, textvariable=curacion_min_var, width=5).grid(row=2, column=2, sticky="w", padx=0, pady=2)
        
        ttk.Label(res_frame, text="Máx:").grid(row=2, column=3, sticky="e", padx=5, pady=2)
        ttk.Label(res_frame, textvariable=curacion_max_var, width=5).grid(row=2, column=4, sticky="w", padx=0, pady=2)
        
        ttk.Label(res_frame, text="Prom:").grid(row=2, column=5, sticky="e", padx=5, pady=2)
        ttk.Label(res_frame, textvariable=curacion_prom_var, width=5).grid(row=2, column=6, sticky="w", padx=0, pady=2)
        
        # Botón para simular
        def simular():
            try:
                # Obtener valores
                nivel_lanzamiento = int(nivel_lanz_var.get())
                mod_atributo = int(mod_attr_var.get())
                
                # Calcular CD y bono de ataque
                bono_comp = 2 + ((nivel_lanzamiento - 1) // 4)  # Bonificador de competencia según nivel
                
                dc = 8 + bono_comp + mod_atributo
                dc_var.set(str(dc))
                
                ataque = bono_comp + mod_atributo
                ataque_var.set(f"+{ataque}")
                
                # Calcular daño
                daño_base = daño_base_var.get()
                daño_nivel = daño_nivel_var.get()
                
                # Si hay daño nivel superior y el nivel de lanzamiento > nivel del hechizo
                nivel_hechizo = int(nivel_var.get())
                niveles_adicionales = max(0, nivel_lanzamiento - nivel_hechizo)
                
                # Calcular daño base
                daño_min, daño_prom, daño_max, _ = calcular_daño(daño_base, modificador=mod_atributo if daño_base else 0)
                
                # Añadir daño por nivel superior si aplica
                if niveles_adicionales > 0 and daño_nivel:
                    for _ in range(niveles_adicionales):
                        dmin, dprom, dmax, _ = calcular_daño(daño_nivel)
                        daño_min += dmin
                        daño_prom += dprom
                        daño_max += dmax
                
                # Mostrar resultados de daño
                daño_min_var.set(str(daño_min))
                daño_max_var.set(str(daño_max))
                daño_prom_var.set(str(int(daño_prom)))
                
                # Calcular curación
                curacion_base = curacion_base_var.get()
                curacion_nivel = curacion_nivel_var.get()
                
                # Calcular curación base
                curacion_min, curacion_prom, curacion_max, _ = calcular_daño(curacion_base, modificador=mod_atributo if curacion_base else 0)
                
                # Añadir curación por nivel superior si aplica
                if niveles_adicionales > 0 and curacion_nivel:
                    for _ in range(niveles_adicionales):
                        cmin, cprom, cmax, _ = calcular_daño(curacion_nivel)
                        curacion_min += cmin
                        curacion_prom += cprom
                        curacion_max += cmax
                
                # Mostrar resultados de curación
                curacion_min_var.set(str(curacion_min))
                curacion_max_var.set(str(curacion_max))
                curacion_prom_var.set(str(int(curacion_prom)))
                
            except Exception as e:
                messagebox.showerror("Error", f"Error en la simulación: {str(e)}")
        
        ttk.Button(sim_frame, text="Simular", command=simular).grid(row=3, column=0, columnspan=4, padx=5, pady=10)
        
        # ----- PESTAÑA CLASES -----
        tab_clases = ttk.Frame(notebook)
        notebook.add(tab_clases, text="Clases")
        
        # Título
        ttk.Label(tab_clases, text="Clases que pueden usar este hechizo:", font=('Helvetica', 12, 'bold')).pack(pady=(10, 20))
        
        # Variables para checkboxes de clases
        clase_vars = {}
        clases_seleccionadas = hechizo_actual.get("clases", []) if hechizo_actual else []
        
        # Frame para checkboxes
        clases_frame = ttk.Frame(tab_clases)
        clases_frame.pack(fill="x", padx=20, pady=10)
        
        # Crear checkboxes
        for i, clase in enumerate(CLASES_MAGICAS):
            fila = i % 4
            columna = i // 4
            clase_vars[clase] = tk.BooleanVar(value=clase in clases_seleccionadas)
            ttk.Checkbutton(clases_frame, text=clase, variable=clase_vars[clase]).grid(row=fila, column=columna, sticky="w", padx=10, pady=5)
        
        # Botones para seleccionar/deseleccionar todas
        botones_clases = ttk.Frame(tab_clases)
        botones_clases.pack(fill="x", padx=20, pady=10)
        
        def seleccionar_todas_clases():
            for var in clase_vars.values():
                var.set(True)
        
        def deseleccionar_todas_clases():
            for var in clase_vars.values():
                var.set(False)
        
        ttk.Button(botones_clases, text="Seleccionar Todas", command=seleccionar_todas_clases).pack(side="left", padx=5)
        ttk.Button(botones_clases, text="Deseleccionar Todas", command=deseleccionar_todas_clases).pack(side="left", padx=5)
        
        # ----- BOTONES DE ACCIÓN -----
        botones_dialog = ttk.Frame(dialog_frame)
        botones_dialog.pack(fill="x", padx=10, pady=(20, 10))
        
        def guardar_hechizo_form():
            # Recopilar datos del formulario
            nuevo_hechizo = {
                "nombre": nombre_var.get().strip(),
                "nivel": int(nivel_var.get()),
                "escuela": escuela_var.get(),
                "tiempo_lanzamiento": tiempo_var.get(),
                "alcance": alcance_var.get(),
                "componentes": componentes_var.get(),
                "duracion": duracion_var.get(),
                "descripcion": descripcion_text.get("1.0", "end-1c"),
                "tipo_ataque": tipo_ataque_var.get(),
                "requiere_salvacion": requiere_salv_var.get(),
                "tipo_salvacion": tipo_salv_var.get(),
                "efecto_salvacion": efecto_salv_var.get(),
                "daño_base": daño_base_var.get().strip(),
                "tipo_daño": tipo_daño_var.get(),
                "curacion_base": curacion_base_var.get().strip(),
                "daño_nivel_superior": daño_nivel_var.get().strip(),
                "curacion_nivel_superior": curacion_nivel_var.get().strip(),
                "clases": [clase for clase, var in clase_vars.items() if var.get()]
            }
            
            # Validar y guardar
            if modo == "Crear":
                exito, mensaje = agregar_hechizo(nuevo_hechizo)
            else:
                exito, mensaje = editar_hechizo(hechizo_actual, nuevo_hechizo)
            
            # Mostrar mensaje
            if exito:
                messagebox.showinfo("Éxito", mensaje)
                # Cerrar diálogo
                dialogo.destroy()
                # Actualizar lista
                actualizar_lista_hechizos()
            else:
                messagebox.showwarning("Advertencia", mensaje)
        
        ttk.Button(botones_dialog, text="Guardar", command=guardar_hechizo_form).pack(side="right", padx=5)
        ttk.Button(botones_dialog, text="Cancelar", command=dialogo.destroy).pack(side="right", padx=5)
        
        # Permitir rueda del ratón para scroll
        def _on_mousewheel(event):
            dialog_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        dialog_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Cuando se cierra el diálogo, desenlazar eventos
        def on_dialog_close():
            dialog_canvas.unbind_all("<MouseWheel>")
            dialogo.destroy()
        
        dialogo.protocol("WM_DELETE_WINDOW", on_dialog_close)
    
    # Función para volver al menú anterior
    def volver():
        """Vuelve a la pantalla anterior"""
        # Desenlazar eventos de scroll
        canvas.unbind_all("<MouseWheel>")
        # Destruir el contenedor principal
        main_container.destroy()
        # Volver a la pantalla anterior
        callback_volver()
    
    # Botones principales
    ttk.Button(botones_frame, text="Nuevo Hechizo", command=nuevo_hechizo).pack(side="left", padx=5)
    ttk.Button(botones_frame, text="Editar Hechizo", command=editar_hechizo_seleccionado).pack(side="left", padx=5)
    ttk.Button(botones_frame, text="Eliminar Hechizo", command=eliminar_hechizo_seleccionado).pack(side="left", padx=5)
    ttk.Button(botones_frame, text="Importar Hechizos", command=importar_hechizos).pack(side="left", padx=5)
    ttk.Button(botones_frame, text="Exportar Hechizos", command=exportar_hechizos).pack(side="left", padx=5)
    ttk.Button(botones_frame, text="Volver", command=volver).pack(side="right", padx=5)
    
    # Inicializar lista
    actualizar_lista_hechizos()
    
    # Añadir atajos de teclado para navegación con scroll
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    canvas.bind_all("<MouseWheel>", _on_mousewheel)

def mostrar_selector_hechizos_para_personaje(root, clase, callback_seleccion):
    """
    Muestra un selector de hechizos disponibles para una clase específica
    
    Args:
        root: La ventana principal de la aplicación
        clase (str): Clase del personaje para filtrar hechizos disponibles
        callback_seleccion: Función a llamar con los hechizos seleccionados
    """
    # Verificar si hay hechizos disponibles
    hechizos = cargar_hechizos()
    hay_hechizos = False
    
    for nivel_hechizos in hechizos.values():
        for hechizo in nivel_hechizos:
            if clase in hechizo.get("clases", []):
                hay_hechizos = True
                break
        if hay_hechizos:
            break
    
    if not hay_hechizos:
        messagebox.showinfo("Información", 
                          f"No hay hechizos disponibles para la clase {clase}. Puede crear hechizos en el Gestor de Hechizos.")
        callback_seleccion([])  # Volver sin seleccionar nada
        return
    
    # Crear ventana de diálogo
    dialogo = tk.Toplevel(root)
    dialogo.title(f"Seleccionar Hechizos para {clase}")
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
    ttk.Label(dialog_main, text=f"Seleccionar Hechizos para {clase}", font=('Helvetica', 16, 'bold')).pack(pady=(0, 10))
    
    # Frame para filtros
    filtro_frame = ttk.Frame(dialog_main)
    filtro_frame.pack(fill="x", padx=5, pady=5)
    
    # Filtro por nivel
    ttk.Label(filtro_frame, text="Nivel:").pack(side="left", padx=5)
    nivel_filtro_var = tk.StringVar(value="Todos")
    nivel_filtro_values = ["Todos"] + [str(i) for i in range(10)]
    ttk.Combobox(filtro_frame, textvariable=nivel_filtro_var, values=nivel_filtro_values, width=10).pack(side="left", padx=5)
    
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
    tree.column("tipo", width=120)
    
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
    
    # Diccionario para mantener el estado de selección
    seleccion = {}
    
    # Función para actualizar la lista de hechizos según los filtros
    def actualizar_lista_hechizos():
        # Limpiar lista actual
        for item in tree.get_children():
            tree.delete(item)
        
        # Obtener filtros
        nivel = None if nivel_filtro_var.get() == "Todos" else nivel_filtro_var.get()
        nombre = nombre_filtro_var.get()
        
        # Buscar hechizos
        hechizos_filtrados = buscar_hechizos(filtro=nombre, nivel=nivel, clase=clase)
        
        # Mostrar hechizos en la tabla
        for hechizo in hechizos_filtrados:
            # Determinar tipo de hechizo
            tipo = "Ataque"
            if hechizo.get("requiere_salvacion", False):
                tipo = f"Salvación ({hechizo.get('tipo_salvacion', 'Ninguna')})"
            elif hechizo.get("tipo_ataque", "Ninguno") == "Ninguno":
                tipo = "Utilidad"
            
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
        hechizos_db = cargar_hechizos()
        hechizo = None
        
        for h in hechizos_db.get(str(nivel_hechizo), []):
            if h.get("nombre", "") == nombre_hechizo:
                hechizo = h
                break
        
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
    
    # Función para completar la selección
    def completar_seleccion():
        # Obtener hechizos seleccionados
        hechizos_seleccionados = []
        
        for hechizo_id, seleccionado in seleccion.items():
            if seleccionado:
                # Extraer nombre y nivel del ID
                nombre, nivel = hechizo_id.rsplit("_", 1)
                
                # Buscar hechizo completo
                for h in hechizos.get(nivel, []):
                    if h.get("nombre", "") == nombre:
                        hechizos_seleccionados.append(h)
                        break
        
        # Cerrar diálogo
        dialogo.destroy()
        
        # Llamar a callback con los hechizos seleccionados
        callback_seleccion(hechizos_seleccionados)
    
    # Botones de acción
    ttk.Button(botones_frame, text="Seleccionar", command=completar_seleccion).pack(side="right", padx=5)
    ttk.Button(botones_frame, text="Cancelar", command=lambda: (dialogo.destroy(), callback_seleccion([]))).pack(side="right", padx=5)
    
    # Inicializar lista
    actualizar_lista_hechizos()

# Crear hechizos de ejemplo
def crear_hechizos_ejemplo():
    """Crea y añade hechizos de ejemplo a la base de datos"""
    hechizos_ejemplo = [
        {
            "nombre": "Palabra Sagrada",
            "nivel": 7,
            "escuela": "Evocación",
            "tiempo_lanzamiento": "1 acción adicional",
            "alcance": "30 pies",
            "componentes": "V",
            "duracion": "Instantáneo",
            "tipo_ataque": "Ninguno",
            "requiere_salvacion": True,
            "tipo_salvacion": "Carisma",
            "efecto_salvacion": "Ningún daño",
            "daño_base": "",
            "tipo_daño": "Ninguno",
            "curacion_base": "",
            "daño_nivel_superior": "",
            "curacion_nivel_superior": "",
            "clases": ["Clérigo"],
            "descripcion": "Pronuncias una palabra sagrada, imbuida de poder que puede obligar a aquellos que te escuchan a arrodillarse ante ti. Cualquier criatura que elijas y que pueda oírte y esté a 30 pies de ti debe realizar una tirada de salvación de Carisma. Dependiendo de los puntos de golpe actuales de la criatura, esto produce diferentes efectos:\n- 50 PG o menos: sordo durante 1 minuto\n- 40 PG o menos: sordo y cegado durante 10 minutos\n- 30 PG o menos: sordo, cegado y aturdido durante 1 hora\n- 20 PG o menos: muerto instantáneamente\nCualquier celestial es inmune a este hechizo."
        },
        {
            "nombre": "Bola de Fuego",
            "nivel": 3,
            "escuela": "Evocación",
            "tiempo_lanzamiento": "1 acción",
            "alcance": "150 pies",
            "componentes": "V, S, M (una pequeña bola de guano de murciélago y azufre)",
            "duracion": "Instantáneo",
            "tipo_ataque": "Ninguno",
            "requiere_salvacion": True,
            "tipo_salvacion": "Destreza",
            "efecto_salvacion": "Mitad de daño",
            "daño_base": "8d6",
            "tipo_daño": "Fuego",
            "curacion_base": "",
            "daño_nivel_superior": "1d6",
            "curacion_nivel_superior": "",
            "clases": ["Mago", "Hechicero"],
            "descripcion": "Un rayo brillante se dispara desde tu dedo índice hasta un punto que elijas dentro del alcance, para después explotar en llamas con un sordo rugido. Todas las criaturas en una esfera de 20 pies de radio centrada en ese punto deben hacer una tirada de salvación de Destreza. Un objetivo recibe 8d6 de daño por fuego si falla la tirada, o la mitad de daño si tiene éxito.\nEl fuego se extiende rodeando esquinas. Prende fuego a objetos inflamables en el área que no estén siendo llevados o transportados."
        },
        {
            "nombre": "Curar Heridas",
            "nivel": 1,
            "escuela": "Evocación",
            "tiempo_lanzamiento": "1 acción",
            "alcance": "Toque",
            "componentes": "V, S",
            "duracion": "Instantáneo",
            "tipo_ataque": "Ninguno",
            "requiere_salvacion": False,
            "tipo_salvacion": "Ninguna",
            "efecto_salvacion": "Ningún daño",
            "daño_base": "",
            "tipo_daño": "Ninguno",
            "curacion_base": "1d8+4",
            "daño_nivel_superior": "",
            "curacion_nivel_superior": "1d8",
            "clases": ["Bardo", "Clérigo", "Druida", "Paladín", "Explorador"],
            "descripcion": "Una criatura que tocas recupera un número de puntos de golpe igual a 1d8 + tu modificador de característica de lanzamiento de conjuros. Este hechizo no tiene efecto sobre no muertos o constructos.\nA niveles superiores: Cuando lanzas este hechizo usando un espacio de conjuro de nivel 2 o superior, la cantidad de curación aumenta en 1d8 por cada nivel por encima de 1."
        },
        {
            "nombre": "Mano Mágica",
            "nivel": 0,
            "escuela": "Conjuración",
            "tiempo_lanzamiento": "1 acción",
            "alcance": "30 pies",
            "componentes": "V, S",
            "duracion": "1 minuto",
            "tipo_ataque": "Ninguno",
            "requiere_salvacion": False,
            "tipo_salvacion": "Ninguna",
            "efecto_salvacion": "Ningún daño",
            "daño_base": "",
            "tipo_daño": "Ninguno",
            "curacion_base": "",
            "daño_nivel_superior": "",
            "curacion_nivel_superior": "",
            "clases": ["Bardo", "Brujo", "Mago", "Hechicero"],
            "descripcion": "Una mano espectral flotante aparece en un punto que elijas dentro del alcance. La mano dura mientras dure el conjuro o hasta que la descartes como una acción. La mano se desvanece si está alguna vez a más de 30 pies de ti o si vuelves a lanzar este conjuro.\n\nPuedes usar tu acción para controlar la mano. Puedes usarla para manipular un objeto, abrir una puerta o un contenedor cerrado sin llave, guardar o recuperar un objeto de un contenedor abierto, o verter el contenido de un vial. Puedes mover la mano hasta 30 pies cada vez que la usas.\n\nLa mano no puede atacar, activar objetos mágicos o llevar más de 10 libras."
        },
        {
            "nombre": "Proyectil Mágico",
            "nivel": 1,
            "escuela": "Evocación",
            "tiempo_lanzamiento": "1 acción",
            "alcance": "120 pies",
            "componentes": "V, S",
            "duracion": "Instantáneo",
            "tipo_ataque": "Ninguno",
            "requiere_salvacion": False,
            "tipo_salvacion": "Ninguna",
            "efecto_salvacion": "Ningún daño",
            "daño_base": "1d4+1",
            "tipo_daño": "Fuerza",
            "curacion_base": "",
            "daño_nivel_superior": "1d4+1",
            "curacion_nivel_superior": "",
            "clases": ["Mago", "Hechicero"],
            "descripcion": "Creas tres dardos brillantes de fuerza mágica. Cada dardo impacta a una criatura que puedas ver dentro del alcance. Un dardo inflige 1d4+1 de daño por fuerza a su objetivo. Los dardos impactan todos simultáneamente, y puedes dirigirlos para que impacten a una criatura o a varias.\nA niveles superiores: Cuando lanzas este hechizo usando un espacio de conjuro de nivel 2 o superior, el hechizo crea un dardo adicional por cada nivel por encima de 1."
        },
        {
            "nombre": "Rayo de Escarcha",
            "nivel": 0,
            "escuela": "Evocación",
            "tiempo_lanzamiento": "1 acción",
            "alcance": "60 pies",
            "componentes": "V, S",
            "duracion": "Instantáneo",
            "tipo_ataque": "A distancia",
            "requiere_salvacion": False,
            "tipo_salvacion": "Ninguna",
            "efecto_salvacion": "Ningún daño",
            "daño_base": "1d8",
            "tipo_daño": "Frío",
            "curacion_base": "",
            "daño_nivel_superior": "",
            "curacion_nivel_superior": "",
            "clases": ["Mago", "Hechicero"],
            "descripcion": "Un rayo frío de luz azul pálido se dispara hacia una criatura dentro del alcance. Realiza un ataque de hechizo a distancia contra el objetivo. Si impacta, el objetivo recibe 1d8 de daño por frío, y su velocidad se reduce en 10 pies hasta el comienzo de tu siguiente turno.\nEl daño del hechizo aumenta en 1d8 cuando alcanzas el nivel 5 (2d8), el nivel 11 (3d8) y el nivel 17 (4d8)."
        },
        {
            "nombre": "Escudo",
            "nivel": 1,
            "escuela": "Abjuración",
            "tiempo_lanzamiento": "1 reacción",
            "alcance": "Personal",
            "componentes": "V, S",
            "duracion": "1 round",
            "tipo_ataque": "Ninguno",
            "requiere_salvacion": False,
            "tipo_salvacion": "Ninguna",
            "efecto_salvacion": "Ningún daño",
            "daño_base": "",
            "tipo_daño": "Ninguno",
            "curacion_base": "",
            "daño_nivel_superior": "",
            "curacion_nivel_superior": "",
            "clases": ["Mago", "Hechicero"],
            "descripcion": "Una barrera invisible de fuerza mágica aparece y te protege. Hasta el comienzo de tu siguiente turno, tienes un bonificador +5 a la CA, incluyendo contra el ataque que desencadenó el hechizo, y no recibes daño de Proyectil Mágico."
        },
        {
            "nombre": "Curación Masiva",
            "nivel": 5,
            "escuela": "Evocación",
            "tiempo_lanzamiento": "1 acción",
            "alcance": "60 pies",
            "componentes": "V, S",
            "duracion": "Instantáneo",
            "tipo_ataque": "Ninguno",
            "requiere_salvacion": False,
            "tipo_salvacion": "Ninguna",
            "efecto_salvacion": "Ningún daño",
            "daño_base": "",
            "tipo_daño": "Ninguno",
            "curacion_base": "3d8+5",
            "daño_nivel_superior": "",
            "curacion_nivel_superior": "1d8",
            "clases": ["Clérigo", "Druida"],
            "descripcion": "Una oleada de energía curativa emana de ti hacia las criaturas heridas que te rodean. Recuperas hasta seis criaturas que puedas ver dentro del alcance. Cada objetivo recupera puntos de golpe igual a 3d8 + tu modificador de característica de lanzamiento de conjuros.\nEste hechizo no tiene efecto sobre no muertos o constructos.\nA niveles superiores: Cuando lanzas este hechizo usando un espacio de hechizo de nivel 6 o superior, la curación aumenta en 1d8 por cada nivel por encima de 5."
        },
        {
            "nombre": "Desintegrar",
            "nivel": 6,
            "escuela": "Transmutación",
            "tiempo_lanzamiento": "1 acción",
            "alcance": "60 pies",
            "componentes": "V, S, M (un imán y una pizca de polvo)",
            "duracion": "Instantáneo",
            "tipo_ataque": "Ninguno",
            "requiere_salvacion": True,
            "tipo_salvacion": "Destreza",
            "efecto_salvacion": "Ningún daño",
            "daño_base": "10d6+40",
            "tipo_daño": "Fuerza",
            "curacion_base": "",
            "daño_nivel_superior": "3d6",
            "curacion_nivel_superior": "",
            "clases": ["Mago", "Hechicero"],
            "descripcion": "Un fino rayo verde brota de tu dedo índice hacia un objetivo que puedas ver dentro del alcance. El objetivo puede ser una criatura, un objeto o una creación de fuerza mágica, como un muro creado por Muro de Fuerza.\nUna criatura a la que se dirige este hechizo debe hacer una tirada de salvación de Destreza. Si falla, el objetivo sufre 10d6 + 40 de daño por fuerza. Si este daño reduce los puntos de golpe del objetivo a 0, éste es desintegrado.\nUn objetivo desintegrado y todo lo que lleva puesto y transporta, excepto los objetos mágicos, se reduce a un montón de fino polvo gris. La criatura solo puede ser devuelta a la vida mediante los hechizos Resurrección Verdadera o Deseo.\nEste hechizo desintegra automáticamente un objeto no mágico de tamaño Grande o menor o una creación de fuerza mágica. Si el objetivo es un objeto no mágico de tamaño Enorme o mayor, este hechizo desintegra una porción de 10 pies cúbicos de él.\nA niveles superiores: Cuando lanzas este hechizo usando un espacio de hechizo de nivel 7 o superior, el daño aumenta en 3d6 por cada nivel por encima de 6."
        }
    ]
    
    # Agregar hechizos de ejemplo a la base de datos
    for hechizo in hechizos_ejemplo:
        agregar_hechizo(hechizo)
    
    print(f"Se han agregado {len(hechizos_ejemplo)} hechizos de ejemplo a la base de datos.")

# Función para importar hechizos desde archivo externo
def importar_hechizos_desde_json(ruta_archivo):
    """
    Importa hechizos desde un archivo JSON externo
    
    Args:
        ruta_archivo (str): Ruta al archivo JSON con los hechizos
        
    Returns:
        int: Número de hechizos importados exitosamente
    """
    try:
        # Leer archivo
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            hechizos_importados = json.load(f)
        
        # Verificar formato
        if not isinstance(hechizos_importados, list):
            print("Error: El archivo debe contener una lista de hechizos.")
            return 0
        
        # Contador de hechizos importados
        contador = 0
        
        # Importar cada hechizo
        for hechizo in hechizos_importados:
            exito, _ = agregar_hechizo(hechizo)
            if exito:
                contador += 1
        
        return contador
    
    except Exception as e:
        print(f"Error al importar hechizos: {str(e)}")
        return 0

# ----- Funciones de utilidad para integración con el gestor de personajes -----

def obtener_hechizo_por_nombre(nombre, nivel=None):
    """
    Busca un hechizo específico por nombre y opcionalmente nivel
    
    Args:
        nombre (str): Nombre del hechizo a buscar
        nivel (int, optional): Nivel del hechizo para filtrar. Por defecto None.
        
    Returns:
        dict: Datos del hechizo o None si no se encuentra
    """
    hechizos_por_nivel = cargar_hechizos()
    
    # Si se especifica nivel, buscar solo en ese nivel
    if nivel is not None:
        nivel_str = str(nivel)
        if nivel_str in hechizos_por_nivel:
            for hechizo in hechizos_por_nivel[nivel_str]:
                if hechizo.get("nombre", "").lower() == nombre.lower():
                    return hechizo
    else:
        # Buscar en todos los niveles
        for nivel_hechizos in hechizos_por_nivel.values():
            for hechizo in nivel_hechizos:
                if hechizo.get("nombre", "").lower() == nombre.lower():
                    return hechizo
    
    return None

def obtener_hechizos_por_clase_y_nivel(clase, nivel_max=9, nivel_min=0):
    """
    Obtiene todos los hechizos disponibles para una clase específica hasta un nivel máximo
    
    Args:
        clase (str): Clase del personaje
        nivel_max (int, optional): Nivel máximo de hechizos a incluir. Por defecto 9.
        nivel_min (int, optional): Nivel mínimo de hechizos a incluir. Por defecto 0.
        
    Returns:
        list: Lista de hechizos disponibles para la clase
    """
    hechizos_por_nivel = cargar_hechizos()
    hechizos_disponibles = []
    
    for nivel in range(nivel_min, nivel_max + 1):
        nivel_str = str(nivel)
        if nivel_str in hechizos_por_nivel:
            for hechizo in hechizos_por_nivel[nivel_str]:
                if clase in hechizo.get("clases", []):
                    hechizos_disponibles.append(hechizo)
    
    return hechizos_disponibles

def simular_lanzamiento_hechizo(hechizo, nivel_lanzamiento=None, estadistica_conjuros=3, bono_competencia=2):
    """
    Simula el lanzamiento de un hechizo, calculando tiradas de ataque, daño y salvaciones
    
    Args:
        hechizo (dict): Datos del hechizo
        nivel_lanzamiento (int, optional): Nivel al que se lanza el hechizo. Por defecto None (usa el nivel del hechizo).
        estadistica_conjuros (int, optional): Modificador de la estadística de conjuros. Por defecto 3.
        bono_competencia (int, optional): Bonificador de competencia. Por defecto 2.
        
    Returns:
        dict: Resultados de la simulación
    """
    # Si no se especifica nivel de lanzamiento, usar nivel del hechizo
    if nivel_lanzamiento is None:
        nivel_lanzamiento = int(hechizo.get("nivel", 0))
    
    # Obtener nivel del hechizo
    nivel_hechizo = int(hechizo.get("nivel", 0))
    niveles_adicionales = max(0, nivel_lanzamiento - nivel_hechizo)
    
    # Calcular CD de salvación y bono de ataque
    cd_salvacion = 8 + estadistica_conjuros + bono_competencia
    bono_ataque = estadistica_conjuros + bono_competencia
    
    # Inicializar resultados
    resultados = {
        "nombre": hechizo.get("nombre", ""),
        "nivel_hechizo": nivel_hechizo,
        "nivel_lanzamiento": nivel_lanzamiento,
        "cd_salvacion": cd_salvacion,
        "bono_ataque": bono_ataque,
        "tirada_ataque": None,
        "exito_salvacion": None,
        "daño": {
            "formula": hechizo.get("daño_base", ""),
            "resultado": 0,
            "tipo": hechizo.get("tipo_daño", "Ninguno")
        },
        "curacion": {
            "formula": hechizo.get("curacion_base", ""),
            "resultado": 0
        }
    }
    
    # Simular tirada de ataque si es necesario
    if hechizo.get("tipo_ataque", "Ninguno") != "Ninguno":
        # Tirada de d20 + bono de ataque
        tirada = random.randint(1, 20)
        resultados["tirada_ataque"] = {
            "d20": tirada,
            "bono": bono_ataque,
            "total": tirada + bono_ataque,
            "critico": tirada == 20,
            "pifia": tirada == 1
        }
    
    # Simular tirada de salvación (solo para mostrar info)
    if hechizo.get("requiere_salvacion", False):
        tirada = random.randint(1, 20)
        mod_salvacion = 2  # Suponer un modificador promedio
        resultados["exito_salvacion"] = {
            "tipo": hechizo.get("tipo_salvacion", "Ninguna"),
            "d20": tirada,
            "bono": mod_salvacion,
            "total": tirada + mod_salvacion,
            "cd": cd_salvacion,
            "exito": (tirada + mod_salvacion) >= cd_salvacion,
            "efecto": hechizo.get("efecto_salvacion", "Ningún daño")
        }
    
    # Calcular daño base
    if hechizo.get("daño_base", ""):
        # Obtener componentes de la fórmula
        patron = r'^(\d+)d(\d+)([+-]\d+)?$'
        match = re.match(patron, hechizo.get("daño_base", ""))
        
        if match:
            num_dados = int(match.group(1))
            tipo_dado = int(match.group(2))
            mod_adicional = 0
            
            if match.group(3):
                mod_adicional = int(match.group(3))
            
            # Calcular daño base
            daño = sum(random.randint(1, tipo_dado) for _ in range(num_dados)) + mod_adicional
            
            # Añadir daño por nivel superior si aplica
            if niveles_adicionales > 0 and hechizo.get("daño_nivel_superior", ""):
                match_nivel = re.match(patron, hechizo.get("daño_nivel_superior", ""))
                if match_nivel:
                    num_dados_nivel = int(match_nivel.group(1))
                    tipo_dado_nivel = int(match_nivel.group(2))
                    mod_adicional_nivel = 0
                    
                    if match_nivel.group(3):
                        mod_adicional_nivel = int(match_nivel.group(3))
                    
                    # Añadir daño por cada nivel adicional
                    for _ in range(niveles_adicionales):
                        daño_nivel = sum(random.randint(1, tipo_dado_nivel) for _ in range(num_dados_nivel)) + mod_adicional_nivel
                        daño += daño_nivel
            
            # Guardar resultado
            resultados["daño"]["resultado"] = daño
    
    # Calcular curación base
    if hechizo.get("curacion_base", ""):
        # Obtener componentes de la fórmula
        patron = r'^(\d+)d(\d+)([+-]\d+)?$'
        match = re.match(patron, hechizo.get("curacion_base", ""))
        
        if match:
            num_dados = int(match.group(1))
            tipo_dado = int(match.group(2))
            mod_adicional = 0
            
            if match.group(3):
                mod_adicional = int(match.group(3))
            else:
                # Si no hay modificador especificado, añadir el modificador de conjuros
                mod_adicional = estadistica_conjuros
            
            # Calcular curación base
            curacion = sum(random.randint(1, tipo_dado) for _ in range(num_dados)) + mod_adicional
            
            # Añadir curación por nivel superior si aplica
            if niveles_adicionales > 0 and hechizo.get("curacion_nivel_superior", ""):
                match_nivel = re.match(patron, hechizo.get("curacion_nivel_superior", ""))
                if match_nivel:
                    num_dados_nivel = int(match_nivel.group(1))
                    tipo_dado_nivel = int(match_nivel.group(2))
                    mod_adicional_nivel = 0
                    
                    if match_nivel.group(3):
                        mod_adicional_nivel = int(match_nivel.group(3))
                    
                    # Añadir curación por cada nivel adicional
                    for _ in range(niveles_adicionales):
                        curacion_nivel = sum(random.randint(1, tipo_dado_nivel) for _ in range(num_dados_nivel)) + mod_adicional_nivel
                        curacion += curacion_nivel
            
            # Guardar resultado
            resultados["curacion"]["resultado"] = curacion
    
    return resultados

# Punto de entrada si se ejecuta como script principal
if __name__ == "__main__":
    print("Gestor de Hechizos para D&D Combat Manager")
    print("------------------------------------------")
    
    # Inicializar directorios y archivos necesarios
    inicializar_directorios()
    
    # Comprobar si ya existen hechizos
    hechizos = cargar_hechizos()
    total_hechizos = sum(len(nivel) for nivel in hechizos.values())
    
    if total_hechizos == 0:
        print("No se encontraron hechizos. Creando hechizos de ejemplo...")
        crear_hechizos_ejemplo()
    else:
        print(f"Se encontraron {total_hechizos} hechizos en la base de datos.")
    
    print("\nPara usar el gestor de hechizos, importe el módulo en su aplicación principal.")
    print("Ejemplo: from gestor_hechizos import mostrar_gestor_hechizos")
    print("\nPara probar una simulación de lanzamiento de hechizo:")
    
    # Mostrar ejemplo de simulación si hay hechizos disponibles
    if total_hechizos > 0:
        # Buscar un hechizo que tenga daño
        hechizo_ejemplo = None
        for nivel in hechizos.values():
            for h in nivel:
                if h.get("daño_base", ""):
                    hechizo_ejemplo = h
                    break
            if hechizo_ejemplo:
                break
        
        if hechizo_ejemplo:
            print(f"\nEjemplo con el hechizo '{hechizo_ejemplo['nombre']}':")
            resultado = simular_lanzamiento_hechizo(hechizo_ejemplo, nivel_lanzamiento=5)
            
            print(f"CD de Salvación: {resultado['cd_salvacion']}")
            print(f"Bono de Ataque: +{resultado['bono_ataque']}")
            
            if resultado['tirada_ataque']:
                print(f"Tirada de Ataque: {resultado['tirada_ataque']['d20']} + {resultado['tirada_ataque']['bono']} = {resultado['tirada_ataque']['total']}")
            
            if resultado['daño']['resultado'] > 0:
                print(f"Daño: {resultado['daño']['resultado']} de tipo {resultado['daño']['tipo']}")
            
            if resultado['curacion']['resultado'] > 0:
                print(f"Curación: {resultado['curacion']['resultado']} puntos de golpe")