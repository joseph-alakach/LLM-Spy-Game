import random
import numpy as np

from agent import Agent


class SpyGame:
    game_record = {}

    def __init__(self, number_of_players, number_of_rounds: int, secret_word: str, llm_name: str):
        self.secret_word = secret_word
        self.number_of_rounds = number_of_rounds
        self.spy_number = random.randint(0, number_of_players - 1)
        self.players = [Agent(llm_name=llm_name, player_name=f"player_{i}", player_role="spy", secret_word="") if i == self.spy_number else Agent(llm_name=llm_name,
                                                                                    player_name=f"player_{i}",
                                                                                    player_role="detective",
                                                                                    secret_word=self.secret_word) for i in range(number_of_players)]
        self.number_of_players = len(self.players)

        self.game_record["conversation_record"] = f"**Game Starts**"
        self.game_record["voting_record"] = ""
        self.game_record["player_with_most_votes"] = ""
        self.game_record["winner"] = ""
        self.game_record["spy"] = ""
        self.game_record["secret_word"] = ""
        self.game_record["players"] = {}
        self.game_record["conversation_record_json"] = []
        self.game_record["voting_record_json"] = []
        self.game_record["token_details"] = {}
        self.game_record["token_prices"] = {}


    @classmethod
    def from_llm_list(cls, llm_names, number_of_rounds: int, secret_word: str):
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
                secret_word=word
            )
            players.append(agent)

        # Instantiate using the base constructor with dummy values
        game = cls(number_of_players=number_of_players, number_of_rounds=number_of_rounds,
                   secret_word=secret_word, llm_name=None)

        # Overwrite the players and spy_number
        game.players = players
        game.spy_number = spy_number
        game.number_of_players = number_of_players

        return game

    def run(self):
        round = 1
        while round <= self.number_of_rounds:
            player_to_ask_index = 0
            for _ in range(self.number_of_players):
                player_to_respond_index = (player_to_ask_index + 1) % (self.number_of_players)
                question = self.players[player_to_ask_index].ask_question(
                    conversation=self.game_record['conversation_record'])
                self.game_record[
                    "conversation_record"] += f"\nplayer_{player_to_ask_index} asks player_{player_to_respond_index} the question: {question}"
                answer = self.players[player_to_respond_index].respond_to_question(
                    conversation=self.game_record['conversation_record'])
                self.game_record["conversation_record"] += f"\nplayer_{player_to_respond_index} responds: {answer}"


                # Append to conversation_record_json in the desired structured format
                self.game_record["conversation_record_json"].append({
                    "ask_player": f"player_{player_to_ask_index}",
                    "respond_player": f"player_{player_to_respond_index}",
                    "question": question,
                    "answer": answer
                })

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

            # Append to voting_record_json in the desired structured format
            self.game_record["voting_record_json"].append({
                "voter": f"player_{player_index}",
                "voted_for": f"player_{player_voted_on}",
                "reason": explanation
            })

        # check if there is a tie
        max_vote_count = max(votes)
        num_players_with_max = sum(1 for count in votes if count == max_vote_count)

        if num_players_with_max > 1:
            self.game_record["player_with_most_votes"] = "votes_tie"
            # spy wins because of vote tie
            self.game_record["winner"] = "spy"
        else:
            player_with_most_votes = int(np.argmax(votes))
            self.game_record["player_with_most_votes"] = player_with_most_votes
            if player_with_most_votes == self.spy_number:
                guessed_word = self.players[self.spy_number].guess_secret_word(self.game_record["conversation_record"])
                self.game_record["spy_guess"] = guessed_word
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
        self.print_token_costs()



    def getTokenCountForLLM(self) -> dict:
        llms_used = []
        llms_used.extend(self.game_record["players"].values())
        llms_used = list(set(llms_used))
        full_usage = {llm_name: {"input_tokens": 0, "output_tokens": 0, "thinking_tokens": 0, "full_output_tokens": 0}
                      for llm_name in llms_used}
        for player in self.players:
            llm_name = player.llm_name
            input_tokens = player.input_tokens_used
            output_tokens = player.output_tokens_used
            thinking_tokens = player.thinking_tokens_used
            full_output_tokens = output_tokens + thinking_tokens
            full_usage[llm_name]["input_tokens"] += input_tokens
            full_usage[llm_name]["output_tokens"] += output_tokens
            full_usage[llm_name]["thinking_tokens"] += thinking_tokens
            full_usage[llm_name]["full_output_tokens"] += full_output_tokens

        self.game_record["token_details"] = full_usage
        return full_usage

    def calculate_token_costs(self) -> dict:
        full_usage = self.getTokenCountForLLM()
        pricing = {
            "gemini": {"input": 0.15/1000000, "output": 0.6/1000000, "thinking": 3.5/1000000},
            "openai": {"input": 1.1/1000000, "output": 4.4/1000000, "thinking": 4.4/1000000},
            "claude": {"input": 3/1000000, "output": 15/1000000, "thinking": 15/1000000},
            "grok": {"input": 0.3/1000000, "output": 0.5/1000000, "thinking": 0.5/1000000},
            "deepseek": {"input": 0.14/1000000, "output": 2.19/1000000, "thinking": 2.19/1000000},
        }
        llm_costs = {}
        total_input_cost = 0
        total_output_cost = 0
        total_thinking_cost = 0
        total_full_output_cost = 0
        for llm_name, usage in full_usage.items():
            if llm_name in pricing:
                price_per_token = pricing[llm_name]
                input_cost = usage["input_tokens"] * price_per_token["input"]
                output_cost = usage["output_tokens"] * price_per_token["output"]
                thinking_cost = usage["thinking_tokens"] * price_per_token["thinking"]
                full_output_cost = output_cost + thinking_cost

                # Store the results in the llm_costs dictionary
                llm_costs[llm_name] = {
                    "input_cost": input_cost,
                    "output_cost": output_cost,
                    "thinking_cost": thinking_cost,
                    "full_output_cost": full_output_cost,
                }

                total_input_cost += input_cost
                total_output_cost += output_cost
                total_thinking_cost += thinking_cost
                total_full_output_cost += full_output_cost

        llm_costs["total_costs"] = {
            "total_input_cost": total_input_cost,
            "total_output_cost": total_output_cost,
            "total_thinking_cost": total_thinking_cost,
            "total_full_output_cost": total_full_output_cost,
            "full_total_cost": total_input_cost+total_full_output_cost
        }
        self.game_record["token_prices"] = llm_costs
        return llm_costs

    def print_token_costs(self):
        # Get the token counts and costs
        full_usage = self.getTokenCountForLLM()
        llm_costs = self.calculate_token_costs()

        # Print individual costs for each LLM
        for llm_name in full_usage:
            print(f"LLM: {llm_name}")
            print(f"{'=' * 50}")
            print(f"Token Count:")
            print(f"  Input Tokens: {full_usage[llm_name]['input_tokens']}")
            print(f"  Output Tokens: {full_usage[llm_name]['output_tokens']}")
            print(f"  Thinking Tokens: {full_usage[llm_name]['thinking_tokens']}")
            print(f"  Full Output Tokens: {full_usage[llm_name]['full_output_tokens']}")

            print(f"Price:")
            print(f"  Input Cost: ${llm_costs[llm_name]['input_cost']:.6f}")
            print(f"  Output Cost: ${llm_costs[llm_name]['output_cost']:.6f}")
            print(f"  Thinking Cost: ${llm_costs[llm_name]['thinking_cost']:.6f}")
            print(f"  Full Output Cost: ${llm_costs[llm_name]['full_output_cost']:.6f}")

            print(f"{'=' * 50}\n")

        # Print the total costs for the run
        print(f"{'=' * 50}")
        print(f"Total Costs for the Run:")
        print(f"  Total Input Cost: ${llm_costs['total_costs']['total_input_cost']:.6f}")
        print(f"  Total Output Cost: ${llm_costs['total_costs']['total_output_cost']:.6f}")
        print(f"  Total Thinking Cost: ${llm_costs['total_costs']['total_thinking_cost']:.6f}")
        print(f"  Total Full Output Cost: ${llm_costs['total_costs']['total_full_output_cost']:.6f}")
        print(f"  Full Total Cost: ${llm_costs['total_costs']['full_total_cost']:.6f}")
        print(f"{'=' * 50}")
