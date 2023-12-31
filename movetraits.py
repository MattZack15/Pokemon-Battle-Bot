def IsContactMove(move):
    if move.id in ["accelerock", "acrobatics", "aerialace", "anchorshot", "aquajet", "aquastep", "aquatail", "armthrust", "assurance", "astonish", "avalanche", "axekick", "behemothbash", "behemothblade", "bide", "bind", "bite", "bitterblade", "blazekick", "bodypress", "bodyslam", "boltbeak", "boltstrike", "bounce", "branchpoke", "bravebird", "breakingswipe", "brickbreak", "brutalswing", "bugbite", "bulletpunch", "catastropika", "ceaselessedge", "chipaway", "circlethrow", "clamp", "closecombat", "collisioncourse", "cometpunch", "comeuppance", "constrict", "counter", "covet", "crabhammer", "crosschop", "crosspoison", "crunch", "crushclaw", "crushgrip", "cut", "darkestlariat", "dig", "direclaw", "dive", "dizzypunch", "doubleedge", "doublehit", "doubleironbash", "doublekick", "doubleshock", "doubleslap", "dragonascent", "dragonclaw", "dragonhammer", "dragonrush", "dragontail", "drainingkiss", "drainpunch", "drillpeck", "drillrun", "dualchop", "dualwingbeat", "dynamicpunch", "electrodrift", "endeavor", "extremespeed", "facade", "fakeout", "falsesurrender", "falseswipe", "feintattack", "fellstinger", "firefang", "firelash", "firepunch", "firstimpression", "fishiousrend", "flail", "flamecharge", "flamewheel", "flareblitz", "flipturn", "floatyfall", "fly", "flyingpress", "focuspunch", "forcepalm", "foulplay", "frustration", "furyattack", "furycutter", "furyswipes", "geargrind", "gigaimpact", "glaiverush", "grassknot", "grassyglide", "guillotine", "gyroball", "hammerarm", "hardpress", "headbutt", "headcharge", "headlongrush", "headsmash", "heartstamp", "heatcrash", "heavyslam", "highhorsepower", "highjumpkick", "holdback", "hornattack", "horndrill", "hornleech", "hyperdrill", "hyperfang", "iceball", "icefang", "icehammer", "icepunch", "icespinner", "infestation", "ironhead", "irontail", "jawlock", "jetpunch", "jumpkick", "karatechop", "knockoff", "kowtowcleave", "lashout", "lastresort", "leafblade", "leechlife", "letssnuggleforever", "lick", "liquidation", "lowkick", "lowsweep", "lunge", "machpunch", "maliciousmoonsault", "megahorn", "megakick", "megapunch", "metalclaw", "meteormash", "mightycleave", "mortalspin", "multiattack", "needlearm", "nightslash", "nuzzle", "outrage", "payback", "peck", "petaldance", "phantomforce", "plasmafists", "playrough", "pluck", "poisonfang", "poisonjab", "poisontail", "populationbomb", "pounce", "pound", "powertrip", "poweruppunch", "powerwhip", "psyblade", "psychicfangs", "psyshieldbash", "pulverizingpancake", "punishment", "pursuit", "quickattack", "rage", "ragefist", "ragingbull", "rapidspin", "razorshell", "retaliate", "return", "revenge", "reversal", "rockclimb", "rocksmash", "rollingkick", "rollout", "sacredsword", "scratch", "searingsunraze", "smash", "seismictoss", "shadowclaw", "shadowforce", "shadowpunch", "shadowsneak", "shadowstrike", "sizzlyslide", "skittersmack", "skullbash", "skydrop", "skyuppercut", "slam", "slash", "smartstrike", "smellingsalts", "snaptrap", "solarblade"]:
        return True
    else:
        return False
    
def HasSecondaryEffect(move):
    if move.id in secondaryeffectlist:
        return True
    else:
        return False
    
def IsWindMove(move):
    if move.id in wind_moves:
        return True
    else:
        return False
    
def IsRecoverMove(move):
    if move.id in recover_moves:
        return True
    else:
        return False
    
def IsRecoilMove(move):
    if move.id in recoil_moves:
        return True
    else:
        return False
    
wind_moves = [
    "aeroblast",
    "aircutter",
    "bleakwindstorm",
    "blizzard",
    "fairywind",
    "gust",
    "heatwave",
    "hurricane",
    "icywind",
    "petalblizzard",
    "sandsearstorm",
    "sandstorm",
    "springtidestorm",
    "tailwind",
    "twister",
    "whirlwind",
    "wildboltstorm"
]

recover_moves = ["recover", "roost", "slackoff", "softboiled", "milkdrink", "moonlight", "morningsun", "healorder"]

recoil_moves = [
    "axekick",
    "bravebird",
    "doubleedge",
    "flareblitz",
    "headcharge",
    "headsmash",
    "highjumpkick",
    "jumpkick",
    "submission",
    "supercellslam",
    "takedown",
    "wavecrash",
    "wildcharge"
]

secondaryeffectlist = [
    "acid",
    "airslash",
    "ancientpower",
    "astonish",
    "aurorabeam",
    "axekick",
    "barbbarrage",
    "bite",
    "blazekick",
    "bleakwindstorm",
    "blizzard",
    "blueflare",
    "bodyslam",
    "boltstrike",
    "boneclub",
    "bounce",
    "breakingswipe",
    "bubble",
    "bubblebeam",
    "bugbuzz",
    "bulldoze",
    "chatter",
    "chillingwater",
    "confusion",
    "constrict",
    "crosspoison",
    "crunch",
    "crushclaw",
    "darkpulse",
    "discharge",
    "direclaw",
    "dizzypunch",
    "dragonbreath",
    "dragonrush",
    "earthpower",
    "ember",
    "energyball",
    "extrasensory",
    "fierydance",
    "fireblast",
    "firefang",
    "firelash",
    "firepunch",
    "flamewheel",
    "flamethrower",
    "flareblitz",
    "flashcannon",
    "focusblast",
    "forcepalm",
    "freezeshock",
    "gunkshot",
    "headbutt",
    "heartstamp",
    "heatwave",
    "hurricane",
    "icebeam",
    "iceburn",
    "icefang",
    "icepunch",
    "iciclecrash",
    "icywind",
    "infernalparade",
    "ironhead",
    "irontail",
    "jetpunch",
    "lavaplume",
    "leaftornado",
    "lick",
    "liquidation",
    "lowsweep",
    "lunge",
    "lusterpurge",
    "metalclaw",
    "meteormash",
    "mirrorshot",
    "mistball",
    "moonblast",
    "mortalspin",
    "mountaingale",
    "mudbomb",
    "mudshot",
    "mudslap",
    "muddywater",
    "mysticalfire",
    "naturepower",
    "needlearm",
    "nightdaze",
    "nuzzle",
    "octazooka",
    "ominouswind",
    "orderup",
    "playrough",
    "poisonfang",
    "poisongas",
    "poisonjab",
    "poisonsting",
    "poisontail",
    "pounce",
    "powdersnow",
    "poweruppunch",
    "psybeam",
    "psychic",
    "razorshell",
    "relicsong",
    "rockclimb",
    "rockslide",
    "rocksmash",
    "rollingkick",
    "sacredfire",
    "sandsearstorm",
    "scald",
    "searingshot",
    "secretpower",
    "seedflare",
    "shadowball",
    "shadowbone",
    "shockwave",
    "signalbeam",
    "silverwind",
    "sludge",
    "sludgebomb",
    "sludgewave",
    "smog",
    "snore",
    "spark",
    "springtidestorm",
    "steamroller",
    "stokedsparksurfer",
    "stomp",
    "throatchop",
    "thunder",
    "thunderfang",
    "thunderpunch",
    "thundershock",
    "thunderbolt",
    "triattack",
    "triplearrows",
    "tropkick",
    "twineedle",
    "twister",
    "venomdrench",
    "volttackle",
    "waterpulse",
    "waterfall",
    "wildboltstorm",
    "zenheadbutt",
    "zingzap"
]