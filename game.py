import random
from agent import Agent
import numpy as np


class SpyGame:
    game_record = {}

    def __init__(self, number_of_players, number_of_rounds: int, secret_word: str, category: str):
        self.secret_word = secret_word
        self.category = category
        self.number_of_rounds = number_of_rounds
        self.spy_number = random.randint(0, number_of_players - 1)
        self.players = [Agent(llm_name="openai", player_name=f"player_{i}", player_role="spy", secret_word="",
                              category=category) if i == self.spy_number else Agent(llm_name="openai",
                                                                                    player_name=f"player_{i}",
                                                                                    player_role="detective",
                                                                                    secret_word=self.secret_word,
                                                                                    category=category) for i in
                        range(number_of_players)]
        self.number_of_players = len(self.players)
        self.game_record["conversation_record"] = f"**Game Starts**"
        self.game_record["voting_record"] = ""
        self.game_record["player_with_most_votes"] = ""
        self.game_record["winner"] = ""

    def run(self):
        round = 1
        while round <= self.number_of_rounds:
            player_to_ask_index = 0
            for _ in range(self.number_of_players):
                player_to_respond_index = (player_to_ask_index + 1) % (self.number_of_players)
                self.game_record[
                    "conversation_record"] += f"\nplayer_{player_to_ask_index} asks player_{player_to_respond_index} the question: {self.players[player_to_ask_index].ask_question(conversation=self.game_record['conversation_record'])}"
                self.game_record[
                    "conversation_record"] += f"\nplayer_{player_to_respond_index} responds: {self.players[player_to_respond_index].respond_to_question(conversation=self.game_record['conversation_record'])}"
                player_to_ask_index = (player_to_ask_index + 1) % (self.number_of_players)

            round += 1
        self.game_record["conversation_record"] += f"\n**End of Conversation Rounds**"

        votes = [0 for _ in self.players]
        vote_explanations = {}
        for player_index, player in enumerate(self.players):
            player_voted_on, explanation = player.vote(self.game_record["conversation_record"], self.number_of_players)
            votes[player_voted_on] += 1
            self.game_record[
                "voting_record"] += f"\nplayer_{player_index} voted on: player_{player_voted_on} - Reason: {explanation}"
            vote_explanations[f"player_{player_index}"] = explanation

        player_with_most_votes = int(np.argmax(votes))
        self.game_record["player_with_most_votes"] = player_with_most_votes

        if player_with_most_votes == self.spy_number:
            # Spy was caught, give them a chance to guess the word
            guessed_word = self.players[self.spy_number].guess_secret_word(self.game_record["conversation_record"])
            self.game_record["spy_guess"] = guessed_word

            if guessed_word.lower().strip() == self.secret_word.lower().strip():
                self.game_record["winner"] = "spy"
            else:
                self.game_record["winner"] = "detectives"
        else:
            # Spy was not voted out
            self.game_record["winner"] = "spy"

        self.game_record[
            "conversation_record"] += f"\nThe Spy: player_{self.spy_number}, secret_word: {self.secret_word}"