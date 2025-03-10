#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplicación principal de Dungeons and Dragons para gestión de combates.
"""

# 1. Configuración Inicial e Importaciones
import tkinter as tk
from tkinter import ttk, messagebox, font
import os

# Importar módulos propios
from modulos.nueva_campana import mostrar_nueva_campana
from modulos.cargar_campana import mostrar_cargar_campana

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
        
        # Colores para la aplicación
        self.root.configure(bg="#2e2e2e")
        style.configure("TFrame", background="#2e2e2e")
        style.configure("TButton", background="#7b0000", foreground="white")
        style.configure("TLabel", background="#2e2e2e", foreground="white")
        style.configure("Menu.TButton", font=('Helvetica', 14, 'bold'), padding=15)
    
    def mostrar_menu_principal(self):
        """Muestra el menú principal"""
        # Limpiar el frame principal
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Título
        title_label = ttk.Label(self.main_frame, text="D&D Combat Manager", style="Title.TLabel")
        title_label.pack(pady=(30, 50))
        
        # Creación de botones del menú
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill="both", expand=True)
        
        # Botones con las opciones del menú
        botones = [
            ("Nueva Campaña", lambda: mostrar_nueva_campana(self.root, self.directorio_campanas, self.mostrar_menu_principal)),
            ("Cargar Campaña", lambda: mostrar_cargar_campana(self.root, self.directorio_campanas, self.mostrar_menu_principal)),
            ("Gestor de Personajes", self.no_implementado),
            ("Gestor de Monstruos", self.no_implementado),
            ("DM Panel", self.no_implementado),
            ("Simular Combate", self.no_implementado)
        ]
        
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