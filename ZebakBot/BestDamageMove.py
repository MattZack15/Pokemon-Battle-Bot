from calctools import CalcDamage, GetPokemonStat, GetMoves, HasStatus, DamageToHPPercent, IsFaster
import random
import math

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