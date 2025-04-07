from game import SpyGame
import json
import random
import categories

number_of_games = 1
games_total_record = []
number_of_rounds = 2
category = random.choice(list(categories.CATEGORIES.keys()))
secret_word = random.choice(categories.CATEGORIES[category])

allSame = False
if allSame:
    number_of_players = 5
    llm_name = "claude"  # openai, gemini, deepseek, claude
    for _ in range(number_of_games):
        game = SpyGame(number_of_players, number_of_rounds, secret_word, category, llm_name)
        game.run()
        games_total_record.append(game.game_record)

    with open("games_total_record.json", "w") as file:
        json.dump(games_total_record, file, indent=4)
else:
    llm_names = ["openai", "gemini", "claude", "deepseek"]
    for _ in range(number_of_games):
        game = SpyGame.from_llm_list(llm_names=llm_names, number_of_rounds=number_of_rounds, secret_word=secret_word, category=category)
        game.run()
        games_total_record.append(game.game_record)

    with open("games_total_record.json", "w") as file:
        json.dump(games_total_record, file, indent=4)
