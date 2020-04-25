import re
import sys
import pprint as pp
from collections import OrderedDict


list_of_players = OrderedDict()
list_of_other_names = {}

rules = OrderedDict()
rules["+ ="] = ("red", "+ = alea")
rules["mm ma"] = ("orange", "mm ma elem")
rules["mp + ="] = ("blue", "mp + = alea")
rules["mp"] = ("green", "mp bat")
rules["mkc"] = ("#d4c300", "mkc elem bat")


is_reading_players = True
stop = False

def find_player(player_name):
    if player_name in list_of_other_names:
        return list_of_other_names[player_name]
    else:
        sys.stderr.print("Unknown player : " + player_name)
        exit(0)


def convert_rule(rule_str):
    rule_str = rule_str.lower()

    if rule_str == "r":
        return "+ ="
    elif rule_str == "o":
        return "mm ma"
    elif rule_str == "j":
        return "mkc"
    elif rule_str == "v":
        return "mp"
    elif rule_str == "b":
        return "mp + ="
    
    def has(s):
        return rule_str.find(s) != -1

    has_mp = has("mp") or has("vert") or has("bleu")
    has_plus = has("+") or has("rouge") or has("bleu") or has("plus")
    has_mkc = has("mkc") or has("mc") or has("jaune")
    has_mm = has("mm") or has("orange")

    if has_mkc:
        if has_plus or has_mp or has_mm:
            sys.stderr.write("Unknown rule : " + rule_str)
        else:
            return "mkc"
    elif has_mp:
        if has_plus:
            return "mp + ="
        else:
            return "mp"
    elif has_mm:
        return "mm ma"
    elif has_plus:
        return "+ ="
    else:
        sys.stderr.write("Unknown rule : " + rule_str)
        exit(0)


def read_peer(line):
    REGEX_PEER = "^([A-Za-z_^\-0-9]*) Peer vs ([A-Za-z_^\-0-9]*) (.*)$"
    match = re.search(REGEX_PEER, line)
    if match:
        player1 = match.group(1)
        player2 = match.group(2)
        rule_str = match.group(3)

        game_object = {}
        game_object["player1"] = find_player(player1)
        game_object["player2"] = find_player(player2)
        game_object["score"] = 3
        game_object["rule"] = convert_rule(rule_str)

        return game_object
    else:
        return None


def read_game(line):
    regex_str = r"^\[[0-9][0-9]:[0-9][0-9]:[0-9][0-9]\] <([A-Za-z_^\-0-9]*)> (\[[0-9][0-9]:[0-9][0-9]:[0-9][0-9]\])? ?Partie avec ([A-Za-z_^\-0-9]*) terminée ; votre score : ([0-9]*) (.*)$"
    match = re.search(regex_str, line)
    if match:
        player1 = match.group(1)
        player2 = match.group(3)
        score = match.group(4)
        rule_str = match.group(5)

        game_object = {}
        game_object["player1"] = find_player(player1)
        game_object["player2"] = find_player(player2)
        game_object["score"] = int(score)
        game_object["rule"] = convert_rule(rule_str)

        return game_object
    else:
        sys.stderr.write("<" + line + "> does not match regex\n")
        exit(0)




def register_game(player1dict, player2name, rule, score):
    games = player1dict["games"]
    games_rule = games[rule]

    if player2name in games_rule:
        if games_rule[player2name] != score:
            sys.stderr.write(player1dict["name"] + " vs " + player2name + " has two different scores for " + rule + "\n")
            exit(0)
    else:
        games_rule[player2name] = score


with open("input.txt", encoding="utf-8") as f:
    for line in f.readlines():
        line = line.strip()
        if line is None or len(line) == 0:
            continue
        if line[0:2] == "//":
            continue
        if line == "yamete kudasai" or line == "stop":
            stop = True
            continue
        if stop:
            continue

        if line == "-- Players --":
            is_reading_players = True
            continue
        elif line == "-- Games --":
            is_reading_players = False
            continue

        if is_reading_players:
            names = line.split(" ")
            list_of_players[names[0]] = {}
            list_of_players[names[0]]["games"] = {}
            list_of_players[names[0]]["games"]["+ ="] = {}
            list_of_players[names[0]]["games"]["mm ma"] = {}
            list_of_players[names[0]]["games"]["mp + ="] = {}
            list_of_players[names[0]]["games"]["mp"] = {}
            list_of_players[names[0]]["games"]["mkc"] = {}
            list_of_players[names[0]]["name"] = names[0]
            list_of_players[names[0]]["ranking"] = {}

            for name in names:
                list_of_other_names[name] = names[0]
        else:
            game_object = read_peer(line)

            if game_object is None:
                game_object = read_game(line)

            register_game(list_of_players[game_object["player1"]], game_object["player2"], game_object["rule"], game_object["score"])
            register_game(list_of_players[game_object["player2"]], game_object["player1"], game_object["rule"], 10 - game_object["score"])



def compute_rank(list_of_games):
    total_played = 0
    total_score = 0

    for opponent in list_of_games:
        total_played += 1
        total_score += list_of_games[opponent]
    
    d = {}
    d["played"] = total_played
    d["score"] = total_score
    return d


for player_name in list_of_players:
    m = 9999

    for rule in ["+ =", "mm ma", "mp + =", "mp", "mkc"]:
        list_of_players[player_name]["ranking"][rule] = compute_rank(list_of_players[player_name]["games"][rule])
        m = min(m, list_of_players[player_name]["ranking"][rule]["played"])
    
    list_of_players[player_name]["played"] = m





#print("List of players")
#pp.pprint(list_of_players, indent=2)


#print("List of other names")
#pp.pprint(list_of_other_names, indent=2)


print()
print()
print('<table class="wikitable" border="1" style="text-align: center;">')

def get_global_header():
    s = "<tr>"
    s += "<th>Nom</th><th>Joués</th>"

    for player_name in list_of_players:
        s += "<th>" + player_name + "</th>"

    s += "</tr>"
    return s

print(get_global_header())


for player_name in list_of_players:
    p_dict = list_of_players[player_name]

    s = "<tr>"
    s += "<th>" + player_name + "</th>"
    s += "<th>" + str(p_dict["played"]) + "</th>"

    for other_p_name in list_of_players:
        s += "<td>"

        for rule in rules:
            if rule == "mp":
                s += "<br>"
            if other_p_name in p_dict["games"][rule]:
                s += '<span style="color: ' + rules[rule][0] + ';">' + str(p_dict["games"][rule][other_p_name]) + "</span>"

            s += " "

        s += "</td>"

    s += "</tr>"
    print(s)


print('</table>')

print()
print()
print()



print("----")
print("----")
print("----")
print()
print()
print()
print()
print('<table class="wikitable" border="1" style="text-align: center; width: 100%">')

def get_rule_header():
    s = "<tr>"
    for rule in rules:
        s += "<th></th><th colspan=2>" + rules[rule][1] + "</th>"
    s += "</tr>"
    return s

print(get_rule_header())


def get_rule_header2():
    s = "<tr><th>#</th>"
    first = True
    for _ in rules:
        if first:
            first = False
        else:
            s+= "<th></th>"
        s += "<th>Joueur</th>"
        s += "<th>Points</th>"
    s += "</tr>"
    return s

print(get_rule_header2())

rankings = {}

for rule in rules:
    rankings[rule] = []
    l = rankings[rule]

    for player in list_of_players:
        l.append(player)
    
    def cmp_rule(player_name):
        return -list_of_players[player_name]["ranking"][rule]["score"], -list_of_players[player_name]["ranking"][rule]["played"]
    
    l.sort(key=cmp_rule)


for i in range(len(list_of_players)):
    s = "<tr><th>" + str(i + 1) + "</th>"

    for (k, rule) in enumerate(rules):
        if k != 0:
            s += "<th></th>"
        
        p_name = rankings[rule][i]
        s += "<td>" + p_name + "</td><td>" + str(list_of_players[p_name]["ranking"][rule]["score"]) + "</td>"

        list_of_players[p_name]["ranking"][rule]["rank"] = i + 1

    s += "</tr>"

    print(s)


print('</table>')


print()
print()
print()
print()
print()
print()


print("----")
print("----")
print("----")


player_global_ranking = []

for player_name in list_of_players:
    list_of_players[player_name]["final_rank"] = len(list_of_players) * len(rules)

    for rule in rules:
        list_of_players[player_name]["final_rank"] -= rankings[rule].index(player_name)

        list_of_players[player_name]["ranking"][rule]["pts"] = len(list_of_players) - rankings[rule].index(player_name)

    player_global_ranking.append(player_name)

def global_rank_key(player_name):
    return -list_of_players[player_name]["final_rank"]

player_global_ranking.sort(key=global_rank_key)



print()
print()
print()
print()
print()
print()
print('<center><table class="wikitable" border="1" style="text-align: center;">')

if True:
    s = "<tr><th>Position</th><th>Nom</th><th>Points de classement</th><th></th>"
    for rule in rules:
        s += "<th>Rang " + rules[rule][1] + "</th>"
    
    s += "</tr>"
    print(s) 



for (i, player_name) in enumerate(player_global_ranking):
    s = "<tr><th>" + str(i + 1) + "</th><td>" + player_name + "</td><td>" + str(list_of_players[player_name]["final_rank"]) + "</td><th></th>"

    for rule in rules:
        r = str(list_of_players[player_name]["ranking"][rule]["rank"])

        if r == "1":
            r = "1er"
        else:
            r = r + "ème"

        s += "<td>" + r + " (+" + str(list_of_players[player_name]["ranking"][rule]["pts"]) + ")</td>"

    s += "</tr>"
    print(s)

print('</table></center>')



