import random
import numpy as np

from agent import Agent
from utils import retry



class SpyGame:
    game_record = {}

    def __init__(self, number_of_players, number_of_rounds: int, secret_word: str, category: str, llm_name):
        self.secret_word = secret_word
        self.category = category
        self.number_of_rounds = number_of_rounds
        self.spy_number = random.randint(0, number_of_players - 1)
        self.players = [Agent(llm_name=llm_name, player_name=f"player_{i}", player_role="spy", secret_word="",
                              category=category) if i == self.spy_number else Agent(llm_name=llm_name,
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
        self.game_record["spy"] = ""
        self.game_record["secret_word"] = ""
        self.game_record["players"] = {}


    @classmethod
    def from_llm_list(cls, llm_names, number_of_rounds: int, secret_word: str, category: str):
        number_of_players = len(llm_names)
        spy_number = random.randint(0, number_of_players - 1)

        players = []
        for i in range(number_of_players):
            llm = llm_names[i]
            role = "spy" if i == spy_number else "detective"
            word = "" if role == "spy" else secret_word

            agent = Agent(
                llm_name=llm,
                player_name=f"player_{i}",
                player_role=role,
                secret_word=word,
                category=category
            )
            players.append(agent)

        # Instantiate using the base constructor with dummy values
        game = cls(number_of_players=number_of_players, number_of_rounds=number_of_rounds,
                   secret_word=secret_word, category=category, llm_name=None)

        # Overwrite the players and spy_number
        game.players = players
        game.spy_number = spy_number
        game.number_of_players = number_of_players

        return game

    @retry()
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

        playersDataJson = {}
        for i in self.players:
            playersDataJson[i.player_name.split('_')[1]] = i.llm_name
        self.game_record["players"] = playersDataJson
        self.game_record["spy"] = self.spy_number
        self.game_record["secret_word"] = self.secret_word

        self.game_record["llm_info"] = {}
        for player in self.players:
            self.game_record["llm_info"][player.player_name] = {
                "llm_type": player.llm_name,
                "role": player.role,
                "question_generation_durations": player.question_generation_durations,
                "answer_generation_durations": player.answer_generation_durations,
            }

        print("Token Usage Per Agent:")
        total_input_tokens = 0
        total_output_tokens = 0
        for i, player in enumerate(self.players):
            input_tokens = player.input_tokens_used
            output_tokens = player.output_tokens_used
            total = input_tokens + output_tokens

            total_input_tokens += input_tokens
            total_output_tokens += output_tokens
            print(f"player_{i} | input: {input_tokens} | output: {output_tokens} | total: {total}")

        print("\nTotal Token Usage:")
        print(f"Total input tokens used: {total_input_tokens}")
        print(f"Total output tokens used: {total_output_tokens}")
        print(f"Grand total tokens used: {total_input_tokens + total_output_tokens}")