from game import SpyGame
import json
import random
import categories

number_of_games = 2
number_of_rounds = 2
allSame = False

games_total_record = []

category = random.choice(list(categories.CATEGORIES.keys()))
secret_word = random.choice(categories.CATEGORIES[category])


for i in range(number_of_games):
    if allSame:
        number_of_players = 3
        llm_name = "openai"  # openai, gemini, deepseek, claude, grok
        game = SpyGame(number_of_players, number_of_rounds, secret_word, category, llm_name)
    else:
        # llm_names = ["openai", "gemini", "claude", "deepseek", "grok", "human"]
        llm_names = ["openai", "gemini", "claude", "deepseek", "grok"]
        random.shuffle(llm_names)
        game = SpyGame.from_llm_list(llm_names=llm_names, number_of_rounds=number_of_rounds, secret_word=secret_word,
                                     category=category)

    if i != 0:
        with open("games_total_record.json", "r") as file:
            games_total_record = json.load(file)

    game.run()
    if "conversation_record" in game.game_record:
        del game.game_record["conversation_record"]
    if "voting_record" in game.game_record:
        del game.game_record["voting_record"]
    if "conversation_record_json" in game.game_record:
        game.game_record["conversation_record"] = game.game_record["conversation_record_json"]
        del game.game_record["conversation_record_json"]
    if "voting_record_json" in game.game_record:
        game.game_record["voting_record"] = game.game_record["voting_record_json"]
        del game.game_record["voting_record_json"]
    games_total_record.append(game.game_record)

    with open("games_total_record.json", "w") as file:
        json.dump(games_total_record, file, indent=4)
