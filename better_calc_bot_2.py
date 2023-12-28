from poke_env.environment import AbstractBattle
from poke_env.player.battle_order import BattleOrder
from poke_env.player.player import Player
from poke_env.environment.move_category import MoveCategory
from poke_env.environment.pokemon_type import PokemonType
import random
import math
from calctools import CalcDamage, GetPokemonStat, GetMoves
import json
from typing import Optional, Union
from poke_env.ps_client.account_configuration import (
    CONFIGURATION_FROM_PLAYER_COUNTER,
    AccountConfiguration,
)
from poke_env.ps_client.server_configuration import (
    LocalhostServerConfiguration,
    ServerConfiguration,
)
from poke_env.teambuilder.constant_teambuilder import ConstantTeambuilder
from poke_env.teambuilder.teambuilder import Teambuilder

class BetterCalc2(Player):
    def __init__(
        self,
        account_configuration: Optional[AccountConfiguration] = None,
        *,
        avatar: Optional[int] = None,
        battle_format: str = "gen9randombattle",
        log_level: Optional[int] = None,
        max_concurrent_battles: int = 1,
        save_replays: Union[bool, str] = False,
        server_configuration: Optional[ServerConfiguration] = None,
        start_timer_on_battle_start: bool = False,
        start_listening: bool = True,
        ping_interval: Optional[float] = 20.0,
        ping_timeout: Optional[float] = 20.0,
        team: Optional[Union[str, Teambuilder]] = None,
    ):
        # Call the constructor of the superclass (Player)
        super().__init__(
            account_configuration=account_configuration,
            avatar=avatar,
            battle_format=battle_format,
            log_level=log_level,
            max_concurrent_battles=max_concurrent_battles,
            save_replays=save_replays,
            server_configuration=server_configuration,
            start_timer_on_battle_start=start_timer_on_battle_start,
            start_listening=start_listening,
            ping_interval=ping_interval,
            ping_timeout=ping_timeout,
            team=team,
        )

        # Your additional initialization logic here
        file_path = "random-data.json"

        # Open the file and load the JSON data
        with open(file_path, "r") as file:
            data = json.load(file)

        self.randdata = data
    
    def choose_move(self, battle):
        dynamax = battle.can_dynamax
        #print(f"\n{battle.turn}")
        #Best Move is to take the free knockout
        if(True):
            if battle.available_moves:
                if IsFaster(battle.active_pokemon, battle.opponent_active_pokemon, battle):
                    if HasGuaranteedKO(battle.active_pokemon, battle.opponent_active_pokemon, battle):
                        #print(f"Should Pickup Free KO {battle.active_pokemon.species}, {battle.turn}")
                        return self.create_order(BestKOMove(battle.active_pokemon, battle.opponent_active_pokemon, battle))
        
        #Check if want to Swap
        if(battle.available_switches and battle.available_moves):
            if ShouldSwap(battle, self.randdata):
                #Swap
                BestSwap = BestSwitchIn(battle, self.randdata, freeswap= False)
                return self.create_order(BestSwap)
        
        # If the player can attack, it will
        if battle.available_moves:
            
            #Consider Status Moves
            ChosenStatusMove = ConsiderStatusMove(battle.active_pokemon, battle.opponent_active_pokemon, battle, self.randdata)

            if ChosenStatusMove != None:
                return self.create_order(ChosenStatusMove, terastallize= RandomTerastallize(battle))

            best_move = max(GetMoves(battle.active_pokemon, battle, self.randdata).values(), key=lambda move: CalcDamage(move, battle.active_pokemon, battle.opponent_active_pokemon, battle, UseSpecificCalc = True) * move.accuracy)
            return self.create_order(best_move, dynamax= dynamax, terastallize= RandomTerastallize(battle))

        # If no attack is available, a switch will be made
        else:
            if(battle.available_switches):
                BestSwap = BestSwitchIn(battle, self.randdata, True)
                return self.create_order(BestSwap)
            else:
                return self.choose_random_move(battle)
    
    def teampreview(self, battle):
        return "/team 123456"
    
def ConsiderStatusMove(attacker, defender, battle, randdata):
    # In this function we know
    # We don't want to swap
    # We can't knock them out
    possiblemoves = GetMoves(attacker, battle, randdata).values()

    statusMoves = []
    for move in possiblemoves:
        if move.category == MoveCategory.STATUS:
            statusMoves.append(move)

    for move in statusMoves:
        if move.id.startswith("bellydrum"):
            # Belly drum if it wont get us knocked out this turn and we can use boost
            if attacker.boosts["atk"] > 1:
                continue
            
            hpestimate = attacker.current_hp_fraction * 100
            hpestimate -= 50
            hpestimate -= DamageToHPPercent(FindStrongestMoveDamage(defender, attacker, battle, randdata), attacker, battle)
            if hpestimate > 0:
                print(f"{battle.battle_tag}: bellydrum")
                return move
        if move.id.startswith("shellsmash"):
            # Shell smash if we live 2 attacks or live 1 and then can 1 shot after
            if attacker.boosts["atk"] > 1 or attacker.boosts["spa"] > 1:
                continue

            # Check live 2 attacks
            hpestimate = attacker.current_hp_fraction * 100
            hpestimate -= (DamageToHPPercent(FindStrongestMoveDamage(defender, attacker, battle, randdata), attacker, battle)) * 2
            if hpestimate > 0:
                print(f"{battle.battle_tag}: shellsmash")
                return move
            
            #Check 1 attack + one shot after
            hpestimate = attacker.current_hp_fraction * 100
            hpestimate -= (DamageToHPPercent(FindStrongestMoveDamage(defender, attacker, battle, randdata), attacker, battle))
            if hpestimate > 0:
                if HasGuaranteedKO(attacker, defender, battle, 2):
                    print(f"{battle.battle_tag}: shellsmash")
                    return move

    return None

    
def FindStrongestMoveDamage(Attacker, Defender, battle, randdata):
    # Returns EV of damage of strongest move

    attackerMoves = GetMoves(Attacker, battle, randdata)
    
    if(len(attackerMoves) == 0):
        return 0
    bestDamage = -1
    for key in attackerMoves.keys():
        move = attackerMoves[key]
        Damage = CalcDamage(move, Attacker, Defender, battle, UseSpecificCalc = True)
        # Exspected Value
        Damage *= move.accuracy
        # Damage Roll
        Damage *= .925

        if(Damage > bestDamage):
            bestDamage = Damage
    
    return bestDamage

def BestKOMove(attacker, defender, battle):
    hpStat = GetPokemonStat(defender, "hp", battle)
    KOMoves = {}
    for move in battle.available_moves:
       Damage = CalcDamage(move, attacker, defender, battle, True)
       percentDam = math.floor(Damage/hpStat * 100)
       #Check Min Roll
       if(percentDam * .85 > defender.current_hp):
           accuracy = move.accuracy
           if accuracy in KOMoves.keys():
               KOMoves[accuracy].append(move)
           else:
               KOMoves[accuracy] = [move]

    highestaccuracy = 0
    for accuracy in KOMoves.keys():
        if(accuracy > highestaccuracy):
            highestaccuracy = accuracy

    # Return a move with highest accuracy that KOs
    # Random if multiple
    return KOMoves[highestaccuracy][random.randint(0, len(KOMoves[highestaccuracy]) - 1)]
           

def HasGuaranteedKO(attacker, defender, battle, guessedDamageMul = 1):
    hpStat = GetPokemonStat(defender, "hp", battle)
    
    for move in battle.available_moves:
       Damage = CalcDamage(move, attacker, defender, battle, True)
       percentDam = math.floor(Damage/hpStat * 100)

       percentDam *= guessedDamageMul
       #Check Min Roll
       if(percentDam * .85 > defender.current_hp):
           return True
       
    return False

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

def IsFaster(pokemon1, pokemon2, battle):
    # Returns True if pokemon1 is faster than pokemon2
    # False otherwise
    
    if GetPokemonStat(pokemon1, "spe", battle) > GetPokemonStat(pokemon2, "spe", battle):
        return True
    else:
        return False



def DamageToHPPercent(damage, Defender, battle):
    targetMaxHp = GetPokemonStat(Defender, "hp", battle)
    #print(f"{Defender.species}- HP:{targetMaxHp}")
    #print(damage)
    percent = round((damage / targetMaxHp) * 100, 1)
    #print(percent)
    return percent

def SimBattle(Ally, Enemy, battle, randdata, swapincost = 0):
    # Returns a +/- percent health of pokemon
    # +100 means we KO Pokemon without taking any damage
    # -100 means we get KO'ed without dealing any damage
    # Assumes Full HP
    
    AllyStartingHealth = (Ally.current_hp_fraction * 100)
    EnemyStartingHealth = Enemy.current_hp_fraction * 100
    
    AllyCurrentHealth = (Ally.current_hp_fraction * 100) - swapincost
    EnemyCurrentHealth = Enemy.current_hp_fraction * 100

    AllyBestMove = DamageToHPPercent(FindStrongestMoveDamage(Ally, Enemy, battle, randdata), Enemy, battle)
    EnemyBestMove = DamageToHPPercent(FindStrongestMoveDamage(Enemy, Ally, battle, randdata), Ally, battle)
    
    maxSimCount = 10
    while AllyCurrentHealth > 0 and EnemyCurrentHealth > 0 and maxSimCount > 0:
        if IsFaster(Ally, Enemy, battle):
            EnemyCurrentHealth -= AllyBestMove
            if EnemyCurrentHealth <= 0:
                break
            AllyCurrentHealth -= EnemyBestMove
        else:
            AllyCurrentHealth -= EnemyBestMove
            if AllyCurrentHealth <= 0:
                break
            EnemyCurrentHealth -= AllyBestMove

        maxSimCount -= 1

    if(maxSimCount <= 0):
        # Pokemon cant hit eachother return even
        return 0

    # Who won?
    if AllyCurrentHealth <= 0:
        return -(100 - (EnemyStartingHealth - EnemyCurrentHealth))
    else:
        return 100 - (AllyStartingHealth - AllyCurrentHealth)

def ShouldSwap(battle, randdata):
    # We go thorugh all pokemon and see who has the best matchup
    # see if its winning
    # Winning is defined by: I kill them before they kill me
    # Find how much damage I deal, How much damage they deal
    # Who is faster
    #Winning Eval is deteremined by how much health is left on my pokemon when KO
    active_pokemon = battle.active_pokemon
    Enemy = battle.opponent_active_pokemon
    
    if(active_pokemon.is_dynamaxed):
        return False
    
    CurrentEval = SimBattle(active_pokemon, Enemy, battle, randdata)

    CurrentEval += StatIncentive(active_pokemon)

    #print(f"ActiveMon:{active_pokemon.species} Eval: {CurrentEval}")

    TeamEvals = {}
    for pokemon in battle.available_switches:
        #Estimate Swap In Cost
        swapincost = DamageToHPPercent(FindStrongestMoveDamage(Enemy, pokemon, battle, randdata), pokemon, battle)

        newEval = SimBattle(pokemon, Enemy, battle, randdata, swapincost)
        
        #print(f"Possible Swap:{pokemon.species} Eval: {newEval}")
        TeamEvals[newEval] = pokemon
        

    largestEvalIncrease = -1000
    for Eval in TeamEvals.keys():
        newEval = Eval - CurrentEval

        if newEval > largestEvalIncrease:
            largestEvalIncrease = newEval

    if (largestEvalIncrease >= 10):
        # Roll Chance to just not swap scaling with eval size
        #Ex if eval is >50 100 to swap
        # if eval is 10 85% to swap
        swapChance = (3/8)*largestEvalIncrease + (325/4)
        
        # Roll
        roll = random.randint(1, 100)
        if(roll > swapChance):
            return False
        else:
            return True
    return False

def BestSwitchIn(battle, randdata, freeswap):
    BestEval = -1000
    BestPokemon = battle.available_switches[0]

    for pokemon in battle.available_switches:
        
        if(not freeswap):
            #Swap In Cost
            swapincost = DamageToHPPercent(FindStrongestMoveDamage(battle.opponent_active_pokemon, pokemon, battle, randdata), pokemon, battle)
            Eval = SimBattle(pokemon, battle.opponent_active_pokemon, battle, randdata, swapincost)
        else:
            Eval = SimBattle(pokemon, battle.opponent_active_pokemon, battle, randdata)
        if(Eval > BestEval):
            BestEval = Eval
            BestPokemon = pokemon

    return BestPokemon
    

def StatIncentive(active_pokemon):
    # -5 For every 3 net Negative Stat Changes
    statChangesCount = 0
    # boosts is a dict with key-str Stat, Value int Range(-6,6)
    for stat in ["accuracy", "atk", "spa", "def", "spd", "spe"]:
        statChange = active_pokemon.boosts[stat]
        statChangesCount += statChange

    IncentivePerStat = 3
    
    return statChangesCount * IncentivePerStat

