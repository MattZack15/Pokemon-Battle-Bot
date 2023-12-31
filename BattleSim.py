from calctools import CalcDamage, GetMoves, HasStatus, DamageToHPPercent, IsFaster
from poke_env.environment.status import Status
import copy

def SimBattle(Ally, Enemy, battle, randdata, swapincost = 0):
    # Returns a +/- percent health of pokemon
    # +100 means we KO Pokemon without taking any damage
    # -100 means we get KO'ed without dealing any damage
    # Assumes Full HP

    Ally = copy.copy(Ally)
    Enemy = copy.copy(Enemy)

    # Standardize Values
    Ally.set_hp_status(f"{round(Ally.current_hp_fraction * 100)}/100")


    AllyStartingHealth = (Ally.current_hp_fraction * 100)
    EnemyStartingHealth = Enemy.current_hp_fraction * 100

    
    allytoxiccount = 1
    enemytoxiccount = 1

    if Ally.status == Status.TOX:
        allytoxiccount = Ally.status_counter
    if Enemy.status == Status.TOX:
        enemytoxiccount = Enemy.status_counter

    # Cost of swapping in
    TakeDamage(Ally, swapincost)

    AllyBestDamage = DamageToHPPercent(FindStrongestMoveDamage(Ally, Enemy, battle, randdata), Enemy, battle)
    EnemyBestDamage = DamageToHPPercent(FindStrongestMoveDamage(Enemy, Ally, battle, randdata), Ally, battle)
    
    maxSimCount = 20
    while not IsDead(Ally) and not IsDead(Enemy) and maxSimCount > 0:
        if IsFaster(Ally, Enemy, battle):
            TakeDamage(Enemy, AllyBestDamage)
            if IsDead(Enemy):
                break
            TakeDamage(Ally, EnemyBestDamage)
            if IsDead(Ally):
                break
        else:
            TakeDamage(Ally, EnemyBestDamage)
            if IsDead(Ally):
                break
            TakeDamage(Enemy, AllyBestDamage)
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
        print("Max sims reached")
        # Pokemon cant hit eachother return even
        return 0

    # Who won?
    if IsDead(Ally) and IsDead(Enemy):
        return 0
    if IsDead(Ally):
        return -(100 - (EnemyStartingHealth - Enemy.current_hp_fraction * 100))
    else:
        return 100 - (AllyStartingHealth - Ally.current_hp_fraction * 100)

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

    # Negate Change to acount for healing
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
        # Exspected Value
        Damage *= move.accuracy
        # Damage Roll
        Damage *= .925

        if(Damage > bestDamage):
            bestDamage = Damage
    
    return bestDamage

def TakeDamage(pokemon, damagePercent):

    # Calculate new HP value
    currentHP = pokemon.current_hp_fraction * 100
    #print(f"currentHP: {currentHP}")
    #print(f"damagePercent: {damagePercent}")
    newHP = round(currentHP - damagePercent)
    #print(f"newHP: {newHP}")
    if newHP > 100:
        newHP = 100
    elif newHP < 0:
        newHP = 0
    
    # Write to pokemon
    pokemon.set_hp(f"{newHP}/100")

    #print(pokemon.current_hp_fraction * 100)

def IsDead(pokemon):
    if pokemon.current_hp_fraction <= 0:
        return True
    return False