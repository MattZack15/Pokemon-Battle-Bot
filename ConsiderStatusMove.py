from poke_env.environment.status import Status
from poke_env.environment.field import Field
from poke_env.environment.move_category import MoveCategory
from calctools import CalcDamage, GetPokemonStat, GetMoves, HasStatus, DamageToHPPercent, IsFaster
from poke_env.environment.pokemon_type import PokemonType
from BestDamageMove import FindStrongestMoveDamage, HasGuaranteedKO
import movetraits 

def ConsiderStatusMove(attacker, defender, battle, randdata):
    # In this function we know
    # We don't want to swap
    # We can't knock them out
    if attacker.is_dynamaxed:
        return None
    
    possiblemoves = GetMoves(attacker, battle, randdata).values()

    statusMoves = []
    for move in possiblemoves:
        if move.category == MoveCategory.STATUS:
            statusMoves.append(move)

    wantedmove = None
    for move in statusMoves:
        if move.id.startswith("bellydrum"):
            # Belly drum if it wont get us knocked out this turn and we can use boost
            if attacker.boosts["atk"] > 1:
                continue
            
            hpestimate = attacker.current_hp_fraction * 100
            hpestimate -= 50
            hpestimate -= DamageToHPPercent(FindStrongestMoveDamage(defender, attacker, battle, randdata), attacker, battle)
            if hpestimate > 0:
                #print(f"{battle.battle_tag}: bellydrum")
                return move
        if move.id.startswith("shellsmash"):
            # Shell smash if we live 2 attacks or live 1 and then can 1 shot after
            if attacker.boosts["atk"] > 1 or attacker.boosts["spa"] > 1:
                continue

            # Check live 2 attacks
            hpestimate = attacker.current_hp_fraction * 100
            hpestimate -= (DamageToHPPercent(FindStrongestMoveDamage(defender, attacker, battle, randdata), attacker, battle)) * 2
            if hpestimate > 0:
                #print(f"{battle.battle_tag}: shellsmash")
                return move
            
            #Check 1 attack + one shot after
            hpestimate = attacker.current_hp_fraction * 100
            hpestimate -= (DamageToHPPercent(FindStrongestMoveDamage(defender, attacker, battle, randdata), attacker, battle))
            if hpestimate > 0:
                if HasGuaranteedKO(attacker, defender, battle, 2):
                    #print(f"{battle.battle_tag}: shellsmash")
                    return move
        if movetraits.IsRecoverMove(move):
            # We only want to heal if we get full value from heal
            # And it wont cause us to start losing the matchup
            hpestimate = attacker.current_hp_fraction * 100
            bestenemydamage = (DamageToHPPercent(FindStrongestMoveDamage(defender, attacker, battle, randdata), attacker, battle))

            if bestenemydamage > 40:
                # Case if it would cause us to start losing matchup
                continue

            if IsFaster(attacker, defender, battle):
                # We faster
                if hpestimate < 50:
                    return move
            else: 
                # We slower
                if hpestimate - bestenemydamage < 50:
                    return move
        if move.id == "toxic":
            # We want to toxic when we are not threatened and we don't threaten a KO
            #Dont toxic if They have a Status
            if HasStatus(defender):
                continue
            #Dont toxic if They are type immune
            if attacker.ability != "corrosion":
                if PokemonType.STEEL in [defender.type_1, defender.type_2]:
                    continue
                elif PokemonType.POISON in [defender.type_1, defender.type_2]:
                    continue
            if defender.ability == "magicbounce":
                continue
            if battle.fields != None:
                if Field.MISTY_TERRAIN in battle.fields:
                    continue

            # Toxic if we do less than 33% Damage
            BestDamage = DamageToHPPercent(FindStrongestMoveDamage(attacker, defender, battle, randdata), defender, battle)
            if BestDamage < 33:
                wantedmove = move
                continue
            
            enemyCanRecover = False
            EnemyMoves = GetMoves(defender, battle, randdata)
            for enemymovename in EnemyMoves:
                if movetraits.IsRecoverMove(EnemyMoves[enemymovename]):
                    enemyCanRecover = True
                    break
            
            if BestDamage < 50 and enemyCanRecover:
                wantedmove = move
                continue
            

    return wantedmove