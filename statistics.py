import json
import os
from typing import List, Dict

import numpy as np
from transformers import pipeline
import textstat
import config
from pprint import pprint

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



def calculate_wins(folder_path: str, is_same: bool):
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


print("diff")
calculate_wins("generated_data_diff_llm", is_same=False )
print("-"*20)
print("same")
calculate_wins("generated_data_same_llm", is_same=True)
print("-"*20)



def readability_metrics(text: str) -> float :
    reading_ease = textstat.flesch_reading_ease(text)
    return reading_ease

def readability_analysis_dict(game_records: List[Dict]) -> dict:
    llms_used = []
    for game in game_records:
        llms_used.extend(game["players"].values())
    llms_used = list(set(llms_used))

    results = {llm_name: {"as_detective": {"questions": [], "answers": []}, "as_spy": {"questions": [], "answers": []}}
               for llm_name in llms_used}
    for game in game_records:
        for cr in game['conversation_record']:
            question_player = cr["ask_player"]
            answer_player = cr["respond_player"]
            question = cr["question"]
            answer = cr["answer"]

            question_readability = readability_metrics(question)
            answer_readability = readability_metrics(answer)

            for player_name, player_info in game["llm_info"].items():
                if player_name == question_player and player_info["role"] == "detective":
                    results[player_info["llm_type"]]["as_detective"]["questions"].append(question_readability)
                if player_name == question_player and player_info["role"] == "spy":
                    results[player_info["llm_type"]]["as_spy"]["questions"].append(question_readability)
                if player_name == answer_player and player_info["role"] == "detective":
                    results[player_info["llm_type"]]["as_detective"]["answers"].append(answer_readability)
                if player_name == answer_player and player_info["role"] == "spy":
                    results[player_info["llm_type"]]["as_spy"]["answers"].append(answer_readability)
    return results

def compact_readability_analysis_results(readability_data: dict) -> dict:

    compact_data = {}
    for llm_name, roles_data in readability_data.items():
        compact_data[llm_name] = {}

        for role, metrics in roles_data.items():
            question_readability = metrics['questions']
            answer_readability = metrics['answers']


            readability_scores =  answer_readability + question_readability
            avg_reading_ease = sum(readability_scores) / len(readability_scores)
            generated_text_standard_deviation = float( np.std(readability_scores, ddof=1))

            compact_data[llm_name][role] = {
                "generated_text_count" : len(readability_scores),
                "avg_generated_text_reading_ease": avg_reading_ease,
                "generated_text_standard_deviation":generated_text_standard_deviation
            }
    return compact_data


def load_all_games_from_folder(folder_path: str) -> List[Dict]:
    all_game_records = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            full_path = os.path.join(folder_path, filename)
            with open(full_path, "r") as f:
                try:
                    game_records = json.load(f)
                    all_game_records.extend(game_records)
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
    return all_game_records

# Load data and run the full sentiment analysis pipeline
folder_path = "generated_data_diff_llm"  # Change as needed
all_game_data = load_all_games_from_folder(folder_path)
sentiment_data = readability_analysis_dict(all_game_data)
final_results = compact_readability_analysis_results(sentiment_data)

pprint(final_results)

# Load data and run the full sentiment analysis pipeline
folder_path = "generated_data_same_llm"  # Change as needed
all_game_data = load_all_games_from_folder(folder_path)
readability_data = readability_analysis_dict(all_game_data)
final_results = compact_readability_analysis_results(readability_data)

pprint(final_results)







def sentiment_analyzer(text: str) -> list :
    sa = pipeline(task='sentiment-analysis', model=config.HUGGINGFACE_MODEL)
    return sa(text)


def sentiment_analysis_dict(game_records: List[Dict]) -> dict :
    llm_used = ["openai", "gemini", "claude", "deepseek", "grok"]
    results = {llm_name:{"as_detective":[], "as_spy":[]} for llm_name in llm_used}
    for game in game_records:
        for cr in game['conversation_record']:
            answer_player = cr["respond_player"]
            answer = cr["answer"]
            answer_sentiment = sentiment_analyzer(answer)
            for player_name, player_info in game["llm_info"].items():
                if player_name == answer_player and player_info["role"] == "detective":
                    results[player_info["llm_type"]]["as_detective"].append(answer_sentiment)
                if player_name == answer_player and player_info["role"] == "spy":
                    results[player_info["llm_type"]]["as_spy"].append(answer_sentiment)
    return results

def compact_sent_analysis_results(sentiment_data: dict) -> dict:
    compact_data = {}
    for llm_name, roles_data in sentiment_data.items():
        compact_data[llm_name] = {}
        for role, sentiment_list in roles_data.items():
            positive_scores = []
            neutral_scores = []
            negative_scores = []
            positive_count = 0
            neutral_count = 0
            negative_count = 0

            for sentiments in sentiment_list:
                for sentiment in sentiments:
                    label = sentiment['label'].lower()
                    score = sentiment['score']

                    if label == 'positive':
                        positive_scores.append(score)
                        positive_count += 1
                    elif label == 'negative':
                        negative_scores.append(score)
                        negative_count += 1
                    elif label == 'neutral':
                        neutral_scores.append(score)
                        neutral_count += 1

            avg_positive_score = sum(positive_scores) / len(positive_scores) if positive_scores else 0
            avg_negative_score = sum(negative_scores) / len(negative_scores) if negative_scores else 0
            avg_neutral_score = sum(neutral_scores) / len(neutral_scores) if neutral_scores else 0

            compact_data[llm_name][role] = {
                "positive_count": positive_count,
                "neutral_count": neutral_count,
                "negative_count": negative_count,
                "positive_avg_score": avg_positive_score,
                "neutral_avg_score": avg_neutral_score,
                "negative_avg_score": avg_negative_score
            }
    return compact_data



# Load data and run the full sentiment analysis pipeline
folder_path = "generated_data_diff_llm"  # Change as needed
all_game_data = load_all_games_from_folder(folder_path)
sentiment_data = sentiment_analysis_dict(all_game_data)
final_results = compact_sent_analysis_results(sentiment_data)

pprint(final_results)

# Load data and run the full sentiment analysis pipeline
folder_path = "generated_data_same_llm"  # Change as needed
all_game_data = load_all_games_from_folder(folder_path)
sentiment_data = sentiment_analysis_dict(all_game_data)
final_results = compact_sent_analysis_results(sentiment_data)

pprint(final_results)




