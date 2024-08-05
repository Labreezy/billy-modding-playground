from glob import glob
import json
import re
import igraph as ig
import matplotlib.pyplot as plt
from billy_data import EXCLUDE_EGGS, SHORT_EXCLUDE_WORLDS
LEVEL_REGEX = re.compile(r"obj_([a-z]+)([1-8])\.json")

LONGNAMES = {
    "green": "Forest",
    "blue":"Pirate",
    "red":"Dino",
    "purple":"Blizzard",
    "orange":"Circus",
    "yellow":"Sand",
    "last":"Palace"
}

WORLD_ORDER = ["green","blue","red","purple","orange","yellow","last"]
EGG_NAMES = ["Spotted",
"Fire Comb",
            "Water Comb",
            "Lightning Comb",
            "Ice Comb",
            "Wind Comb",
            "Iron Comb",
            "Light Comb",
            "Wings",
            "Booster",
            "Paraloop",
            "Thorn Egg",
            "Speed Shoes",
            "Bomb",
            "Spring Shoes",
            "Circus Hat",
            "Psychic Hat",
            "Heart Hat",
            "Bat",
            "Crow",
            "Cipher",
            "Clippen",
            "Recky",
            "Richie",
            "Peliwan",
            "Runny",
            "Rabbish",
            "Rikol",
            "Kaboot",
            "Datch",
            "Glarin",
            "Baskus",
            "Oritta",
            "Biboo",
            "Gorilla",
            "Chameleon",
            "Mouse",
            "Turtle",
            "Lion",
            "Dice",
            "Super Fruit",
            "Tiger",
            "Sheep",
            "Hawk",
            "Fox",
            "Large Butterfly",
            "Stopwatch",
            "Small Butterfly",
            "1 Up",
            "Chick Bomb",
            "Egg Bomb",
            "Game Boy Advance Game: Chu Chu Rocket Challenge",
            "Game Boy Advance Game: Nights Score Attack",
            "Game Boy Advance Game: Billy Hatcher Shoot - Easy",
            "Game Boy Advance Game: Billy Hatcher Hyper Shoot",
            "Game Boy Advance Game: Puyo Pop",
            "Sonic",
            "Tails",
            "Knuckles",
            "Chao",
            "Rappy",
            "Kapu Kapu",
            "NIGHTS",
            "Amigo",
            "Super Clippen",
            "Super Recky",
            "Chicken Suit",
            "Oma-Oma",
            "Uri-Uri",
            "Ura-Ura",
            "Ponee",
            "Allani",
            "Mera-Mera"
]


class Level():
    def __init__(self,world,mnum,egglist):
        self.world = world
        self.missionnum = mnum
        self.egglist = egglist
    def __str__(self):
        return LONGNAMES[self.world] + " " + str(self.missionnum)




def get_egglist_from_json(fn):
    objlist = json.loads(open(fn).read())

    eggs_full = [o for o in objlist['data'] if o['name'] == "egg"]
    unique_eggs = list(set(list(map(lambda e: e["intparams"][1], eggs_full))))
    unique_eggs.sort()
    return [EGG_NAMES[i] for i in unique_eggs]
if __name__ == '__main__':
    edgelist = []
    all_levels = []
    for fn in glob("base_setjsons/*.json"):
        groups = LEVEL_REGEX.findall(fn)
        if len(groups) > 0:
            world, mnum = groups[0]
            if world == "test":
                continue
            lvl = Level(world,int(mnum),get_egglist_from_json(fn))
            all_levels.append(lvl)
            all_levels.sort(key=lambda l: WORLD_ORDER.index(l.world)*8+l.missionnum)
    for world in range(7):
        #generic conditions
        for m in range(4):
            level_idx = world*8+m
            edgelist.append((level_idx,level_idx+1))
    for world in range(6):
        edgelist.append((world*8+1,(world+1)*8))

    #pirate 4 to forest/pirate 6
    edgelist.append((11,5))
    edgelist.append((11,13))
    edgelist.append((11,21))
    #dino 4 to forest,pirate,dino 7
    edgelist.append((8*3+3,6))
    edgelist.append((8*3+3, 8+6))
    edgelist.append((8*3+3, 16+6))
    #blizzard 4 to forest,pirate,dino,blizzard 8
    edgelist.append((8*4+3, 7))
    edgelist.append((8*4+3, 8+7))
    edgelist.append((8*4+3, 16+7))
    edgelist.append((8*4+3, 24+7))

    #connect friend missions to after boss for blizzard, circus, sand
    for j in range(3,6):
        for i in range(5,8):
            edgelist.append((j*8+1,j*8+i))
    #palace too
    for i in range(5,8):
        edgelist.append((48,48+i))




    fig, ax = plt.subplots()
    g = ig.Graph(56, edgelist, directed=True)

    result_lens = [len(p) for p in g.get_shortest_paths(0)]
    REMAINING_EGGS = EGG_NAMES.copy()
    EGG_MIN_LEVEL_CLEARS = [999]*len(EGG_NAMES)
    EGG_MIN_LEVEL_CLEAR_NAMES = [None]*len(EGG_MIN_LEVEL_CLEARS)
    for i in range(0,len(result_lens)):
        e_list = all_levels[i].egglist
        pathlength = result_lens[i]
        for egg in e_list:
            egg_idx = EGG_NAMES.index(egg)
            if pathlength < EGG_MIN_LEVEL_CLEARS[egg_idx]:
                EGG_MIN_LEVEL_CLEARS[egg_idx] = pathlength
                EGG_MIN_LEVEL_CLEAR_NAMES[egg_idx] = all_levels[i]


    eggcleardata = [(e,n) for e,n in zip(EGG_NAMES, EGG_MIN_LEVEL_CLEAR_NAMES) if n is not None]
    eggcleardata.sort(key=lambda e: WORLD_ORDER.index(e[1].world)*8+e[1].missionnum)

    for egg, level in eggcleardata:
        if level is None:
            continue
        if egg in EXCLUDE_EGGS:
            continue
        print(f"Hatch a {egg} egg and finish ({str(level)})")









