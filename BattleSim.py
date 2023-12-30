from calctools import CalcDamage, GetMoves, HasStatus, DamageToHPPercent, IsFaster
from poke_env.environment.status import Status

def SimBattle(Ally, Enemy, battle, randdata, swapincost = 0):
    # Returns a +/- percent health of pokemon
    # +100 means we KO Pokemon without taking any damage
    # -100 means we get KO'ed without dealing any damage
    # Assumes Full HP
    
    AllyStartingHealth = (Ally.current_hp_fraction * 100)
    EnemyStartingHealth = Enemy.current_hp_fraction * 100

    
    allytoxiccount = 1
    enemytoxiccount = 1

    if Ally.status == Status.TOX:
        allytoxiccount = Ally.status_counter
    if Enemy.status == Status.TOX:
        enemytoxiccount = Enemy.status_counter

    
    AllyCurrentHealth = (Ally.current_hp_fraction * 100) - swapincost
    EnemyCurrentHealth = Enemy.current_hp_fraction * 100

    AllyBestMove = DamageToHPPercent(FindStrongestMoveDamage(Ally, Enemy, battle, randdata), Enemy, battle)
    EnemyBestMove = DamageToHPPercent(FindStrongestMoveDamage(Enemy, Ally, battle, randdata), Ally, battle)
    
    maxSimCount = 20
    while AllyCurrentHealth > 0 and EnemyCurrentHealth > 0 and maxSimCount > 0:
        if IsFaster(Ally, Enemy, battle):
            EnemyCurrentHealth -= AllyBestMove
            if EnemyCurrentHealth <= 0:
                break
            AllyCurrentHealth -= EnemyBestMove
            if AllyCurrentHealth <= 0:
                break
        else:
            AllyCurrentHealth -= EnemyBestMove
            if AllyCurrentHealth <= 0:
                break
            EnemyCurrentHealth -= AllyBestMove
            if EnemyCurrentHealth <= 0:
                break

        # End Of Turn Effects
        AllyCurrentHealth += ApplyEndOfTurnEffects(Ally, allytoxiccount)
        EnemyCurrentHealth += ApplyEndOfTurnEffects(Enemy, enemytoxiccount)
        if Ally.status == Status.TOX:
            allytoxiccount += 1
        if Enemy.status == Status.TOX:
            enemytoxiccount += 1


        maxSimCount -= 1

    if(maxSimCount <= 0):
        # Pokemon cant hit eachother return even
        return 0

    # Who won?
    if AllyCurrentHealth <= 0 and EnemyCurrentHealth <= 0:
        return 0
    if AllyCurrentHealth <= 0:
        return -(100 - (EnemyStartingHealth - EnemyCurrentHealth))
    else:
        return 100 - (AllyStartingHealth - AllyCurrentHealth)

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

    return change

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