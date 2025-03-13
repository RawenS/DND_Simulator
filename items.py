#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo para el sistema de objetos equipables en la aplicación D&D Combat Manager.
Define la estructura base para todos los tipos de items, el comportamiento específico por tipo,
y la funcionalidad para guardar/cargar los objetos.
"""

import json
import os
from typing import Dict, List, Any, Optional, Union

# Directorio para almacenar los objetos
DIRECTORIO_OBJETOS = "data/objetos"

# Tipos de objetos disponibles
ITEM_TYPES = {
    "armor": "Armadura",
    "weapon": "Arma",
    "helmet": "Casco",
    "shield": "Escudo",
    "ring": "Anillo",
    "amulet": "Amuleto",
    "accessory": "Accesorio",
    "consumable": "Consumible"
}

# Propiedades específicas por tipo
TYPE_PROPERTIES = {
    "armor": ["base_ac", "dex_bonus_limit", "strength_required", "stealth_disadvantage"],
    "weapon": ["damage_dice", "damage_type", "range", "properties"],
    "helmet": ["base_ac", "ability_bonus", "properties"],
    "shield": ["base_ac", "properties"],
    "ring": ["ability_bonus", "saving_throw_bonus", "properties"],
    "amulet": ["ability_bonus", "saving_throw_bonus", "properties"],
    "accessory": ["ability_bonus", "properties"],
    "consumable": ["effect", "duration", "uses"]
}

# Tipos de rareza
RARITY_TYPES = [
    "Common", "Uncommon", "Rare", "Very Rare", "Legendary", "Artifact"
]

# Tipos de daño
DAMAGE_TYPES = [
    "Ácido", "Contundente", "Frío", "Fuego", "Fuerza", "Necrótico", 
    "Perforante", "Psíquico", "Radiante", "Relámpago", "Cortante", "Trueno", "Veneno"
]

# Propiedades de armas
WEAPON_PROPERTIES = [
    "Munición", "Cuerpo a cuerpo", "A distancia", "Alcance", "Recarga", "Arrojo",
    "A dos manos", "Versátil", "Ligera", "Pesada", "Sutil", "Especial"
]

class Item:
    """Clase base para todos los objetos equipables"""
    
    def __init__(self, id: str, name: str, item_type: str, rarity: str, 
                 description: str, properties: Dict = None, magic: bool = False):
        """
        Inicializa un nuevo objeto equipable
        
        Args:
            id (str): Identificador único del objeto
            name (str): Nombre del objeto
            item_type (str): Tipo de objeto (armor, weapon, etc.)
            rarity (str): Rareza del objeto
            description (str): Descripción del objeto
            properties (Dict, optional): Propiedades adicionales. Por defecto None
            magic (bool, optional): Si el objeto es mágico. Por defecto False
        """
        self.id = id
        self.name = name
        self.item_type = item_type
        self.rarity = rarity
        self.description = description
        self.properties = properties or {}
        self.magic = magic
    
    def to_dict(self) -> Dict:
        """
        Convierte el objeto a un diccionario para guardarlo
        
        Returns:
            Dict: Representación del objeto como diccionario
        """
        return {
            "id": self.id,
            "name": self.name,
            "type": self.item_type,
            "rarity": self.rarity,
            "description": self.description,
            "properties": self.properties,
            "magic": self.magic
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Item':
        """
        Crea un objeto a partir de un diccionario
        
        Args:
            data (Dict): Diccionario con los datos del objeto
        
        Returns:
            Item: Objeto creado
        """
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            item_type=data.get("type", ""),
            rarity=data.get("rarity", "Common"),
            description=data.get("description", ""),
            properties=data.get("properties", {}),
            magic=data.get("magic", False)
        )
    
    def get_ac_bonus(self) -> int:
        """
        Obtiene la bonificación a la CA proporcionada por el objeto
        
        Returns:
            int: Bonificación a la CA (0 por defecto)
        """
        if self.item_type in ["armor", "helmet", "shield"]:
            return self.properties.get("base_ac", 0)
        return 0
    
    def get_dex_bonus_limit(self) -> Optional[int]:
        """
        Obtiene el límite de bonificación por destreza para armaduras
        
        Returns:
            Optional[int]: Límite de bonificación por destreza (None si no aplica)
        """
        if self.item_type == "armor":
            limit = self.properties.get("dex_bonus_limit")
            if limit is not None:
                return int(limit)
        return None
    
    def get_damage(self) -> str:
        """
        Obtiene el daño del arma
        
        Returns:
            str: Descripción del daño (vacío si no es un arma)
        """
        if self.item_type == "weapon":
            damage_dice = self.properties.get("damage_dice", "")
            damage_type = self.properties.get("damage_type", "")
            if damage_dice and damage_type:
                return f"{damage_dice} {damage_type}"
        return ""
    
    def get_ability_bonus(self) -> Dict[str, int]:
        """
        Obtiene bonificaciones a habilidades
        
        Returns:
            Dict[str, int]: Diccionario con habilidades y sus bonificaciones
        """
        return self.properties.get("ability_bonus", {})
    
    def __str__(self) -> str:
        """
        Representación de cadena del objeto
        
        Returns:
            str: Representación legible del objeto
        """
        base_str = f"{self.name} ({ITEM_TYPES.get(self.item_type, self.item_type)})"
        if self.magic:
            base_str += " [Mágico]"
        
        if self.item_type in ["armor", "helmet", "shield"]:
            base_str += f" - CA: {self.get_ac_bonus()}"
        elif self.item_type == "weapon":
            damage = self.get_damage()
            if damage:
                base_str += f" - Daño: {damage}"
        
        return base_str


def save_item(item: Item) -> bool:
    """
    Guarda un objeto en el sistema de archivos
    
    Args:
        item (Item): Objeto a guardar
    
    Returns:
        bool: True si se guardó correctamente, False en caso contrario
    """
    # Asegurar que el directorio existe
    os.makedirs(DIRECTORIO_OBJETOS, exist_ok=True)
    os.makedirs(os.path.join(DIRECTORIO_OBJETOS, item.item_type), exist_ok=True)
    
    # Ruta del archivo
    filepath = os.path.join(DIRECTORIO_OBJETOS, item.item_type, f"{item.id}.json")
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(item.to_dict(), f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"Error al guardar el objeto: {str(e)}")
        return False


def load_item(item_type: str, item_id: str) -> Optional[Item]:
    """
    Carga un objeto desde el sistema de archivos
    
    Args:
        item_type (str): Tipo de objeto
        item_id (str): ID del objeto
    
    Returns:
        Optional[Item]: Objeto cargado o None si no se encuentra
    """
    filepath = os.path.join(DIRECTORIO_OBJETOS, item_type, f"{item_id}.json")
    
    if not os.path.exists(filepath):
        return None
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return Item.from_dict(data)
    except Exception as e:
        print(f"Error al cargar el objeto: {str(e)}")
        return None


def load_all_items_by_type(item_type: str) -> List[Item]:
    """
    Carga todos los objetos de un tipo específico
    
    Args:
        item_type (str): Tipo de objeto a cargar
    
    Returns:
        List[Item]: Lista de objetos del tipo especificado
    """
    items = []
    type_dir = os.path.join(DIRECTORIO_OBJETOS, item_type)
    
    if not os.path.exists(type_dir):
        os.makedirs(type_dir, exist_ok=True)
        return items
    
    for filename in os.listdir(type_dir):
        if filename.endswith('.json'):
            item_id = filename[:-5]  # Quitar la extensión .json
            item = load_item(item_type, item_id)
            if item:
                items.append(item)
    
    return items


def load_all_items() -> Dict[str, List[Item]]:
    """
    Carga todos los objetos organizados por tipo
    
    Returns:
        Dict[str, List[Item]]: Diccionario con listas de objetos por tipo
    """
    all_items = {}
    
    # Asegurar que el directorio existe
    os.makedirs(DIRECTORIO_OBJETOS, exist_ok=True)
    
    for item_type in ITEM_TYPES:
        all_items[item_type] = load_all_items_by_type(item_type)
    
    return all_items


def delete_item(item_type: str, item_id: str) -> bool:
    """
    Elimina un objeto del sistema de archivos
    
    Args:
        item_type (str): Tipo de objeto
        item_id (str): ID del objeto
    
    Returns:
        bool: True si se eliminó correctamente, False en caso contrario
    """
    filepath = os.path.join(DIRECTORIO_OBJETOS, item_type, f"{item_id}.json")
    
    if not os.path.exists(filepath):
        return False
    
    try:
        os.remove(filepath)
        return True
    except Exception as e:
        print(f"Error al eliminar el objeto: {str(e)}")
        return False


def generate_unique_id(item_type: str, name: str) -> str:
    """
    Genera un ID único para un objeto basado en su tipo y nombre
    
    Args:
        item_type (str): Tipo de objeto
        name (str): Nombre del objeto
    
    Returns:
        str: ID único
    """
    # Crear un slug a partir del nombre
    slug = name.lower().replace(" ", "_").replace("-", "_")
    # Eliminar caracteres especiales
    slug = ''.join(c for c in slug if c.isalnum() or c == '_')
    
    # Comprobar si ya existe un objeto con este ID
    counter = 0
    item_id = f"{item_type}_{slug}"
    
    while os.path.exists(os.path.join(DIRECTORIO_OBJETOS, item_type, f"{item_id}.json")):
        counter += 1
        item_id = f"{item_type}_{slug}_{counter}"
    
    return item_id


# Constantes para armaduras y otros objetos comunes
ARMOR_CATEGORIES = {
    "light": "Armadura ligera",
    "medium": "Armadura media",
    "heavy": "Armadura pesada"
}

# Definiciones de armaduras estándar del juego
DEFAULT_ARMORS = [
    {
        "name": "Armadura acolchada",
        "type": "armor",
        "rarity": "Common",
        "description": "Armadura hecha de tela acolchada y capas.",
        "properties": {
            "category": "light",
            "base_ac": 11,
            "dex_bonus_limit": None,  # Sin límite
            "strength_required": 0,
            "stealth_disadvantage": True
        },
        "magic": False
    },
    {
        "name": "Armadura de cuero",
        "type": "armor",
        "rarity": "Common",
        "description": "La coraza está hecha de cuero que ha sido endurecido después de hervirlo en aceite. El resto de la armadura está hecha de materiales más blandos y flexibles.",
        "properties": {
            "category": "light",
            "base_ac": 11,
            "dex_bonus_limit": None,  # Sin límite
            "strength_required": 0,
            "stealth_disadvantage": False
        },
        "magic": False
    },
    {
        "name": "Armadura de cuero tachonado",
        "type": "armor",
        "rarity": "Common",
        "description": "Hecha de cuero resistente pero flexible con remaches. Los remaches se añaden para prevenir que las garras y colmillos de los monstruos perforen el cuero.",
        "properties": {
            "category": "light",
            "base_ac": 12,
            "dex_bonus_limit": None,  # Sin límite
            "strength_required": 0,
            "stealth_disadvantage": False
        },
        "magic": False
    },
    {
        "name": "Camisote de mallas",
        "type": "armor",
        "rarity": "Common",
        "description": "Hecha de anillos de metal entrelazados, el camisote de mallas se utiliza entre capas de ropa o cuero.",
        "properties": {
            "category": "medium",
            "base_ac": 13,
            "dex_bonus_limit": 2,
            "strength_required": 0,
            "stealth_disadvantage": False
        },
        "magic": False
    },
    {
        "name": "Cota de escamas",
        "type": "armor",
        "rarity": "Common",
        "description": "Esta armadura consiste en una casaca y polainas de cuero cubiertas con piezas superpuestas de metal, parecidas a las escamas de un pez.",
        "properties": {
            "category": "medium",
            "base_ac": 14,
            "dex_bonus_limit": 2,
            "strength_required": 0,
            "stealth_disadvantage": True
        },
        "magic": False
    },
    {
        "name": "Coraza",
        "type": "armor",
        "rarity": "Common",
        "description": "Esta armadura consiste en un peto y una protección para la espalda hechos de metal, que se conectan con uniones de cuero flexibles.",
        "properties": {
            "category": "medium",
            "base_ac": 14,
            "dex_bonus_limit": 2,
            "strength_required": 0,
            "stealth_disadvantage": False
        },
        "magic": False
    },
    {
        "name": "Media armadura",
        "type": "armor",
        "rarity": "Common",
        "description": "Esta armadura consiste en placas de metal que cubren la mayor parte del cuerpo.",
        "properties": {
            "category": "medium",
            "base_ac": 15,
            "dex_bonus_limit": 2,
            "strength_required": 0,
            "stealth_disadvantage": True
        },
        "magic": False
    },
    {
        "name": "Cota de anillas",
        "type": "armor",
        "rarity": "Common",
        "description": "Esta armadura es de cuero con anillos de metal pesados cosidos.",
        "properties": {
            "category": "heavy",
            "base_ac": 14,
            "dex_bonus_limit": 0,
            "strength_required": 0,
            "stealth_disadvantage": True
        },
        "magic": False
    },
    {
        "name": "Cota de malla",
        "type": "armor",
        "rarity": "Common",
        "description": "Esta armadura está hecha de anillos de metal entrelazados.",
        "properties": {
            "category": "heavy",
            "base_ac": 16,
            "dex_bonus_limit": 0,
            "strength_required": 13,
            "stealth_disadvantage": True
        },
        "magic": False
    },
    {
        "name": "Armadura de bandas",
        "type": "armor",
        "rarity": "Common",
        "description": "Esta armadura está hecha de tiras verticales de metal remachadas a un refuerzo de cuero que se lleva sobre un acolchado de tela.",
        "properties": {
            "category": "heavy",
            "base_ac": 17,
            "dex_bonus_limit": 0,
            "strength_required": 15,
            "stealth_disadvantage": True
        },
        "magic": False
    },
    {
        "name": "Armadura de placas",
        "type": "armor",
        "rarity": "Common",
        "description": "Esta armadura consiste en placas de metal que se ajustan perfectamente sobre un acolchado de cuero.",
        "properties": {
            "category": "heavy",
            "base_ac": 18,
            "dex_bonus_limit": 0,
            "strength_required": 15,
            "stealth_disadvantage": True
        },
        "magic": False
    }
]

# Escudos estándar
DEFAULT_SHIELDS = [
    {
        "name": "Escudo",
        "type": "shield",
        "rarity": "Common",
        "description": "Un escudo está hecho de madera o metal y se lleva en un brazo. Usar un escudo aumenta tu Clase de Armadura en 2.",
        "properties": {
            "base_ac": 2
        },
        "magic": False
    }
]

# Cascos estándar
DEFAULT_HELMETS = [
    {
        "name": "Casco de cuero",
        "type": "helmet",
        "rarity": "Common",
        "description": "Un simple casco hecho de cuero endurecido.",
        "properties": {
            "base_ac": 0  # No proporciona CA por defecto
        },
        "magic": False
    },
    {
        "name": "Casco de metal",
        "type": "helmet",
        "rarity": "Common",
        "description": "Un casco forjado en metal para proteger la cabeza.",
        "properties": {
            "base_ac": 0  # No proporciona CA por defecto
        },
        "magic": False
    }
]

# Anillos estándar
DEFAULT_RINGS = [
    {
        "name": "Anillo común",
        "type": "ring",
        "rarity": "Common",
        "description": "Un simple anillo sin propiedades mágicas.",
        "properties": {},
        "magic": False
    },
    {
        "name": "Anillo de protección",
        "type": "ring",
        "rarity": "Uncommon",
        "description": "Obtienes un bonificador +1 a la CA y a las tiradas de salvación mientras llevas este anillo.",
        "properties": {
            "base_ac": 1,
            "saving_throw_bonus": 1
        },
        "magic": True
    }
]

# Amuletos estándar
DEFAULT_AMULETS = [
    {
        "name": "Amuleto común",
        "type": "amulet",
        "rarity": "Common",
        "description": "Un simple amuleto sin propiedades mágicas.",
        "properties": {},
        "magic": False
    },
    {
        "name": "Amuleto de salud",
        "type": "amulet",
        "rarity": "Uncommon",
        "description": "Mientras llevas este amuleto, tu Constitución es 19. No tiene efecto si tu Constitución ya es 19 o mayor.",
        "properties": {
            "ability_override": {"Constitución": 19}
        },
        "magic": True
    }
]


def initialize_default_items():
    """
    Inicializa los objetos por defecto en el sistema
    """
    # Crear directorio base si no existe
    os.makedirs(DIRECTORIO_OBJETOS, exist_ok=True)
    
    # Crear armaduras por defecto
    for armor_data in DEFAULT_ARMORS:
        item_id = generate_unique_id("armor", armor_data["name"])
        armor_data["id"] = item_id
        armor = Item.from_dict(armor_data)
        save_item(armor)
    
    # Crear escudos por defecto
    for shield_data in DEFAULT_SHIELDS:
        item_id = generate_unique_id("shield", shield_data["name"])
        shield_data["id"] = item_id
        shield = Item.from_dict(shield_data)
        save_item(shield)
    
    # Crear cascos por defecto
    for helmet_data in DEFAULT_HELMETS:
        item_id = generate_unique_id("helmet", helmet_data["name"])
        helmet_data["id"] = item_id
        helmet = Item.from_dict(helmet_data)
        save_item(helmet)
    
    # Crear anillos por defecto
    for ring_data in DEFAULT_RINGS:
        item_id = generate_unique_id("ring", ring_data["name"])
        ring_data["id"] = item_id
        ring = Item.from_dict(ring_data)
        save_item(ring)
    
    # Crear amuletos por defecto
    for amulet_data in DEFAULT_AMULETS:
        item_id = generate_unique_id("amulet", amulet_data["name"])
        amulet_data["id"] = item_id
        amulet = Item.from_dict(amulet_data)
        save_item(amulet)


def calculate_character_ac(character_data, equipped_items):
    """
    Calcula la CA total de un personaje basado en sus estadísticas y objetos equipados
    
    Args:
        character_data (Dict): Datos del personaje
        equipped_items (Dict): Objetos equipados en cada slot
    
    Returns:
        Dict: Información detallada de la CA, incluyendo valor total y contribuciones
    """
    # Obtener estadísticas del personaje
    estadisticas = character_data.get("estadisticas", {})
    dex_mod = (estadisticas.get("Destreza", 10) - 10) // 2
    
    # Inicializar valores
    base_ac = 10  # CA base sin armadura
    ac_items = {}  # Contribución de cada item a la CA
    final_dex_mod = dex_mod  # Modificador de destreza que se aplicará
    
    # Armadura
    armor = equipped_items.get("armor")
    if armor:
        base_ac = armor.get_ac_bonus()
        dex_limit = armor.get_dex_bonus_limit()
        if dex_limit is not None:
            final_dex_mod = min(dex_mod, dex_limit)
        ac_items["armor"] = armor.get_ac_bonus()
    
    # Añadir otros objetos
    for slot, item in equipped_items.items():
        if slot != "armor" and item:
            ac_bonus = item.get_ac_bonus()
            if ac_bonus > 0:
                ac_items[slot] = ac_bonus
    
    # Calcular AC total
    total_ac = base_ac + final_dex_mod + sum(ac_items.values())
    
    # Devolver información detallada
    return {
        "base_ac": base_ac,
        "dex_modifier": final_dex_mod,
        "item_bonuses": ac_items,
        "total_ac": total_ac
    }


# Código de inicialización
if __name__ == "__main__":
    # Inicializar objetos por defecto si no existen
    initialize_default_items()
    
    # Mostrar información de carga
    all_items = load_all_items()
    print("Objetos cargados:")
    for item_type, items in all_items.items():
        print(f"  {ITEM_TYPES.get(item_type, item_type)}: {len(items)} objetos")