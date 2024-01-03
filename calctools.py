from poke_env.environment import AbstractBattle
from poke_env.player.battle_order import BattleOrder
from poke_env.player.player import Player
from poke_env.environment.move_category import MoveCategory
from poke_env.environment.weather import Weather
from poke_env.environment.pokemon_type import PokemonType
from poke_env.environment.field import Field
import random
import math
from poke_env.data import GenData, to_id_str
import json
from poke_env.environment.move import Move
from poke_env.environment.status import Status
from movetraits import IsContactMove, HasSecondaryEffect, IsWindMove


def CalcDamage(move, attacker, defender, battle, UseSpecificCalc = False):
    
    if(move.category == MoveCategory.STATUS):
        return 0
    
    if UseSpecificCalc:
        
        
        # Use specific calc for RAND BATS
        Damage = CalcBaseDamage(move, attacker, defender, battle)
        Damage *= CalcDamageMultiplier(move, attacker, defender, battle)
        
        #Exspected Hits
        expected_hits = move.expected_hits
        if(move.expected_hits > 1):
            if(attacker.ability == "skilllink"):
                expected_hits = 5
        Damage *= expected_hits
        
        #Special Cases Where calc is completly different
        if move.id.startswith("seismictoss") or move.id.startswith("nightshade"):
            if(Damage != 0):
                return attacker.level
        
        return Damage

    else:
        #Use general calc
        Damage = move.base_power
        Damage *= NaiveDamageMultiplier(move, attacker, defender, battle)
        # Expected Value
        Damage *= move.accuracy
        return  Damage


def STABMultiplier(move, attacker):
    
    if(not attacker.terastallized):
        # Normal Stab bonus
        if(move.type in [attacker.type_1, attacker.type_2]):
            return 1.5
    elif (attacker.terastallized):
        if(move.type == attacker.type_1):
            # Do we get double bonus?  
            #WaterMove: Water -> Tera Water
            if attacker.stab_multiplier == 2:
                return 2
            else:
                # FireMove: Water -> Tera Fire
                return 1.5
        # Check if its any of our original types!
        else:
            species = to_id_str(attacker.species)
            Gen = GenData.from_gen(9)
            dex_entry = Gen.pokedex[species]
            type_1 = PokemonType.from_name(dex_entry["types"][0])
            if len(dex_entry["types"]) == 1:
                type_2 = None
            else:
                type_2 = PokemonType.from_name(dex_entry["types"][1])

            if(move.type in [type_1, type_2]):
                # WaterMove: Water -> Tera Fire
                return 1.5
    
    return 1


def BoostMultiplier(pokemon, stat):
        boostStage = pokemon.boosts[stat]
        
        if(boostStage >= 0):
           return (boostStage+2)/2
        elif(boostStage < 0):
            return 2/(2-boostStage)
        else:
            return None

def NaiveDamageMultiplier(move, attacker, defender, battle):
    mul = 1

    # STAB
    mul *= STABMultiplier(move, attacker)
    
    # Effectiveness
    mul *= defender.damage_multiplier(move)

    #Boosts
    if move.category == MoveCategory.SPECIAL or move.category == MoveCategory.PHYSICAL:
        #Apply Offensive boost
        if(move.category == MoveCategory.SPECIAL):
            mul *= BoostMultiplier(attacker, "spa")
        elif (move.category == MoveCategory.PHYSICAL):
            mul *= BoostMultiplier(attacker, "atk")

    #Weather
    mul *= WeatherMultiplier(battle, move)

    #Abilities
    mul *= AbilityMultiplierDefender(move, defender, attacker)
    mul *= AbilityMultiplierAttacker(move, attacker)

    return mul

def AbilityMultiplierAttacker(move, attacker):
    if(attacker.ability is None):
        return 1
    
    if(attacker.ability == "megalauncher"):
        if move.id in ["aurasphere", "darkpulse", "dragonpulse", "originpulse",	"terrainpulse", "waterpulse"]:
            return 1.5
        else:
            return 1
        
    if attacker.ability == "toughclaws":
        if IsContactMove(move):
            return 1.3
    
    if attacker.ability == "dragonsmaw":
        if move.type == PokemonType.DRAGON:
            return 1.5
    if attacker.ability == "transistor":
        if move.type == PokemonType.ELECTRIC:
            return 1.5
    if attacker.ability == "sheerforce":
        if HasSecondaryEffect(move):
            return 1.3
        
    if attacker.ability == "technician":
        if move.base_power <= 60:
            return 1.5
        
    if attacker.ability == "guts":
        if attacker.status != None:
            if attacker.status in [Status.BRN, Status.PSN, Status.PAR, Status.TOX]:
                return 1.5
    
    return 1


def AbilityMultiplierDefender(move, defender, attacker):
    if attacker.ability == "moldbreaker":
        # Ignore ability - ability
        return 1
    
    if(defender.ability is None):
        return 1
    
    if defender.ability in ["waterabsorb", "stormdrain"]:
        if move.type == PokemonType.WATER:
            return 0
    if defender.ability == "levitate":
        if move.type == PokemonType.GROUND:
            return 0
    if defender.ability == "dryskin":
        if move.type == PokemonType.WATER:
            return 0
        elif move.type == PokemonType.FIRE:
            return 1.25
    if defender.ability == "flashfire":
        if move.type == PokemonType.FIRE:
            return 0
    if defender.ability in ["lightningrod", "motordrive", "voltabsorb"]:
        if move.type == PokemonType.ELECTRIC:
            return 0
    if defender.ability == "sapsipper":
        if move.type == PokemonType.GRASS:
            return 0
    if defender.ability == "wonderguard":
        if defender.damage_multiplier(move) <= 1:
            return 0
    if defender.ability == "iceface":
        if move.category == MoveCategory.PHYSICAL:
            if not defender.species.startswith("eiscuenoice"):
                return 0
    if defender.ability == "windrider":
        if IsWindMove(move):
            return 0
    if defender.ability == "thickfat":
        if move.type in [PokemonType.FIRE, PokemonType.ICE]:
            return .5
    if defender.ability == "icescales":
        if move.category == MoveCategory.SPECIAL:
            return .5
        
    return 1

def GetEffectiveAttackStat(move, attacker, defender, battle):
    #Special Cases
    if(move.id.startswith("bodypress")):
        return GetPokemonStat(attacker, "def", battle)
    if(move.id.startswith("foulplay")):
        return GetPokemonStat(defender, "atk", battle)
    
    if(move.category == MoveCategory.SPECIAL):
        return GetPokemonStat(attacker, "spa", battle)
    elif (move.category == MoveCategory.PHYSICAL):
        return GetPokemonStat(attacker, "atk", battle)
    else:
        return None
    
def GetEffectiveDefenceStat(move, defender, battle):
    if(move.id.startswith("psyshock") or move.id.startswith("psystrike")):
        return GetPokemonStat(defender, "def", battle)
    
    if(move.category == MoveCategory.SPECIAL):
        return GetPokemonStat(defender, "spd", battle)
    elif (move.category == MoveCategory.PHYSICAL):
        return GetPokemonStat(defender, "def", battle)
    else:
        return None

def GetPokemonStat(pokemon, statName, battle):
    # Assumes Random Format
    if(statName == "hp"):
        # Must manualy find hp
        Base = pokemon.base_stats["hp"]
        Level = pokemon.level
        maxhp = math.floor(0.01 * (2 * Base + 31 + math.floor(0.25 * 85)) * Level) + 10 + Level
        
        if pokemon.is_dynamaxed:
            return maxhp * 2
        else:
            return maxhp

    if(pokemon.stats == None or pokemon.stats[statName] == None):
        Stat = CalcUnknowStat(pokemon, statName, battle)
    else:
        Stat = pokemon.stats[statName]

    #With Boosts
    Stat *= BoostMultiplier(pokemon, statName)

    # Speed mods
    if(statName == "spe"):
        if (Status.PAR == pokemon.status):
            Stat *= .5
        if pokemon.item == "choicescarf":
            if not pokemon.is_dynamaxed:
                Stat *= 1.5
        if pokemon.ability == "unburden":
            if pokemon.item == None:
                Stat *= 1.5

    if pokemon.item == "eviolite":
        if statName in ["def", "spd"]:
            Stat *= 1.5
    
    # Sandstorm rock spd boost
    if statName == "spd":
        if Weather.SANDSTORM == battle.weather:
            if PokemonType.ROCK in [pokemon.type_1, pokemon.type_2]:
                Stat *= 1.5

    return Stat

def CalcUnknowStat(enemy, statName, battle):
    # Assumes Random Format
    Base = enemy.base_stats[statName]
    Level = enemy.level

    # Base Stat
    enemyStat = (math.floor(0.01 * (2 * Base + 31 + math.floor(0.25 * 85)) * Level) + 5) * 1

    return enemyStat

def MoveBasePower(move, attacker, defender):
    basepower = move.base_power
    
    if move.id.startswith("waterspout"):
        return basepower * attacker.current_hp_fraction
    if move.id in ["heavyslam", "heatcrash"]:
        if defender.is_dynamaxed:
            return 0
        weight_ratio = (defender.weight / attacker.weight) * 100

        if weight_ratio > 50:
            power = 40
        elif 33.35 <= weight_ratio <= 50:
            power = 60
        elif 25.01 <= weight_ratio <= 33.34:
            power = 80
        elif 20.01 <= weight_ratio <= 25:
            power = 100
        else:
            power = 120
        return power
    if move.id.startswith("grassknot"):
        target_weight_kg = defender.weight
        if target_weight_kg <= 9.9:
            power = 20
        elif 10.0 <= target_weight_kg <= 24.9:
            power = 40
        elif 25.0 <= target_weight_kg <= 49.9:
            power = 60
        elif 50.0 <= target_weight_kg <= 99.9:
            power = 80
        elif 100.0 <= target_weight_kg <= 199.9:
            power = 100
        else:
            power = 120

        return power
    if move.id.startswith("storedpower"):
        boostcount = 1
        for stat in attacker.boosts:
            boost = attacker.boosts[stat]
            if boost > 0:
                boostcount += boost
        return 20 * boostcount


        

    return basepower

def CalcBaseDamage(move, attacker, defender, battle):
    Level = attacker.level
    Power = MoveBasePower(move, attacker, defender)
    A = GetEffectiveAttackStat(move, attacker, defender, battle)
    D = GetEffectiveDefenceStat(move, defender, battle)

    Damage = ((((2*Level/5)+2) * Power * (A/D)) / 50) + 2

    return Damage

def ItemMultiplier(move, attacker, defender):
    
    if(defender.item == "airballoon"):
        if(move.type == PokemonType.GROUND):
            return 0
        
    if (attacker.item == None):
        return 1
    if (attacker.item == "lifeorb"):
        return 1.3
    if (attacker.item == "magnet"):
        if move.type == PokemonType.ELECTRIC:
            return 1.2
    
    # Choice Items
    if not attacker.is_dynamaxed:
        if attacker.item == "choiceband":
            if move.category == MoveCategory.PHYSICAL:
                return 1.5
        if attacker.item == "choicespecs":
            if move.category == MoveCategory.SPECIAL:
                return 1.5

    return 1

    



def CalcDamageMultiplier(move, attacker, defender, battle):
    mul = 1

    # STAB
    mul *= STABMultiplier(move, attacker)
    
    # Effectiveness
    mul *= EffectivenessMultiplier(move, defender, attacker)

    # Weather
    mul *= WeatherMultiplier(battle, move)

    # Terrain
    mul *= TerrainMultiplier(battle, move, attacker, defender)

    #Abilities
    mul *= AbilityMultiplierDefender(move, defender, attacker)
    mul *= AbilityMultiplierAttacker(move, attacker)

    # Move Effects
    mul *= MoveEffectMultiplier(move, attacker, defender)

    #Items
    mul *= ItemMultiplier(move, attacker, defender)
    return mul

def EffectivenessMultiplier(move, defender, attacker):
    if move.id.startswith("freezedry"):
        if(defender.type_1 == PokemonType.WATER or defender.type_2 == PokemonType.WATER):
            return defender.damage_multiplier(move) * 4
    
    if move.id.startswith("multiattack"):
        return defender.damage_multiplier(attacker.type_1)
    
    if attacker.ability == "scrappy":
        if move.type in [PokemonType.NORMAL, PokemonType.FIGHTING]:
            if PokemonType.GHOST in [defender.type_1, defender.type_2]:
                return 1

    return defender.damage_multiplier(move)



def MoveEffectMultiplier(move, attacker, defender):
    movename = move.id

    if attacker.is_dynamaxed:
        return 1

    if movename.startswith("knockoff"):
        if(defender.item != None and defender.item != ""):
            return 1.5
    if movename.startswith("facade"):
        if attacker.status != None:
            if attacker.status in [Status.BRN, Status.PSN, Status.PAR, Status.TOX]:
                return 2
    if movename.startswith("acrobatics"):
        if attacker.item == None or attacker.item == "":
            return 2
    if movename.startswith("firstimpression") or movename.startswith("fakeout"):
        if not attacker.first_turn:
            return 0
    
    return 1

def HasStatus(pokemon):
    # If the pokemon has an unoverridable status return True
    # Ignores Freeze
    if pokemon.status == None:
        return False
    if pokemon.status in [Status.BRN, Status.PSN, Status.PAR, Status.TOX, Status.SLP]:
        return True
        
    return False

def AttackerIsGrounded(attacker):
    if(attacker.item == "airballoon"):
        return False
    if PokemonType.FLYING in [attacker.type_1, attacker.type_2]:
        return False
    if attacker.ability == "levitate":
        return False
    return True

def TerrainMultiplier(battle, move, attacker, defender):
    fields = battle.fields
    
    if fields == None:
        return 1
    elif Field.ELECTRIC_TERRAIN in fields:
        if move.type == PokemonType.ELECTRIC:
            if(AttackerIsGrounded(attacker)):
                if(move.id.startswith("risingvoltage")):
                    return 2*1.3
                else:
                    return 1.3
    elif Field.GRASSY_TERRAIN in fields:
        if move.id.startswith("earthquake"):
            return .5
        if move.type == PokemonType.GRASS:
            if AttackerIsGrounded(attacker):
                return 1.3
    elif Field.MISTY_TERRAIN in fields:
        if move.type == PokemonType.DRAGON:
            if AttackerIsGrounded(attacker) and AttackerIsGrounded(defender):
                return .5
    elif Field.PSYCHIC_TERRAIN in fields:
        mul = 1
        if move.id.startswith("expandingforce"):
            mul *= 1.5
        
        if move.type == PokemonType.PSYCHIC:
            if AttackerIsGrounded(attacker):
                mul *= 1.3
            
        return mul
    
    return 1

            



def WeatherMultiplier(battle, move):
    weather = battle.weather
    
    # Takes in weather and move
    # Returns a float damage Multiplier for that move
    
    if weather == None or len(weather) == 0:
        return 1
    if(len(weather) > 1):
        print(weather)
    
    weather = list(weather.keys())[0]

    if weather == Weather.SUNNYDAY:
        if move.type == PokemonType.FIRE:
            return 1.5
        elif move.type == PokemonType.WATER:
            return .5
    elif weather == Weather.RAINDANCE:
        if move.type == PokemonType.WATER:
            return 1.5
        elif move.type == PokemonType.FIRE:
            return .5
    elif weather == Weather.DESOLATELAND:
        if move.type == PokemonType.FIRE:
            return 1.5
        elif move.type == PokemonType.WATER:
            return 0
    elif weather == Weather.PRIMORDIALSEA:
        if move.type == PokemonType.WATER:
            return 1.5
        elif move.type == PokemonType.FIRE:
            return 0

    return 1
    
def DamageToHPPercent(damage, Defender, battle):
    targetMaxHp = GetPokemonStat(Defender, "hp", battle)
    percent = round((damage / targetMaxHp) * 100, 1)
    return percent

def IsFaster(pokemon1, pokemon2, battle):
    # Returns True if pokemon1 is faster than pokemon2
    # False otherwise
    
    if GetPokemonStat(pokemon1, "spe", battle) > GetPokemonStat(pokemon2, "spe", battle):
        return True
    else:
        return False

def GetMoves(pokemon, battle, randomsets):
    # -> Dict[str, Move]
    # Check If active pokemon, return possible moves
    if pokemon == battle.active_pokemon:
        possibleMoves = battle.available_moves
        attackerMoves = {}
        for move in possibleMoves:
            if pokemon.is_dynamaxed:
                move = move.dynamaxed
                attackerMoves[move.id] = move
            else:
                attackerMoves[move.id] = move
        return attackerMoves

    # If server gives us all moves then we are done
    if len(pokemon.moves) < 4 or pokemon.moves == None:
        # Otherwise find moves from file
        pokemonName = pokemon.species

        #Special Cases for different versions
        if pokemonName.startswith("pikachu"):
            pokemonName = "pikachu"
        elif pokemonName.startswith("mimikyu"):
            pokemonName = "mimikyu"
        elif pokemonName.startswith("eiscue"):
            pokemonName = "eiscue"
        elif pokemonName.startswith("gastrodon"):
            pokemonName = "gastrodon"
        elif pokemonName.startswith("wishiwashi"):
            pokemonName = "wishiwashischool"
        elif pokemonName.startswith("zygardecomplete"):
            pokemonName = "zygarde"
        
        #Check if name is in List
        if(not pokemonName in randomsets.keys()):
            #if not check gmax version
            if(not pokemonName+"gmax" in randomsets.keys()):
                print(f"{pokemonName} has no move entries")
                return pokemon.moves
            else:
                pokemonName += "gmax"
        
        pokemonData = randomsets[pokemonName]
        pokemon_moves = pokemonData.get("moves")

        if(pokemon_moves == None):
            pokemonData = randomsets[pokemonName+"gmax"]
            pokemon_moves = pokemonData.get("moves")

        if(pokemon_moves == None):
            print(pokemonName)

        #Create Move Set
        MoveSet = {}
        for movestr in pokemon_moves:
            moveID = movestr.replace(" ", "").lower()
            NewMove = Move(moveID, 8)
            MoveSet[moveID] = NewMove

        #Return Dynamaxed moves instead
        if pokemon.is_dynamaxed:
            DMoveSet = {}
            for moveID in MoveSet:
                move = MoveSet[moveID]
                move = move.dynamaxed
                DMoveSet[move.id] = move
            
            return DMoveSet

        
        return MoveSet
    
    else:
        
        if pokemon.is_dynamaxed:
            MoveSet = {}
            for moveID in pokemon.moves:
                move = pokemon.moves[moveID]
                move = move.dynamaxed
                MoveSet[move.id] = move
            
            return MoveSet
        
        else:
            return pokemon.moves
        
