from game import SpyGame
import json



number_of_games = 2
games_total_record = []
number_of_players = 7
for _ in range(number_of_games):
    game = SpyGame(number_of_players)
    game.run()
    games_total_record.append(game.game_record)
print(games_total_record)

with open("games_total_record.json", "w") as file:
    json.dump(games_total_record, file, indent=4)