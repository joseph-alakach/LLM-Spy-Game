import time

import config
import prompts_constants
from token_utils import count_openai_input_tokens, count_openai_output_tokens


class Agent:

    def __init__(self, llm_name: str, player_name: str, player_role: str, secret_word: str, category: str):
        self.llm_name = llm_name
        self.player_name = player_name
        self.role = player_role
        self.category = category
        self.player_name_conversation_log = []
        self.input_tokens_used = 0
        self.output_tokens_used = 0
        self.thinking_tokens_used = 0
        self.question_generation_durations = []
        self.answer_generation_durations = []
        if self.role == "spy":
            secret_word = ""
        self.secret_word = f"The secret_word is: {secret_word}" if secret_word != "" else "You were not given the secret_word because you are a spy"

        if self.llm_name == "human":
            print(f"You are participating in the game as {self.player_name}, your role in the game is ({self.role}), {self.secret_word}")

    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        if self.llm_name == "openai":
            llm_response = config.OPENAI_CLIENT.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages= [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
            )
            output_text = llm_response.choices[0].message.content.strip()
            self.input_tokens_used += llm_response.usage.prompt_tokens
            self.output_tokens_used += (llm_response.usage.completion_tokens - llm_response.usage.completion_tokens_details.reasoning_tokens)
            self.thinking_tokens_used += llm_response.usage.completion_tokens_details.reasoning_tokens

        elif self.llm_name == "gemini":
            prompt = system_prompt + "\n\n" + user_prompt
            llm_response = config.GEMINI_CLIENT.models.generate_content(
                model=config.GEMINI_MODEL,
                contents=prompt,
            )
            output_text = llm_response.text.strip() if hasattr(llm_response, "text") else ""
            self.input_tokens_used += llm_response.usage_metadata.prompt_token_count
            self.output_tokens_used += llm_response.usage_metadata.candidates_token_count
            self.thinking_tokens_used += llm_response.usage_metadata.thoughts_token_count

        elif self.llm_name == "deepseek":
            llm_response = config.DEEPSEEK_CLIENT.chat.completions.create(
                model=config.DEEPSEEK_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.00000001,
            )
            output_text = llm_response.choices[0].message.content.strip()
            self.input_tokens_used += llm_response.usage.prompt_tokens
            self.output_tokens_used += (llm_response.usage.completion_tokens - llm_response.usage.completion_tokens_details.reasoning_tokens)
            self.thinking_tokens_used += llm_response.usage.completion_tokens_details.reasoning_tokens

        elif self.llm_name == "claude":
            llm_response = config.CLAUDE_CLIENT.messages.create(
                model=config.CLAUDE_MODEL,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=6000,
                thinking={
                    "type": "enabled",
                    "budget_tokens": 5000
                }
            )
            output_text = llm_response.content[1].text.strip() if hasattr(llm_response, "content") else ""
            self.input_tokens_used += llm_response.usage.input_tokens
            self.output_tokens_used += llm_response.usage.output_tokens

        elif self.llm_name == "grok":
            llm_response = config.GROK_CLIENT.chat.completions.create(
                model=config.GROK_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.000000001
            )
            output_text = llm_response.choices[0].message.content.strip()
            self.input_tokens_used += llm_response.usage.prompt_tokens
            self.output_tokens_used += llm_response.usage.completion_tokens
            self.thinking_tokens_used += llm_response.usage.completion_tokens_details.reasoning_tokens

        return output_text

    def ask_question(self, conversation: str) -> str:
        print("ask_question")
        system_message = (
            f"{prompts_constants.SYSTEM_PROMPTS.get('rules')} \n"
            f"{prompts_constants.SYSTEM_PROMPTS.get(self.role)} \n"
            f"The secret word belongs to the category: {self.category} \n"
            f"Your name in the game is: {self.player_name} \n"
            f"{self.secret_word}"
        )
        user_message = (
            f"This is the conversation record so far: {conversation}. \n\n"
            "- Do NOT ask a question that has already been asked before. \n"
            "- You must come up with a new question that has not been asked. \n"
            "- Ask short questions related to the secret word but it should be vague in order to not give away the secret word to the spy. \n"
            "- Return only the question sentence do not add anything else. \n\n"
            "Your question: "
        )
        question = ""
        if self.llm_name != "human":
            start_time = time.time()
            question = self._call_llm(system_message, user_message)
            end_time = time.time()
            self.question_generation_durations.append(end_time - start_time)
        else:
            print(f"This is the conversation record so far: {conversation}. \n\n")
            question = input(f"As {self.player_name} role:({self.role}) insert the question you want to ask to the next player: ")
        self.player_name_conversation_log.append(question)
        return question

    def respond_to_question(self, conversation: str) -> str:
        print("respond_to_question")
        system_message = f"""{prompts_constants.SYSTEM_PROMPTS.get('rules')}
            {prompts_constants.SYSTEM_PROMPTS.get(self.role)}
            Your name in the game is: {self.player_name}
            {self.secret_word}

            Your task now is to respond only to the question directed at you."""

        user_message = f"""This is the conversation record so far: {conversation}
            Now it is your turn to respond to the last question in the conversation record.
            The last question in the conversation record is directed at you. 
            
            Your response to the last question in the conversation record: 

            Give only the response to the question, don't add anything else in the beginning and the end."""

        response = ""
        if self.llm_name != "human":
            start_time = time.time()
            response = self._call_llm(system_message, user_message)
            end_time = time.time()
            self.answer_generation_durations.append(end_time - start_time)
        else:
            print(f"This is the conversation record so far: {conversation}. \n\n")
            print("Now it is your turn to respond to the last question in the conversation record.")
            response = input(f"As {self.player_name} role:({self.role}) insert the answer to respond to the last question: ")
        self.player_name_conversation_log.append(response)
        return response

    def vote(self, conversation: str, number_of_players: int) -> tuple:
        print("vote")
        response = ""
        explanation = ""
        list_of_players = [f'player_{i}' for i in range(number_of_players)]
        system_message = (
            f"{prompts_constants.SYSTEM_PROMPTS.get('rules')} \n"
            f"{prompts_constants.SYSTEM_PROMPTS.get(self.role)} \n"
            f"Your name in the game is: {self.player_name} \n"
            f"{self.secret_word}"
        )
        user_message = (
            f"""This is the conversation record so far: {conversation}. \n
                - Now it is the **voting round**. 
                - Choose the **player you suspect the most** based on their answers. 
                - You are not allowed to vote for yourself.
                - Select from this list: {list_of_players}.
                - **Return only one name in this format**: player_# 
                - **Then, explain why you are voting for them in a short statement.**
            
                Example response:  
                player_3  
                "I believe player_3 is the spy because their answer to X question was inconsistent with the secret word."
            
                Your response:"""
        )
        if self.llm_name != "human":
            output_text = self._call_llm(system_message, user_message)
            lines = output_text.split("\n", 1)
            response = lines[0].strip().replace("player_", "")
            explanation = lines[1].strip() if len(lines) > 1 else "No explanation provided."
        else:
            print(f"This is the conversation record so far: {conversation}. \n\n")
            print("""- Now it is the **voting round**. 
                - Choose the **player you suspect the most** based on their answers. 
                - You are not allowed to vote for yourself.
                - Select from this list: {list_of_players}.
                - **insert only one name in this format**: player_#""")
            response = input(f"As {self.player_name} role:({self.role}) insert the player_# to vote him out: ")
            response = response.strip().replace("player_", "")
        response = int(response)
        self.player_name_conversation_log.append((response, explanation))
        return response, explanation

    def guess_secret_word(self, conversation: str) -> str:
        print("guess_secret_word")
        system_message = (
            f"{prompts_constants.SYSTEM_PROMPTS.get('rules')} \n"
            f"{prompts_constants.SYSTEM_PROMPTS.get(self.role)} \n"
            f"You are the spy. You were just caught, but you now have one chance to guess the secret word."
        )
        user_message = (
            f"Here is the full conversation record: {conversation} \n\n"
            "Based on this, make your best guess of the secret word. Respond with only the word, nothing else."
        )
        response = ""
        if self.llm_name != "human":
            response = self._call_llm(system_message, user_message)
        elif self.llm_name == "human":
            print(f"This is the conversation record so far: {conversation}. \n\n")
            print("As you know you are the spy and the players have voted you out"
                  "but you still have the chance to win by guessing the secret word Based on this, make your best guess of the secret word. Respond with only the word, nothing else.")
            response = input(f"As {self.player_name} role:({self.role}) insert your guess of the secret word: ")
        return response