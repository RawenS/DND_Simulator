#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplicación principal de Dungeons and Dragons para gestión de combates.
"""

# 1. Configuración Inicial e Importaciones
import tkinter as tk
from tkinter import ttk, messagebox, font
import os
import json

# Importar módulos propios
from modulos.nueva_campana import mostrar_nueva_campana
from modulos.cargar_campana import mostrar_cargar_campana
from modulos.gestor_personajes import mostrar_gestor_personajes
from editores.editar_personaje import mostrar_editar_personaje

class DnDApp:
    def __init__(self, root):
        self.root = root
        self.root.title("D&D Combat Manager")
        self.root.geometry("1024x768")
        self.root.minsize(1024, 768)
        
        # Configurar columnas y filas para expansión
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Configuración de estilo
        self.configurar_estilo()
        
        # Crear frame principal
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Directorio para guardar campañas
        self.directorio_campanas = "campanas"
        if not os.path.exists(self.directorio_campanas):
            os.makedirs(self.directorio_campanas)
        
        # Campaña actual
        self.campana_actual = None
        self.ruta_campana_actual = None
        
        # Frame para la información de campaña en esquina superior derecha
        self.info_frame = ttk.Frame(self.root)
        self.info_frame.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)
        
        # Etiqueta para mostrar la campaña actual
        self.label_campana_actual = ttk.Label(self.info_frame, text="Campaña: Ninguna", font=('Helvetica', 11))
        self.label_campana_actual.pack(anchor="e")
        
        # Panel de personajes (inicialmente oculto)
        self.personajes_panel = None
        
        # Mostrar menú principal
        self.mostrar_menu_principal()
    
    def configurar_estilo(self):
        """Configura los estilos de la aplicación"""
        style = ttk.Style()
        style.theme_use("clam")
        
        # Definir fuentes
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(size=11)
        
        # Configurar estilos personalizados
        style.configure("TButton", padding=10, font=('Helvetica', 11))
        style.configure("TLabel", font=('Helvetica', 11))
        style.configure("TEntry", font=('Helvetica', 11))
        style.configure("TCombobox", font=('Helvetica', 11))
        style.configure("TCheckbutton", font=('Helvetica', 11))
        style.configure("Header.TLabel", font=('Helvetica', 18, 'bold'))
        style.configure("Title.TLabel", font=('Helvetica', 24, 'bold'))
        style.configure("Subtitle.TLabel", font=('Helvetica', 16, 'bold'))
        
        # Estilos compactos para panel de personajes
        style.configure("Compact.TButton", padding=3, font=('Helvetica', 9))
        style.configure("PanelHeader.TLabel", font=('Helvetica', 10, 'bold'))
        style.configure("Link.TLabel", font=('Helvetica', 10), foreground="#0000ff")
        
        # Colores para la aplicación
        self.root.configure(bg="#2e2e2e")
        style.configure("TFrame", background="#2e2e2e")
        style.configure("TButton", background="#7b0000", foreground="white")
        style.configure("TLabel", background="#2e2e2e", foreground="white")
        style.configure("Menu.TButton", font=('Helvetica', 14, 'bold'), padding=15)
        
        # Estilo especial para el panel
        style.configure("Panel.TFrame", background="#3e3e3e")
        style.configure("PanelHeader.TLabel", background="#3e3e3e", foreground="white")
        style.configure("PanelText.TLabel", background="#3e3e3e", foreground="white")
        style.configure("Compact.TButton", background="#600000", foreground="white")
    
    def mostrar_menu_principal(self):
        """Muestra el menú principal"""
        # Limpiar el frame principal
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Actualizar etiqueta de campaña actual
        if self.campana_actual:
            self.label_campana_actual.config(text=f"Campaña: {self.campana_actual.get('nombre', 'Sin nombre')}")
            # Mostrar panel de personajes
            self.mostrar_panel_personajes()
        else:
            self.label_campana_actual.config(text="Campaña: Ninguna")
            # Ocultar panel de personajes si existe
            if self.personajes_panel:
                self.personajes_panel.destroy()
                self.personajes_panel = None
        
        # Título
        title_label = ttk.Label(self.main_frame, text="D&D Combat Manager", style="Title.TLabel")
        title_label.pack(pady=(30, 50))
        
        # Creación de botones del menú
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill="both", expand=True)
        
        # Botones con las opciones del menú - siempre presentes
        botones = [
            ("Nueva Campaña", lambda: mostrar_nueva_campana(self.root, self.directorio_campanas, self.mostrar_menu_principal)),
            ("Cargar Campaña", lambda: mostrar_cargar_campana(self.root, self.directorio_campanas, self.mostrar_menu_principal, self.cargar_campana)),
            ("Gestor de Personajes", lambda: mostrar_gestor_personajes(self.root, self.mostrar_menu_principal)),
            ("Gestor de Monstruos", self.no_implementado),
        ]
        
        # Añadir botones adicionales según haya campaña cargada o no
        # CAMBIO: Ya no agregamos los botones de continuar y editar campaña
        if self.campana_actual:
            botones.extend([
                # Los botones "Continuar Campaña Actual" y "Editar Campaña Actual" han sido eliminados
                ("DM Panel", self.no_implementado),
                ("Simular Combate", self.no_implementado)
            ])
        else:
            botones.extend([
                ("DM Panel", self.no_implementado),
                ("Simular Combate", self.no_implementado)
            ])
        
        # Configurar el frame de botones para expansión
        button_frame.columnconfigure(0, weight=1)
        
        # Creación y configuración de botones
        for i, (texto, comando) in enumerate(botones):
            btn = ttk.Button(button_frame, text=texto, command=comando, style="Menu.TButton")
            btn.grid(row=i, column=0, sticky="ew", padx=100, pady=10)
        
        # Versión
        version_label = ttk.Label(self.main_frame, text="Versión 0.1")
        version_label.pack(pady=(50, 10), side="bottom")
        
        # Mostrar el frame
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    def mostrar_panel_personajes(self):
        """Muestra un panel compacto con los personajes de la campaña actual"""
        # Destruir panel existente si hay
        if self.personajes_panel:
            self.personajes_panel.destroy()
        
        # Verificar si hay personajes en la campaña
        if not self.campana_actual or not self.campana_actual.get("jugadores", []):
            return
        
        # Crear nuevo panel
        self.personajes_panel = ttk.Frame(self.info_frame, style="Panel.TFrame")
        self.personajes_panel.pack(fill="x", pady=2, anchor="e")
        
        # Botón para mostrar/ocultar panel de personajes
        self.toggle_button = ttk.Button(self.personajes_panel, text="Mostrar Personajes", 
                                      command=self.toggle_personajes_panel, style="Compact.TButton")
        self.toggle_button.pack(fill="x", pady=2)
        
        # Frame para la lista de personajes (inicialmente oculto)
        self.lista_personajes_frame = ttk.Frame(self.personajes_panel, style="Panel.TFrame")
        self.lista_personajes_frame.pack_forget()  # Inicialmente oculto
        
        # Añadir personajes al panel
        for i, personaje in enumerate(self.campana_actual.get("jugadores", [])):
            personaje_frame = ttk.Frame(self.lista_personajes_frame, style="Panel.TFrame")
            personaje_frame.pack(fill="x", pady=2)
            
            # Información del personaje
            info_texto = f"{personaje.get('nombre', 'Sin nombre')} ({personaje.get('clase', '')}, Nv.{personaje.get('nivel', 1)})"
            ttk.Label(personaje_frame, text=info_texto, style="PanelText.TLabel").pack(side="left", padx=5)
            
            # Botón para editar
            personaje_actual = personaje  # Para la captura de lambda
            idx = i  # Para la captura de lambda
            ttk.Button(personaje_frame, text="EDITAR", 
                     command=lambda p=personaje_actual, idx=idx: self.editar_personaje_desde_menu(p, idx),
                     style="Compact.TButton").pack(side="right", padx=5)
        
        # Botón para editar campaña
        edit_btn_frame = ttk.Frame(self.lista_personajes_frame, style="Panel.TFrame")
        edit_btn_frame.pack(fill="x", pady=5)
        ttk.Button(edit_btn_frame, text="Editar Campaña", 
                  command=self.editar_campana_actual, 
                  style="Compact.TButton").pack(side="right", padx=5, pady=2)
    
    def toggle_personajes_panel(self):
        """Muestra u oculta el panel de personajes"""
        if self.lista_personajes_frame.winfo_ismapped():
            self.lista_personajes_frame.pack_forget()
            self.toggle_button.config(text="Mostrar Personajes")
        else:
            self.lista_personajes_frame.pack(fill="x", pady=2)
            self.toggle_button.config(text="Ocultar Personajes")
    
    def cargar_campana(self, campana, ruta):
        """Carga una campaña como la campaña actual"""
        self.campana_actual = campana
        self.ruta_campana_actual = ruta
        # Actualizar el indicador de campaña
        self.label_campana_actual.config(text=f"Campaña: {campana.get('nombre', 'Sin nombre')}")
        # Actualizar panel de personajes
        self.mostrar_panel_personajes()
        # Volver al menú principal
        self.mostrar_menu_principal()
    
    def continuar_campana_actual(self):
        """Continua la campaña actual mostrando directamente el menú principal con los personajes"""
        if not self.campana_actual:
            messagebox.showinfo("Información", "No hay ninguna campaña cargada.")
            return
        
        # Simplemente volvemos al menú principal, que ya mostrará los personajes
        self.mostrar_menu_principal()
    
    def editar_personaje_desde_menu(self, personaje, indice):
        """Edita un personaje desde el menú principal"""
        from editores.editar_personaje import mostrar_editar_personaje
        
        # Callback para cuando se termina la edición
        def callback_edicion():
            # Recargar la campaña para reflejar los cambios
            if self.ruta_campana_actual:
                try:
                    with open(self.ruta_campana_actual, 'r', encoding='utf-8') as f:
                        self.campana_actual = json.load(f)
                except Exception as e:
                    messagebox.showerror("Error", f"Error al recargar la campaña: {str(e)}")
            
            # Actualizar panel de personajes
            self.mostrar_panel_personajes()
            # Volver al menú principal
            self.mostrar_menu_principal()
        
        # Mostrar el editor de personaje
        mostrar_editar_personaje(self.root, personaje, callback_edicion)
    
    def editar_campana_actual(self):
        """Implementar edición de la campaña actual"""
        if not self.campana_actual:
            messagebox.showinfo("Información", "No hay ninguna campaña cargada.")
            return
        
        # Llamar a la función para editar la campaña
        from editores.editar_campana import mostrar_editar_campana
        mostrar_editar_campana(self.root, self.campana_actual, self.ruta_campana_actual,
                              self.directorio_campanas, self.cargar_campana, self.mostrar_menu_principal)
    
    def no_implementado(self):
        """Función temporal para opciones no implementadas"""
        messagebox.showinfo("Información", "No implementado")

# Inicialización de la aplicación
def main():
    root = tk.Tk()
    app = DnDApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()