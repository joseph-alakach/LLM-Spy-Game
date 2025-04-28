from game import SpyGame
import json
import random
import categories


def run_games_same_llm(llm_name: str, number_of_games: int):
    games_total_record = []
    number_of_rounds = 2
    category = random.choice(list(categories.CATEGORIES.keys()))
    secret_word = random.choice(categories.CATEGORIES[category])

    # Run the games
    for i in range(number_of_games):
        number_of_players = 5
        game = SpyGame(number_of_players, number_of_rounds, secret_word, category, llm_name)

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

    return games_total_record


def run_games_different_llms(number_of_games: int):
    llms = ["openai", "gemini", "claude", "deepseek", "grok"]
    games_total_record = []
    number_of_rounds = 2
    category = random.choice(list(categories.CATEGORIES.keys()))
    secret_word = random.choice(categories.CATEGORIES[category])

    # Calculate the number of games each LLM should be the spy
    spy_count = number_of_games // len(llms)

    # Generate a list of LLMs that will act as the spy
    spy_assignments = []
    for llm in llms:
        spy_assignments.extend([llm] * spy_count)

    # If there are leftover games, we can shuffle the spy assignments for the remainder
    while len(spy_assignments) < number_of_games:
        spy_assignments.append(llms[random.randint(0, len(llms) - 1)])

    random.shuffle(spy_assignments)  # Shuffle the spy assignments

    # Run the games
    for i in range(number_of_games):
        llm_names = llms.copy()
        random.shuffle(llm_names)

        # Assign the spy role for the current game
        spy_llm = spy_assignments[i]
        # print("required spy llm: " + spy_llm)
        game = SpyGame.from_llm_list(llm_names=llm_names, number_of_rounds=number_of_rounds, secret_word=secret_word,
                                     category=category)
        spy_llm_now = game.players[game.spy_number].llm_name
        # print("current spy llm: " + spy_llm_now)
        while spy_llm_now != spy_llm:
            game = SpyGame.from_llm_list(llm_names=llm_names, number_of_rounds=number_of_rounds,
                                         secret_word=secret_word,
                                         category=category)
            spy_llm_now = game.players[game.spy_number].llm_name
            # print("current spy llm: " + spy_llm_now)


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
    return games_total_record


# Run games with the same LLM
# number_of_games_same = 4
# llm_name = "openai"  #openai, gemini, deepseek, claud, grok
# games_same_llm = run_games_same_llm(llm_name, number_of_games_same)

# Run games with different LLMs
number_of_games_different = 5
games_different_llms = run_games_different_llms(number_of_games_different)
