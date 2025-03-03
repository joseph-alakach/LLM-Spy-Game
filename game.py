import random
from typing import List
from agent import Agent


class Game:
    conversation_record = {}

    def __init__(self, number_of_players):
        spy_number = random.randint(1, number_of_players)
        self.players = [Agent(llm_name="openai", player_name=f"player_{i+1}", player_role="spy") if i+1 == spy_number else Agent(llm_name="openai", player_name=f"player_{i+1}", player_role="detective") for i in range(number_of_players)]
        self.number_of_players = len(self.players)
        self.spy = random.choice(players)






