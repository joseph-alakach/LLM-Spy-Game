import json
from pprint import pprint
from typing import List, Dict

import numpy as np

import config

# llm_response = config.DEEPSEEK_CLIENT.chat.completions.create(
#                 model=config.DEEPSEEK_MODEL,
#                 messages=[
#                     {"role": "system", "content": "Act as a dumb llm"},
#                     {"role": "user", "content": "what is the meaning of life?"}
#                 ],
#                 # temperature=0.3,
#             )

# llm_response = config.DEEPSEEK_CLIENT.chat.completions.create(
#                 model=config.DEEPSEEK_MODEL,
#                 messages=[
#                     {"role": "system", "content": system_prompt},
#                     {"role": "user", "content": user_prompt}
#                 ],
#                 temperature=0.00000001,
#             )
# print(llm_response)
# self.input_tokens_used += llm_response.usage.input_tokens
# self.output_tokens_used += llm_response.usage.output_tokens




import os

def calculate(folder_path: str, is_same: bool):
    llm_used = ["openai", "gemini", "claude", "deepseek", "grok"]
    stats = {llm_name:{"spy_win":0, "detective_win":0} for llm_name in llm_used}
    llm_roles_count = {llm_name:{"spy":0, "detective":0} for llm_name in llm_used}
    game_count = 0
    spy_win_count = 0
    detective_win_count = 0

    for filename in os.listdir(folder_path):
        full_path = os.path.join(folder_path, filename)
        with open(full_path, "r") as file:
            games_total_record = json.load(file)


        for game in games_total_record:
            game_count +=1
            game_winner_role = game["winner"]

            for player_name in ["player_0","player_1","player_2","player_3","player_4"]:
                llm_name =  game["llm_info"][player_name]["llm_type"]
                llm_role = game["llm_info"][player_name]["role"]
                llm_roles_count[llm_name][llm_role] +=1


            if game_winner_role == "detectives":
                detective_win_count +=1

                # spy_player_name = f"player_{game['spy']}"
                detective_player_names = [f"player_{i}" for i in range(5) if i!=game['spy']]
                if is_same:
                    detective_llm_name = game["llm_info"][detective_player_names[0]]["llm_type"]
                    stats[detective_llm_name]["detective_win"] += 1
                else:
                    for detective_player_name in detective_player_names:
                        detective_llm_name = game["llm_info"][detective_player_name]["llm_type"]
                        stats[detective_llm_name]["detective_win"] += 1
            if game_winner_role == "spy":
                spy_win_count +=1

                spy_player_name =f"player_{game['spy']}"
                spy_llm_name = game["llm_info"][spy_player_name]["llm_type"]
                stats[spy_llm_name]["spy_win"] +=1

    if is_same:
        for llm_name in stats:
            games_count_with_specific_llm = (stats[llm_name]["spy_win"]+stats[llm_name]["detective_win"])
            stats[llm_name]["spy_win"] = stats[llm_name]["spy_win"] /games_count_with_specific_llm
            stats[llm_name]["detective_win"] = stats[llm_name]["detective_win"] /games_count_with_specific_llm
            stats[llm_name]["spy_count"] = llm_roles_count[llm_name]["spy"]
            stats[llm_name]["detective_count"] = llm_roles_count[llm_name]["detective"]
    else:
        for llm_name in stats:
            stats[llm_name]["spy_win"] = stats[llm_name]["spy_win"] / llm_roles_count[llm_name]["spy"]
            stats[llm_name]["detective_win"] = stats[llm_name]["detective_win"] / llm_roles_count[llm_name]["detective"]
            stats[llm_name]["spy_count"] = llm_roles_count[llm_name]["spy"]
            stats[llm_name]["detective_count"] = llm_roles_count[llm_name]["detective"]

    print(f"Spy win: {spy_win_count/game_count}")
    print(f"Detectives win: {detective_win_count/game_count}")
    pprint(stats)




# def llms_vote_stats(game_records: List[Dict]) -> dict :
#     llms_used = []
#     for game in game_records:
#         llms_used.extend(game["players"].values())
#     llms_used = list(set(llms_used))
#     stats = {llm_name:{"detective_correct_votes":0, "got_votes_as_spy":0} for llm_name in llms_used}
#     for game in game_records:
#         for player_name, player_info in game["llm_info"].items():
#             if player_info["role"] == "detective":
#                 spy_name = f"player_{game['spy']}"
#                 for vote in game["voting_record"]:
#                     if vote["voter"] == player_name and vote["voted_for"] == spy_name:
#                         stats[player_info["llm_type"]]["detective_correct_votes"] +=1
#             else: # player is a spy
#                 for vote in game["voting_record"]:
#                     if vote["voter"] != player_name and vote["voted_for"] == player_name:
#                         stats[player_info["llm_type"]]["got_votes_as_spy"] +=1
#     return stats




def calculate_vote_all_stats(folder_path: str):
    llm_used = ["openai", "gemini", "claude", "deepseek", "grok"]
    stats = {
        llm_name: {
            "detective_correct_votes": 0,
            "total_detective_votes": 0,
            "got_votes_as_spy": 0,
            "spy_games": 0,
            "spy_not_voted": 0  # <-- now this counts individual detective votes that did NOT vote for the spy
        } for llm_name in llm_used
    }

    for filename in os.listdir(folder_path):
        full_path = os.path.join(folder_path, filename)
        with open(full_path, "r") as file:
            games_total_record = json.load(file)

        for game in games_total_record:
            spy_id = game['spy']
            spy_name = f"player_{spy_id}"
            voting_record = game["voting_record"]

            # Count votes by detectives
            for vote in voting_record:
                voter = vote["voter"]
                voted_for = vote["voted_for"]
                voter_info = game["llm_info"][voter]

                if voter_info["role"] == "detective":
                    stats[voter_info["llm_type"]]["total_detective_votes"] += 1
                    if voted_for == spy_name:
                        stats[voter_info["llm_type"]]["detective_correct_votes"] += 1

            # Count votes related to the spy
            for player_name, player_info in game["llm_info"].items():
                if player_info["role"] == "spy":
                    spy_llm = player_info["llm_type"]
                    stats[spy_llm]["spy_games"] += 1

                    for vote in voting_record:
                        if vote["voter"] != player_name:
                            voter_info = game["llm_info"][vote["voter"]]
                            if voter_info["role"] == "detective":
                                if vote["voted_for"] == player_name:
                                    stats[spy_llm]["got_votes_as_spy"] += 1
                                else:
                                    stats[spy_llm]["spy_not_voted"] += 1

    # Add accuracy stats
    for llm_name in stats:
        d = stats[llm_name]
        d["detective_accuracy"] = round(d["detective_correct_votes"] / d["total_detective_votes"], 3) if d["total_detective_votes"] > 0 else None
        # per-vote deception rate = how often detective votes avoided the spy
        total_spy_votes_faced = d["spy_not_voted"] + d["got_votes_as_spy"]
        d["spy_deception_accuracy"] = round(d["spy_not_voted"] / total_spy_votes_faced, 3) if total_spy_votes_faced > 0 else None

    pprint(stats)


print("diff")
calculate_vote_all_stats("generated_data_diff_llm")
print("-"*20)
print("same")
calculate_vote_all_stats("generated_data_same_llm")
print("-"*20)