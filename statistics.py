import json
from typing import List, Dict
from transformers import pipeline
import textstat
import config
from pprint import pprint

def llms_vote_stats(game_records: List[Dict]) -> dict :
    llms_used = []
    for game in game_records:
        llms_used.extend(game["players"].values())
    llms_used = list(set(llms_used))
    stats = {llm_name:{"detective_correct_votes":0, "got_votes_as_spy":0} for llm_name in llms_used}
    for game in game_records:
        for player_name, player_info in game["llm_info"].items():
            if player_info["role"] == "detective":
                spy_name = f"player_{game['spy']}"
                for vote in game["voting_record"]:
                    if vote["voter"] == player_name and vote["voted_for"] == spy_name:
                        stats[player_info["llm_type"]]["detective_correct_votes"] +=1
            else: # player is a spy
                for vote in game["voting_record"]:
                    if vote["voter"] != player_name and vote["voted_for"] == player_name:
                        stats[player_info["llm_type"]]["got_votes_as_spy"] +=1
    return stats


def sentiment_analyzer(text: str) -> list :
    sa = pipeline(task='sentiment-analysis', model=config.HUGGINGFACE_MODEL)
    return sa(text)

def readability_metrics(text: str) -> list :
    reading_ease = textstat.flesch_reading_ease(text)
    grade_level = textstat.flesch_kincaid_grade(text)
    return [reading_ease, grade_level]

def sentiment_analysis_dict(game_records: List[Dict]) -> dict :
    llms_used = []
    for game in game_records:
        llms_used.extend(game["players"].values())
    llms_used = list(set(llms_used))
    results = {llm_name:{"as_detective":[], "as_spy":[]} for llm_name in llms_used}
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

            question_count = len(question_readability)
            answer_count = len(answer_readability)

            avg_question_reading_ease = sum([metric[0] for metric in question_readability]) / question_count if question_count > 0 else 0
            avg_question_grade_level = sum([metric[1] for metric in question_readability]) / question_count if question_count > 0 else 0

            avg_answer_reading_ease = sum([metric[0] for metric in answer_readability]) / answer_count if answer_count > 0 else 0
            avg_answer_grade_level = sum([metric[1] for metric in answer_readability]) / answer_count if answer_count > 0 else 0

            compact_data[llm_name][role] = {
                "question_count": question_count,
                "answer_count": answer_count,
                "avg_question_reading_ease": avg_question_reading_ease,
                "avg_question_grade_level": avg_question_grade_level,
                "avg_answer_reading_ease": avg_answer_reading_ease,
                "avg_answer_grade_level": avg_answer_grade_level
            }
    return compact_data


with open("games_total_record.json", "r") as file:
    games_total_record = json.load(file)

print(llms_vote_stats(games_total_record))
# pprint(compact_sent_analysis_results(sentiment_analysis_dict(games_total_record)))
# pprint(compact_readability_analysis_results(readability_analysis_dict(games_total_record)))