#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilidades para el cálculo de Clase de Armadura (CA) en la aplicación D&D Combat Manager.
"""

# Constantes para tipos de armadura
TIPOS_ARMADURA = [
    "Sin armadura",
    "Armadura ligera", 
    "Armadura media", 
    "Armadura pesada"
]

# Definiciones de armaduras con sus valores base y límites de modificador
ARMADURAS = {
    "Sin armadura": {
        "tipo": "Sin armadura",
        "valor_base": 10,
        "limite_mod": None,  # Sin límite para modificador de destreza
        "requiere_competencia": False
    },
    "Armadura acolchada": {
        "tipo": "Armadura ligera",
        "valor_base": 11,
        "limite_mod": None,  # Sin límite para modificador de destreza
        "requiere_competencia": True
    },
    "Armadura de cuero": {
        "tipo": "Armadura ligera",
        "valor_base": 11,
        "limite_mod": None,
        "requiere_competencia": True
    },
    "Armadura de cuero tachonado": {
        "tipo": "Armadura ligera",
        "valor_base": 12,
        "limite_mod": None,
        "requiere_competencia": True
    },
    "Camisote de mallas": {
        "tipo": "Armadura media",
        "valor_base": 13,
        "limite_mod": 2,  # Límite de +2 para modificador de destreza
        "requiere_competencia": True
    },
    "Cota de escamas": {
        "tipo": "Armadura media",
        "valor_base": 14,
        "limite_mod": 2,
        "requiere_competencia": True
    },
    "Coraza": {
        "tipo": "Armadura media",
        "valor_base": 14,
        "limite_mod": 2,
        "requiere_competencia": True
    },
    "Media armadura": {
        "tipo": "Armadura media",
        "valor_base": 15,
        "limite_mod": 2,
        "requiere_competencia": True
    },
    "Cota de anillas": {
        "tipo": "Armadura pesada",
        "valor_base": 14,
        "limite_mod": 0,  # No se aplica modificador de destreza
        "requiere_competencia": True
    },
    "Cota de malla": {
        "tipo": "Armadura pesada",
        "valor_base": 16,
        "limite_mod": 0,
        "requiere_competencia": True
    },
    "Armadura de bandas": {
        "tipo": "Armadura pesada",
        "valor_base": 17,
        "limite_mod": 0,
        "requiere_competencia": True
    },
    "Armadura de placas": {
        "tipo": "Armadura pesada",
        "valor_base": 18,
        "limite_mod": 0,
        "requiere_competencia": True
    }
}

# Escudos
ESCUDOS = {
    "Sin escudo": {
        "bonus_ca": 0,
        "requiere_competencia": False
    },
    "Escudo": {
        "bonus_ca": 2,
        "requiere_competencia": True
    }
}

def calcular_ca(armadura_nombre, mod_destreza, escudo_nombre=None, bonus_adicional=0):
    """
    Calcula la Clase de Armadura (CA) basada en la armadura, el modificador de destreza y los bonus adicionales
    
    Args:
        armadura_nombre (str): Nombre de la armadura equipada
        mod_destreza (int): Modificador de destreza del personaje
        escudo_nombre (str, optional): Nombre del escudo equipado. Por defecto None.
        bonus_adicional (int, optional): Cualquier bonus adicional a la CA. Por defecto 0.
    
    Returns:
        dict: Diccionario con detalles del cálculo de CA
    """
    # Obtener datos de la armadura
    armadura = ARMADURAS.get(armadura_nombre, ARMADURAS["Sin armadura"])
    valor_base = armadura.get("valor_base", 10)
    tipo = armadura.get("tipo", "Sin armadura")
    limite_mod = armadura.get("limite_mod", None)
    
    # Aplicar modificador de destreza según tipo de armadura
    mod_aplicado = mod_destreza
    if limite_mod is not None:
        mod_aplicado = min(mod_destreza, limite_mod)
    
    # Calcular CA base
    ca_base = valor_base + mod_aplicado
    
    # Añadir bonus de escudo
    bonus_escudo = 0
    if escudo_nombre:
        escudo = ESCUDOS.get(escudo_nombre, ESCUDOS["Sin escudo"])
        bonus_escudo = escudo.get("bonus_ca", 0)
    
    # Calcular CA total
    ca_total = ca_base + bonus_escudo + bonus_adicional
    
    # Devolver diccionario completo con detalles del cálculo
    return {
        "nombre": armadura_nombre,
        "tipo": tipo,
        "valor_base": valor_base,
        "mod_destreza": mod_destreza,
        "mod_aplicado": mod_aplicado,
        "escudo": escudo_nombre or "Sin escudo",
        "bonus_escudo": bonus_escudo,
        "bonus_adicional": bonus_adicional,
        "ca_base": ca_base,
        "ca_total": ca_total
    }

def obtener_ca_maxima_posible(mod_destreza, competencias=None):
    """
    Determina la mejor combinación posible de armadura y escudo para un personaje
    basado en sus competencias y modificador de destreza
    
    Args:
        mod_destreza (int): Modificador de destreza del personaje
        competencias (list, optional): Lista de competencias con armaduras. Por defecto None.
    
    Returns:
        dict: Diccionario con la mejor combinación y CA resultante
    """
    if competencias is None:
        competencias = []
    
    # Convertir a conjunto para búsquedas más rápidas
    comp_set = set(competencias)
    
    mejor_ca = 0
    mejor_combinacion = {
        "armadura": "Sin armadura",
        "escudo": "Sin escudo",
        "ca_total": 10 + mod_destreza  # CA base sin armadura
    }
    
    # Comprobar cada combinación de armadura y escudo
    for armadura_nombre, armadura_datos in ARMADURAS.items():
        # Verificar si requiere competencia y si el personaje la tiene
        tipo_armadura = armadura_datos.get("tipo", "Sin armadura")
        if tipo_armadura == "Sin armadura":
            requiere_comp = False
        else:
            requiere_comp = armadura_datos.get("requiere_competencia", True)
            
        # Si requiere competencia, verificar que el personaje la tenga
        if requiere_comp and not any(tipo in comp_set for tipo in ["Ligeras", "Medias", "Pesadas"]):
            continue
            
        # Para armaduras específicas, verificar competencia con el tipo
        if tipo_armadura == "Armadura ligera" and "Ligeras" not in comp_set:
            continue
        elif tipo_armadura == "Armadura media" and "Medias" not in comp_set:
            continue
        elif tipo_armadura == "Armadura pesada" and "Pesadas" not in comp_set:
            continue
        
        # Para cada escudo
        for escudo_nombre, escudo_datos in ESCUDOS.items():
            # Verificar competencia con escudo
            if escudo_datos.get("requiere_competencia", False) and "Escudos" not in comp_set:
                continue
            
            # Calcular CA para esta combinación
            resultado = calcular_ca(armadura_nombre, mod_destreza, escudo_nombre)
            
            # Actualizar mejor combinación si es mejor
            if resultado["ca_total"] > mejor_ca:
                mejor_ca = resultado["ca_total"]
                mejor_combinacion = {
                    "armadura": armadura_nombre,
                    "escudo": escudo_nombre,
                    "ca_total": resultado["ca_total"]
                }
    
    return mejor_combinacion

def sugerir_equipo_optimo(personaje):
    """
    Sugiere el mejor equipo posible para un personaje basado en sus estadísticas y competencias
    
    Args:
        personaje (dict): Datos del personaje
    
    Returns:
        dict: Sugerencias de equipamiento para maximizar CA
    """
    # Obtener modificador de destreza
    estadisticas = personaje.get("estadisticas", {})
    valor_destreza = estadisticas.get("Destreza", 10)
    mod_destreza = (valor_destreza - 10) // 2
    
    # Obtener competencias con armaduras
    competencias = personaje.get("comp_armaduras", [])
    
    # Obtener mejor combinación
    mejor_combo = obtener_ca_maxima_posible(mod_destreza, competencias)
    
    # Preparar sugerencia detallada
    sugerencia = {
        "equipo_recomendado": {
            "armadura": mejor_combo["armadura"],
            "escudo": mejor_combo["escudo"],
        },
        "ca_resultante": mejor_combo["ca_total"],
        "explicacion": f"Para maximizar tu CA, te recomendamos usar {mejor_combo['armadura']}"
    }
    
    if mejor_combo["escudo"] != "Sin escudo":
        sugerencia["explicacion"] += f" junto con un {mejor_combo['escudo']}"
    
    sugerencia["explicacion"] += f". Con tu modificador de Destreza de {'+' if mod_destreza >= 0 else ''}{mod_destreza}, alcanzarás una CA total de {mejor_combo['ca_total']}."
    
    # Añadir consejos adicionales
    if mod_destreza > 2 and "Ligeras" in competencias:
        sugerencia["consejos"] = ["Con tu alto modificador de Destreza, las armaduras ligeras son más efectivas que las medias o pesadas."]
    elif mod_destreza <= 0 and "Pesadas" in competencias:
        sugerencia["consejos"] = ["Con tu bajo modificador de Destreza, las armaduras pesadas son la mejor opción."]
    
    return sugerencia

# Ejemplo de uso
if __name__ == "__main__":
    # Ejemplo de un personaje
    personaje_ejemplo = {
        "nombre": "Thorin",
        "clase": "Guerrero",
        "estadisticas": {
            "Fuerza": 16,
            "Destreza": 14,
            "Constitución": 15,
            "Inteligencia": 10,
            "Sabiduría": 12,
            "Carisma": 8
        },
        "comp_armaduras": ["Ligeras", "Medias", "Pesadas", "Escudos"]
    }
    
    # Calcular CA con diferentes armaduras
    print("= Ejemplos de cálculo de CA =")
    
    mod_destreza = (personaje_ejemplo["estadisticas"]["Destreza"] - 10) // 2
    print(f"Modificador de Destreza: {mod_destreza}")
    
    sin_armadura = calcular_ca("Sin armadura", mod_destreza)
    print(f"Sin armadura: {sin_armadura['ca_total']} (Base {sin_armadura['valor_base']} + Mod {sin_armadura['mod_aplicado']})")
    
    armadura_ligera = calcular_ca("Armadura de cuero tachonado", mod_destreza)
    print(f"Cuero tachonado: {armadura_ligera['ca_total']} (Base {armadura_ligera['valor_base']} + Mod {armadura_ligera['mod_aplicado']})")
    
    armadura_media = calcular_ca("Cota de escamas", mod_destreza)
    print(f"Cota de escamas: {armadura_media['ca_total']} (Base {armadura_media['valor_base']} + Mod {armadura_media['mod_aplicado']})")
    
    armadura_pesada = calcular_ca("Armadura de placas", mod_destreza)
    print(f"Armadura de placas: {armadura_pesada['ca_total']} (Base {armadura_pesada['valor_base']} + Mod {armadura_pesada['mod_aplicado']})")
    
    # Con escudo
    con_escudo = calcular_ca("Armadura de placas", mod_destreza, "Escudo")
    print(f"Armadura de placas + Escudo: {con_escudo['ca_total']} (Base {con_escudo['valor_base']} + Mod {con_escudo['mod_aplicado']} + Escudo {con_escudo['bonus_escudo']})")
    
    # Sugerir equipamiento óptimo
    print("\n= Sugerencia de equipamiento =")
    sugerencia = sugerir_equipo_optimo(personaje_ejemplo)
    print(f"Equipo recomendado: {sugerencia['equipo_recomendado']['armadura']} y {sugerencia['equipo_recomendado']['escudo']}")
    print(f"CA resultante: {sugerencia['ca_resultante']}")
    print(f"Explicación: {sugerencia['explicacion']}")