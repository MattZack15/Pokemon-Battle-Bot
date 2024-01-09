import asyncio
import time
import basic_bots
import better_calc_bot
from ZebakBot.zebak_bot_a import ZebakBot as ZebakBotA
from ZebakBot.zebak_bot_b import ZebakBot as ZebakBotB
from poke_env import AccountConfiguration, ShowdownServerConfiguration
from poke_env.player import RandomPlayer
from teams import randomteam, clickdamageteam, swappingteam, jteam, herosteam

#Formats
#gen9nationaldexag
#gen8randombattle
#gen8randombattle

async def main():
    # "Online" "Sims"
    mode = "Sims"
    
    if mode == "Online":
        concurrent_battles = 1
    elif mode == "Sims":
        concurrent_battles = 4
    
    # We create a random player
    if(mode == "Sims"):
        Bot1 = ZebakBotA(
            battle_format="gen8randombattle",
            max_concurrent_battles= concurrent_battles,
            #account_configuration=AccountConfiguration("RoboDougRoll", "destroyhumans"),
            #server_configuration=ShowdownServerConfiguration,
            #team= clickdamageteam,
        )
    BetterBot = ZebakBotB(
        battle_format="gen8randombattle",
        max_concurrent_battles= concurrent_battles,
        #account_configuration=AccountConfiguration("RoboDougRoll", "destroyhumans"),
        #server_configuration=ShowdownServerConfiguration,
        #team= jteam,
    )

    start = time.time()


    if mode == "Sims":
        testCount = 100
        await BetterBot.battle_against(Bot1, n_battles=testCount)

    
    #data = CollectData(BetterBot)
    #data = CollectData(BetterBot, data)
    #PrintData(data, "./CollectedData/RandWinrates.txt")
    

    # Sending challenges to 'your_username'
    #await BetterBot.send_challenges("Saul2Paul", n_challenges=1)

    # Accepting one challenge from any user
    #await BetterBot.accept_challenges(None, 1, packed_team=swappingteam)

    # Accepting three challenges from 'your_username'
    # await player.accept_challenges('your_username', 3)

    if(mode == "Online"):
        #Number of Requested games
        TotalGames = 100
        GamesCount = 0
        while(GamesCount < TotalGames):
            await BetterBot.ladder(1)
            time.sleep(3)
            GamesCount += 1
            print("\n"*50)
            print(
                "Bot won %d / %d battles \nWinrate %.1f%%"
                %(
                    BetterBot.n_won_battles, GamesCount, BetterBot.n_won_battles/GamesCount * 100
                )
            )
            newrating = list(BetterBot.battles.items())[-1][1].rating
            f = open("./CollectedData/highest_rating.txt", "r")
            oldrating = int(f.readline())
            f.close()
            
            if newrating > oldrating:
                f = open("./CollectedData/highest_rating.txt", "w")
                f.writelines(str(newrating))
                f.close()

            
            print(f"Rating: {newrating}")

    
    

    # Print the rating of the player and its opponent after each battle
    #for battle in max_damage_player.battles.values():
    #    print(battle.rating, battle.opponent_rating)
    if(mode == "Sims"):
        print(
            "Bot2 won %d / %d battles [this took %f seconds]\nWinrate %.1f%%"
            %(
                BetterBot.n_won_battles, testCount, time.time() - start, BetterBot.n_won_battles/testCount * 100
            )
        )

def CollectData(bot, dict = {}):
    # {pokemonName: [Wins, Loses]}
    mons = dict

    for battleID in bot.battles.keys():
        abstBattle = bot.battles[battleID]
        won = abstBattle.won
        teamDict = abstBattle.team
        
        for pokemonkey in teamDict:
            Pokemon = teamDict[pokemonkey]


            pokemonName = Pokemon.species
            #Correct Names
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

            if(pokemonName in mons):
                if won:
                    mons[pokemonName][0] = mons[pokemonName][0] + 1
                else:
                    mons[pokemonName][1] = mons[pokemonName][1] + 1
            else:
                if won:
                    mons[pokemonName] = [1, 0]
                else:
                    mons[pokemonName] = [0, 1]

    return mons

def PrintData(dict, filename):
    winrates = {}
    for pokemon in dict:
        winrate = round((dict[pokemon][0] / (dict[pokemon][0] + dict[pokemon][1])) * 100, 1)
        winrates[pokemon] = winrate

    winrates = sorted(winrates.items(), key=lambda x:x[1], reverse= True)

    with open(filename, 'w') as file:
        # Write each line to the file
        for data in winrates:
            line = f"{data[0]}: {data[1]}%\n"
            file.write(line)
        




if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())