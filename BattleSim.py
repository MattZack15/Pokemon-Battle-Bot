from calctools import CalcDamage, GetMoves, HasStatus, DamageToHPPercent, IsFaster, GetPokemonStat
from poke_env.environment.status import Status
from ConsiderStatusMove import ConsiderStatusMove
from BestDamageMove import FindStrongestMoveDamage
from movetraits import IsRecoverMove
import math
import copy

def SimBattle(Ally, Enemy, battle, randdata, swapincost = 0):
    # Returns a +/- percent health of pokemon
    # +100 means we KO Pokemon without taking any damage
    # -100 means we get KO'ed without dealing any damage
    # Assumes Full HP


    Ally = copy.copy(Ally)
    Ally.boosts = copy.copy(Ally.boosts)

    Enemy = copy.copy(Enemy)
    Enemy.boosts = copy.copy(Enemy.boosts)

    # Standardize Values
    #Ally.set_hp_status(f"{round(Ally.current_hp_fraction * 100)}/100")
    EnemyMaxHP = GetPokemonStat(Enemy, "hp", battle)
    Enemy.set_hp_status(f"{round(Enemy.current_hp_fraction * EnemyMaxHP)}/{EnemyMaxHP}")



    AllyStartingHealth = Ally.current_hp
    EnemyStartingHealth = Enemy.current_hp

    
    allytoxiccount = 1
    enemytoxiccount = 1

    if Ally.status == Status.TOX:
        allytoxiccount = Ally.status_counter
    if Enemy.status == Status.TOX:
        enemytoxiccount = Enemy.status_counter

    # Cost of swapping in
    TakeDamage(Ally, swapincost)
    
    maxSimCount = 35
    while not IsDead(Ally) and not IsDead(Enemy) and maxSimCount > 0:
        
        # Choose Moves for this round
        AllyBestDamage = FindStrongestMoveDamage(Ally, Enemy, battle, randdata)
        EnemyBestDamage = FindStrongestMoveDamage(Enemy, Ally, battle, randdata)

        AllyStatusMove = ConsiderStatusMove(Ally, Enemy, battle, randdata)
        EnemyStatusMove = ConsiderStatusMove(Enemy, Ally, battle, randdata)

        
        if IsFaster(Ally, Enemy, battle):
           # if Ally Move first
            TakeTurn(Ally, Enemy, AllyBestDamage, AllyStatusMove)
            if IsDead(Enemy):
                break
            TakeTurn(Enemy, Ally, EnemyBestDamage, EnemyStatusMove)
            if IsDead(Ally):
                break
        else:
            TakeTurn(Enemy, Ally, EnemyBestDamage, EnemyStatusMove)
            if IsDead(Ally):
                break
            TakeTurn(Ally, Enemy, AllyBestDamage, AllyStatusMove)
            if IsDead(Enemy):
                break

        # End Of Turn Effects
        ApplyEndOfTurnEffects(Ally, allytoxiccount)
        ApplyEndOfTurnEffects(Enemy, enemytoxiccount)
        if Ally.status == Status.TOX:
            allytoxiccount += 1
        if Enemy.status == Status.TOX:
            enemytoxiccount += 1


        maxSimCount -= 1

        
    if(maxSimCount <= 0):
        #print("Max sims reached")
        #print(f"{Ally.species}, {GetMoves(Ally, battle, randdata)}")
        #print(f"{Enemy.species}, {GetMoves(Enemy, battle, randdata)}")
        # Pokemon cant hit eachother return even
        return 0

    # Who won?
    if IsDead(Ally) and IsDead(Enemy):
        return 0
    if IsDead(Ally):
        return -(100 - ((EnemyStartingHealth - Enemy.current_hp)/Enemy.max_hp)*100)
    else:
        return 100 - ((AllyStartingHealth - Ally.current_hp)/Ally.max_hp)*100

def ApplyEndOfTurnEffects(pokemon, toxic_counter):
    # Returns the net HP Change after end of turn effects occur
    change = 0
    if pokemon.item in ["leftovers", "blacksludge"]:
        change += 6.25
    
    if pokemon.status == Status.BRN:
        change -= 6.25

    if pokemon.status == Status.PSN:
        if pokemon.ability == "poisonheal":
            change += 12.5
        else:
            change -= 12.5

    if pokemon.status == Status.TOX:
        if pokemon.ability == "poisonheal":
            change += 12.5
        else:
            change -= (6.25 * toxic_counter)

    # Negate Change to account for healing
    
    #Convert Percent hp to true hp
    change = math.floor(pokemon.max_hp * (change/100))

    TakeDamage(pokemon, -change)

def FindStrongestMoveDamage(Attacker, Defender, battle, randdata):
    # Returns EV of damage of strongest move

    attackerMoves = GetMoves(Attacker, battle, randdata)
    
    if(len(attackerMoves) == 0):
        return 0
    bestDamage = -1
    for key in attackerMoves.keys():
        move = attackerMoves[key]
        Damage = CalcDamage(move, Attacker, Defender, battle, UseSpecificCalc = True)
        # Expected Value
        Damage *= move.accuracy
        # Damage Roll
        Damage *= .925

        if(Damage > bestDamage):
            bestDamage = Damage
    
    return math.floor(bestDamage)

def TakeDamage(pokemon, damage):

    damage = math.floor(damage)
    # Calculate new HP value
    currentHP = pokemon.current_hp
    #print(f"currentHP: {currentHP}")
    #print(f"damage: {damage}")
    newHP = pokemon.current_hp - damage
    #print(f"newHP: {newHP}")
    if newHP > pokemon.max_hp:
        newHP = pokemon.max_hp
    elif newHP < 0:
        newHP = 0
    
    # Write to pokemon
    pokemon.set_hp(f"{newHP}/{pokemon.max_hp}]")
    #print(f"written HP: {pokemon.current_hp}")

def IsDead(pokemon):
    if pokemon.current_hp_fraction <= 0:
        return True
    return False

def SimStatusMove(attacker, defender, statusmove):
    if IsRecoverMove(statusmove):
        # Restore 1/2 hp
        TakeDamage(attacker, -math.floor(attacker.max_hp*.5))
        return
    if statusmove.id == "toxic":
        defender.set_hp_status(f"{defender.current_hp}/{defender.max_hp} TOX")
        if defender.current_hp_fraction * 100 > 100:
            print("Error Setting HP")
            print(defender.current_hp_fraction * 100)
        return
    if statusmove.id == "bellydrum":
        TakeDamage(attacker, math.floor(attacker.max_hp*.5))
        attacker.boost("atk", 6)
    if statusmove.id == "shellsmash":
        attacker.boost("atk", 2)
        attacker.boost("spa", 2)
        attacker.boost("spe", 2)
        attacker.boost("def", -1)
        attacker.boost("spd", -1)


def TakeTurn(attacker, defender, bestdamage, statusmove):
    
    if statusmove != None:
        SimStatusMove(attacker, defender, statusmove)
    else:
        TakeDamage(defender, bestdamage)