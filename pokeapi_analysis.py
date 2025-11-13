"""
🎯 Proyecto: Análisis de Pokémon con la PokeAPI
📚 Objetivo:
Utilizar la API pública https://pokeapi.co/ para responder preguntas sobre tipos,
evoluciones, estadísticas y curiosidades de Pokémon.
"""

import requests
import time

BASE_URL = "https://pokeapi.co/api/v2"

# ---------------------------
# Función auxiliar para peticiones seguras
# ---------------------------
def get_data(url):
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Error al obtener {url}: {e}")
        return None

# ---------------------------
# 🔹 Clasificación por Tipos
# ---------------------------

def pokemon_tipo_fuego_kanto():
    """a) Cuántos Pokémon de tipo fuego existen en Kanto"""
    data = get_data(f"{BASE_URL}/type/fire")
    if not data:
        return
    pokemons = [p["pokemon"]["name"] for p in data["pokemon"]]
    # Solo Kanto (ID 1–151)
    kanto = [p for p in pokemons if get_data(f"{BASE_URL}/pokemon/{p}").get("id", 1000) <= 151]
    print(f"🔥 Pokémon tipo fuego en Kanto: {len(kanto)}")
    print(kanto)

def pokemon_agua_altos():
    """b) Pokémon tipo agua con altura > 10"""
    data = get_data(f"{BASE_URL}/type/water")
    if not data:
        return
    result = []
    for p in data["pokemon"]:
        poke = get_data(p["pokemon"]["url"])
        if poke and poke["height"] > 10:
            result.append(poke["name"])
        time.sleep(0.1)
    print("💧 Pokémon tipo agua con altura > 10:")
    print(result)

# ---------------------------
# 🔹 Evoluciones
# ---------------------------

def cadena_evolutiva(pokemon_inicial="charmander"):
    """a) Cadena evolutiva completa de un Pokémon inicial"""
    species = get_data(f"{BASE_URL}/pokemon-species/{pokemon_inicial}")
    if not species:
        return
    evo_chain_url = species["evolution_chain"]["url"]
    chain = get_data(evo_chain_url)
    if not chain:
        return

    cadena = []
    evo = chain["chain"]
    while evo:
        cadena.append(evo["species"]["name"])
        evo = evo["evolves_to"][0] if evo["evolves_to"] else None

    print(f"🧬 Cadena evolutiva de {pokemon_inicial.capitalize()}: {', '.join(cadena)}")

def electricos_sin_evolucion():
    """b) Pokémon eléctricos sin evoluciones"""
    data = get_data(f"{BASE_URL}/type/electric")
    if not data:
        return
    sin_evo = []
    for p in data["pokemon"]:
        species = get_data(p["pokemon"]["url"].replace("pokemon/", "pokemon-species/"))
        if species and species["evolves_from_species"] is None and not get_data(species["evolution_chain"]["url"])["chain"]["evolves_to"]:
            sin_evo.append(species["name"])
        time.sleep(0.1)
    print("⚡ Pokémon eléctricos sin evoluciones:")
    print(sin_evo)

# ---------------------------
# 🔹 Estadísticas de Batalla
# ---------------------------

def max_ataque_johto():
    """a) Pokémon con mayor ataque base en Johto (ID 152–251)"""
    max_atk = 0
    max_name = ""
    for i in range(152, 252):
        poke = get_data(f"{BASE_URL}/pokemon/{i}")
        if not poke:
            continue
        atk = next(s["base_stat"] for s in poke["stats"] if s["stat"]["name"] == "attack")
        if atk > max_atk:
            max_atk = atk
            max_name = poke["name"]
        time.sleep(0.05)
    print(f"💪 Pokémon con mayor ataque base en Johto: {max_name.capitalize()} ({max_atk})")

def mas_rapido_no_legendario():
    """b) Pokémon con mayor velocidad que no sea legendario"""
    max_speed = 0
    name = ""
    for i in range(1, 500):
        poke = get_data(f"{BASE_URL}/pokemon/{i}")
        if not poke:
            continue
        species = get_data(f"{BASE_URL}/pokemon-species/{poke['name']}")
        if species and not species["is_legendary"]:
            speed = next(s["base_stat"] for s in poke["stats"] if s["stat"]["name"] == "speed")
            if speed > max_speed:
                max_speed = speed
                name = poke["name"]
        time.sleep(0.05)
    print(f"⚡ Pokémon no legendario más rápido: {name.capitalize()} ({max_speed})")

# ---------------------------
# 🔹 Extras
# ---------------------------

def habitat_comun_planta():
    """a) Hábitat más común entre los Pokémon tipo planta"""
    data = get_data(f"{BASE_URL}/type/grass")
    habitats = {}
    for p in data["pokemon"]:
        species = get_data(p["pokemon"]["url"].replace("pokemon/", "pokemon-species/"))
        if species and species["habitat"]:
            nombre_habitat = species["habitat"]["name"]
            habitats[nombre_habitat] = habitats.get(nombre_habitat, 0) + 1
        time.sleep(0.1)
    if habitats:
        hab_mas_comun = max(habitats, key=habitats.get)
        print(f"🌿 Hábitat más común entre tipo planta: {hab_mas_comun}")

def pokemon_mas_liviano():
    """b) Pokémon con el menor peso registrado"""
    min_peso = 999999
    nombre = ""
    for i in range(1, 900):
        poke = get_data(f"{BASE_URL}/pokemon/{i}")
        if poke and poke["weight"] < min_peso:
            min_peso = poke["weight"]
            nombre = poke["name"]
        time.sleep(0.02)
    print(f"🍃 Pokémon más liviano: {nombre.capitalize()} (peso: {min_peso})")

# ---------------------------
# 🔹 Ejecución principal
# ---------------------------
if __name__ == "__main__":
    print("\n=== 🔥 Clasificación por Tipos ===")
    pokemon_tipo_fuego_kanto()
    pokemon_agua_altos()

    print("\n=== 🧬 Evoluciones ===")
    cadena_evolutiva("charmander")
    electricos_sin_evolucion()

    print("\n=== ⚔️ Estadísticas de Batalla ===")
    max_ataque_johto()
    mas_rapido_no_legendario()

    print("\n=== 🌿 Extras ===")
    habitat_comun_planta()
    pokemon_mas_liviano()
