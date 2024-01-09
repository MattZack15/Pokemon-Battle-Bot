from poke_env.environment import AbstractBattle
from poke_env.player.battle_order import BattleOrder
from poke_env.player.player import Player
from poke_env.environment.move_category import MoveCategory
from poke_env.environment.pokemon_type import PokemonType
from poke_env.environment.weather import Weather
import random
import math
from calctools import CalcDamage, WeatherMultiplier


class MaxBaseDamage(Player):
    def choose_move(self, battle):
        # If the player can attack, it will
        if battle.available_moves:
            # Finds the best move among available ones
            best_move = max(battle.available_moves, key=lambda move: move.base_power)
            return self.create_order(best_move)

        # If no attack is available, a random switch will be made
        else:
            return self.choose_random_move(battle)
    
class Random2(Player):
    # Switches Are Less Likely
    
    def choose_move(self, battle):
        # If the player can attack, it will
        if battle.available_moves:
            canSwap = False
            
            moveCount = len(battle.available_moves)
            if battle.available_switches:
                canSwap = True
                moveCount += 1
            
            chosenMove = random.randint(0, moveCount-1)

            if(canSwap and chosenMove == moveCount-1):
                # Switch
                switches = [BattleOrder(switch) for switch in battle.available_switches]
                return switches[random.randint(0, len(switches)-1)]
            else:
                return self.create_order(battle.available_moves[chosenMove], terastallize= RandomTerastallize(battle), dynamax=RandomDynamax(battle))
            

        # If no attack is available, a random switch will be made
        else:
            return self.choose_random_move(battle)
        
    def teampreview(self, battle):
        return "/team 123456"


def RandomTerastallize(battle):
        # Becomes more likely the less pokemon we have
        # Always Tera if last pokemon
        
        if battle.can_tera:
            if battle.available_switches:
                teraRoll = random.randint(0, len(battle.available_switches)*2)
                if(teraRoll == 0):
                    return True
                else:
                    return False
            else:
                return True
        else:
            return False

    
def RandomDynamax(battle):
        # Becomes more likely the less pokemon we have
        
        if battle.can_dynamax:
            if battle.available_switches:
                Roll = random.randint(0, len(battle.available_switches)*2)
                if(Roll == 0):
                    return True
                else:
                    return False
            else:
                return True
        else:
            return False


class SmartDamage(Player):
    def choose_move(self, battle):
        dynamax = battle.can_dynamax
        
        # If the player can attack, it will
        if battle.available_moves:
        
            best_move = max(battle.available_moves, key=lambda move: CalcDamage(move, battle.active_pokemon, battle.opponent_active_pokemon, battle))
            return self.create_order(best_move, dynamax= dynamax, terastallize= RandomTerastallize(battle))

        # If no attack is available, a random switch will be made
        else:
            return self.choose_random_move(battle)
        
    def teampreview(self, battle):
        return "/team 123456"

def EvalTypeDefence(Ally, Enemy):
    #-10 Terrible Matchup, 0 Even, +10 Goated Matchup
    
    # Both Evals are in worst case
    weaknessEval = 0
    resistanceEval = 0

    dam = Ally.damage_multiplier(Enemy.type_1)
    # Damage we take from enemy first type
    if(dam == 1):
        pass
    elif(dam == 2):
        weaknessEval = -5
    elif(dam > 2):
        weaknessEval = -10
    else:
        # Resist Type
        if(dam == .5):
            resistanceEval = 5
        elif(dam < .5):
            resistanceEval = 10
        
    if Enemy.type_2:

        dam = Ally.damage_multiplier(Enemy.type_2)
        if(dam == 1):
            resistanceEval = 0
        elif(dam == 2):
            if(weaknessEval > -5):
                weaknessEval = -5
        elif(dam > 2):
            weaknessEval = -10
        else:
            # Resist Type
            if(dam == .5):
                if(resistanceEval > 5):
                    resistanceEval = 5
            elif(dam < .5):
                if(resistanceEval >= 10):
                    resistanceEval = 15


    if(weaknessEval < 0):
        return weaknessEval
    else:
        return resistanceEval
            

def EvalMatchup(ally, enemy):
    # Default value assumes all moves resist
    Eval = -5

    # Does it have a super effective move?
    for key in ally.moves:
        move = ally.moves[key]
        if(move.base_power > 0):
            moveDamMul = enemy.damage_multiplier(move)
            if(moveDamMul == 1):
                if(Eval < 0):
                    Eval = 0
            elif moveDamMul == 2:
                if(Eval < 5):
                    Eval = 5
            elif moveDamMul > 2:
                Eval = 10
                break
    
    # How good is the type matchup?
    Eval += EvalTypeDefence(ally, enemy)

    #print(f"{ally.species} Eval: {Eval}")
    return Eval


def ShouldSwap(battle):
    # Checks to see if any swap would reselt in an eval change of 10+
    enemy = battle.opponent_active_pokemon
    BaseEval = EvalMatchup(battle.active_pokemon, enemy)

    # -5 For every 3 net Negative Stat Changes
    statChangesCount = 0
    # boosts is a dict with key-str Stat, Value int Range(-6,6)
    for stat in ["accuracy", "atk", "spa", "def", "spd"]:
        statChange = battle.active_pokemon.boosts[stat]
        if(statChange != 0):
            #print(f"{stat} - {statChange}")
            pass
        statChangesCount += battle.active_pokemon.boosts[stat]

    if statChangesCount > -3:
        pass
    else:
        #print(f"Base Eval {BaseEval}")
        #print(statChangesCount)
        BaseEval += -5*round((-statChangesCount)/3)
        #print(f"New Eval {BaseEval}")
        pass

    # Less change to swap if dynamaxed
    if(battle.active_pokemon.is_dynamaxed):
        BaseEval += 10
    
    # Bonus if we are faster
    #Calc Enemy Speed
    Base = battle.opponent_active_pokemon.base_stats["spe"]
    Level = battle.opponent_active_pokemon.level
    enemySpeed = (math.floor(0.01 * (2 * Base + 31 + math.floor(0.25 * 84)) * Level) + 5) * 1
    
    if battle.active_pokemon.stats["spe"] > enemySpeed:
        # Even better if enemy is real low
        if(battle.opponent_active_pokemon.current_hp_fraction < .2):
            BaseEval += 5
            pass

    for teamMember in battle.available_switches:
        if EvalMatchup(teamMember, enemy) - BaseEval >= 10:
            return True
    return False


class SwitchingPlayer(Player):
    def choose_move(self, battle):
        dynamax = battle.can_dynamax
        
        #Check if want to Swap
        if(battle.available_switches):
            if ShouldSwap(battle):
                #Swap
                BestSwap = max(battle.available_switches, key=lambda self: EvalMatchup(self, battle.opponent_active_pokemon))
                return self.create_order(BestSwap)
        
        # If the player can attack, it will
        if battle.available_moves:
        
            best_move = max(battle.available_moves, key=lambda move: CalcDamage(move, battle.active_pokemon, battle.opponent_active_pokemon, battle))
            return self.create_order(best_move, dynamax= dynamax, terastallize= RandomTerastallize(battle))

        # If no attack is available, a switch will be made
        else:
            if(battle.available_switches):
                BestSwap = max(battle.available_switches, key=lambda self: EvalMatchup(self, battle.opponent_active_pokemon))
                return self.create_order(BestSwap)
            else:
                return self.choose_random_move(battle)
    
    def teampreview(self, battle):
        return "/team 123456"