import random
from typing import List
from agent import Agent
import numpy as np


class Game:
    game_record = {}
    def __init__(self, number_of_players):
        self.secret_word = "airplane"
        self.spy_number = random.randint(0, number_of_players-1)
        self.players = [Agent(llm_name="openai", player_name=f"player_{i}", player_role="spy", secret_word="") if i == self.spy_number else Agent(llm_name="openai", player_name=f"player_{i}", player_role="detective", secret_word=self.secret_word) for i in range(number_of_players)]
        self.number_of_players = len(self.players)
        self.game_record["conversation_record"]= "**Game Starts**"
        self.game_record["voting_record"] = ""
        self.game_record["player_with_most_votes"] = ""
        self.game_record["winner"] = ""


    def run(self):
        round = 1
        player_to_ask_index = 0
        while round <= 3:
            player_to_respond_index = (player_to_ask_index + 1) % (7 + 1)

            self.game_record["conversation_record"] +=f"\nplayer_{player_to_ask_index} asks player_{player_to_respond_index} the question: {self.players[player_to_ask_index].ask_question(conversation=self.game_record['conversation_record'])}"
            self.game_record["conversation_record"] +=f"\nplayer_{player_to_respond_index} responds: {self.players[player_to_respond_index].respond_to_question(conversation=self.game_record['conversation_record'])}"

            round += 1
            player_to_ask_index = (player_to_ask_index + 1) % (7 + 1)
        self.game_record["conversation_record"] +=f"\n**End of Conversation Rounds**"

        votes = [ 0 for player in self.players]
        for player_index, player in enumerate(self.players):
            player_voted_on = player.vote(self.game_record["conversation_record"], self.number_of_players)
            votes[player_voted_on] += 1
            self.game_record["voting_record"] +=f"\nplayer_{player_index} voted on: player_{player_voted_on}"

        player_with_most_votes = np.argmax(votes)
        self.game_record["player_with_most_votes"] = player_with_most_votes

        if player_with_most_votes == self.spy_number:
            self.game_record["winner"] = "detectives"
        else:
            self.game_record["winner"] = "spy"



game = Game(7)
game.run()
print(game.game_record)
