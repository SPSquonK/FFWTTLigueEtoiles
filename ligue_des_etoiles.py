import re
import sys
import pprint as pp



list_of_players = {}
list_of_other_names = {}


is_reading_players = True

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
    has_plus = has("+") or has("rouge") or has("bleu")
    has_mkc = has("mkc") or has("mc") or has("yellow")
    has_mm = has("mm")

    if has_mkc:
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
        sys.stderr.print("Unknown rule : " + rule_str)
        exit(0)


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


        pp.pprint(game_object, indent=2)

        return game_object
    else:
        sys.stderr.print("<" + line + "> does not match regex\n")
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

            for name in names:
                list_of_other_names[name] = names[0]
        else:
            game_object = read_game(line)

            register_game(list_of_players[game_object["player1"]], game_object["player2"], game_object["rule"], game_object["score"])
            register_game(list_of_players[game_object["player2"]], game_object["player1"], game_object["rule"], 10 - game_object["score"])




print("List of players")
pp.pprint(list_of_players, indent=2)


print("List of other names")
pp.pprint(list_of_other_names, indent=2)



