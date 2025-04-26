import json
from typing import List, Dict
from transformers import pipeline
import textstat
import config

def llms_vote_stats(game_records: List[Dict], llms_used: List[str]) -> dict :
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
    sa = pipeline(task ='sentiment-analysis', model=config.HUGGINGFACE_MODEL)
    return sa(text)

def readability_metrics(text: str) -> list :
    reading_ease = textstat.flesch_reading_ease(text)
    grade_level = textstat.flesch_kincaid_grade(text)
    return [reading_ease, grade_level]



with open("games_total_record.json", "r") as file:
    games_total_record = json.load(file)

# print(llms_vote_stats(games_total_record, ["openai","claude"]))