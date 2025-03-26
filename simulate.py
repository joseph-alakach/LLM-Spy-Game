from game import SpyGame
import json
import random
import categories

number_of_games = 1
games_total_record = []
number_of_players = 5
number_of_rounds = 2
category = random.choice(list(categories.CATEGORIES.keys()))
secret_word = random.choice(categories.CATEGORIES[category])
llm_name = "openai"  # openai, gemini, deepseek
for _ in range(number_of_games):
    game = SpyGame(number_of_players, number_of_rounds, secret_word, category, llm_name)
    game.run()
    games_total_record.append(game.game_record)

with open("games_total_record.json", "w") as file:
    json.dump(games_total_record, file, indent=4)