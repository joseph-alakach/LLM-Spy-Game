from game import SpyGame
import json
import random
import categories

number_of_games = 1
games_total_record = []
number_of_rounds = 2
category = random.choice(list(categories.CATEGORIES.keys()))
secret_word = random.choice(categories.CATEGORIES[category])


def convert_game_record(game_record):
    # Function to remove unwanted escape sequences like \"
    def clean_text(text):
        return text.replace('\\"', '')

    # Initialize the conversation_record as an empty list
    conversation_record = []

    # Split conversation_record string by newlines
    if isinstance(game_record['conversation_record'], str):
        lines = game_record['conversation_record'].split("\n")

        # Ignore the first and last elements (game start and end of rounds)
        lines = lines[1:-1]

        # Iterate through the conversation and group the "asks" and "responds"
        for i in range(0, len(lines), 2):
            if "asks" in lines[i] and "responds" in lines[i + 1]:
                questioner = clean_text(lines[i].split(" asks ")[0].strip())
                responder = clean_text(lines[i].split(" asks ")[1].split(" the question")[0].strip())
                question = clean_text(lines[i].split(" asks ")[1].split(" the question: ")[1].strip())
                answer = clean_text(lines[i + 1].split(" responds: ")[1].strip())

                conversation_record.append({
                    "ask_player": questioner,
                    "respond_player": responder,
                    "question": question,
                    "answer": answer
                })

    # Convert voting_record into a list of dictionaries
    voting_record = []
    for entry in game_record['voting_record'].split("\n"):
        if "voted on" in entry:
            parts = entry.split(" voted on: ")
            voter = parts[0].strip()
            rest = parts[1].split(" - Reason: ")

            if len(rest) > 1:
                voted_for = rest[0].strip()
                reason = clean_text(rest[1].strip())  # Clean reason as well
                voting_record.append({
                    "voter": voter,
                    "voted_for": voted_for,
                    "reason": reason
                })
            else:
                print(f"Skipping incomplete vote entry: {entry}")

    # Update game_record with the new format
    game_record['conversation_record'] = conversation_record
    game_record['voting_record'] = voting_record

    return game_record


games = []
def process_all_games(data):
    # Iterate through each game record in the list
    for game in data:
        game = convert_game_record(game)
        games.append(game)


allSame = False
if allSame:
    number_of_players = 5
    llm_name = "claude"  # openai, gemini, deepseek, claude
    for _ in range(number_of_games):
        game = SpyGame(number_of_players, number_of_rounds, secret_word, category, llm_name)
        game.run()
        games_total_record.append(game.game_record)

else:
    llm_names = ["openai", "openai"] #, "gemini", "claude", "deepseek"]
    random.shuffle(llm_names)
    for _ in range(number_of_games):
        game = SpyGame.from_llm_list(llm_names=llm_names, number_of_rounds=number_of_rounds, secret_word=secret_word, category=category)
        game.run()
        games_total_record.append(game.game_record)


process_all_games(games_total_record)
with open("games_total_record.json", "w") as file:
    json.dump(games, file, indent=4)
