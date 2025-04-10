import config
import prompts_constants
from token_utils import count_openai_input_tokens, count_openai_output_tokens


class Agent:

    def __init__(self, llm_name: str, player_name: str, player_role: str, secret_word: str, category: str):
        self.llm_name = llm_name
        self.player_name = player_name
        self.role = player_role
        self.category = category
        self.secret_word = f"The secret_word is: {secret_word}" if secret_word != "" else "You were not given the secret_word because you are a spy"
        self.player_name_conversation_log = []
        self.input_tokens_used = 0
        self.output_tokens_used = 0

    def ask_question(self, conversation: str) -> str:
        print("ask_question")
        question = ""
        try:
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
                "- Ensure that the question is relevant and helps progress the game. \n"
                "- Return only the question. \n\n"
                "Your question:"
            )

            if self.llm_name == "openai":
                messages = [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ]

                # Count input tokens before sending
                input_tokens = count_openai_input_tokens(messages, model=config.OPENAI_MODEL)

                # Call OpenAI API
                llm_response = config.OPENAI_CLIENT.chat.completions.create(
                    model=config.OPENAI_MODEL,
                    messages=messages,
                    # temperature=0.3,
                )

                output_text = llm_response.choices[0].message.content.strip()
                output_tokens = count_openai_output_tokens(output_text, model=config.OPENAI_MODEL)

                # Update the agent’s token counters
                self.input_tokens_used += input_tokens
                self.output_tokens_used += output_tokens
                question = output_text

            elif self.llm_name == "gemini":
                chat = config.GEMINI_MODEL.start_chat()
                response = chat.send_message(system_message + "\n\n" + user_message)

                question = response.text.strip() if hasattr(response, "text") else ""

            elif self.llm_name == "deepseek":
                llm_response = config.DEEPSEEK_CLIENT.chat.completions.create(
                    model=config.DEEPSEEK_MODEL,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.3,
                )
                question = llm_response.choices[0].message.content.strip()

            elif self.llm_name == "claude":
                llm_response = config.CLAUDE_CLIENT.messages.create(
                    model=config.CLAUDE_MODEL,
                    system=system_message,
                    messages=[
                        {"role": "user", "content": user_message}
                    ],
                    max_tokens=256
                )
                question = llm_response.content[0].text.strip() if hasattr(llm_response, "content") else ""

            if question == "":
                raise Exception("Empty question returned.")

            self.player_name_conversation_log.append(question)
            return question

        except Exception as e:
            print(f"[ask_question error] {e}")
            return f"Error generating question: llm_name: {self.llm_name}, player_name: {self.player_name}, role: {self.role}"

    def respond_to_question(self, conversation: str) -> str:
        print("respond_to_question")
        response = ""
        try:
            system_message = (
                f"{prompts_constants.SYSTEM_PROMPTS.get('rules')} \n"
                f"{prompts_constants.SYSTEM_PROMPTS.get(self.role)} \n"
                f"Your name in the game is: {self.player_name} \n"
                f"{self.secret_word}"
            )

            user_message = (
                f"This is the conversation record so far: {conversation} \n\n"
                "Now it is your turn to respond to the last question in the conversation record.\n"
                "Return only your response."
            )

            if self.llm_name == "openai":
                messages = [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ]

                input_tokens = count_openai_input_tokens(messages, model=config.OPENAI_MODEL)

                llm_response = config.OPENAI_CLIENT.chat.completions.create(
                    model=config.OPENAI_MODEL,
                    messages=messages,
                    # temperature=0.3,
                )

                output_text = llm_response.choices[0].message.content.strip()
                output_tokens = count_openai_output_tokens(output_text, model=config.OPENAI_MODEL)

                self.input_tokens_used += input_tokens
                self.output_tokens_used += output_tokens
                response = output_text

            elif self.llm_name == "gemini":
                chat = config.GEMINI_MODEL.start_chat()
                response = chat.send_message(system_message + "\n\n" + user_message)

                response = response.text.strip() if hasattr(response, "text") else ""

            elif self.llm_name == "deepseek":
                llm_response = config.DEEPSEEK_CLIENT.chat.completions.create(
                    model=config.DEEPSEEK_MODEL,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.3,
                )
                response = llm_response.choices[0].message.content.strip()

            elif self.llm_name == "claude":
                llm_response = config.CLAUDE_CLIENT.messages.create(
                    model=config.CLAUDE_MODEL,
                    system=system_message,
                    messages=[
                        {"role": "user", "content": user_message}
                    ],
                    max_tokens=256
                )
                response = llm_response.content[0].text.strip() if hasattr(llm_response, "content") else ""

            if response == "":
                raise Exception("Empty response returned.")

            self.player_name_conversation_log.append(response)
            return response

        except Exception as e:
            print(f"[respond_to_question error] {e}")
            return f"Error generating response: llm_name: {self.llm_name}, player_name: {self.player_name}, role: {self.role}"

    def vote(self, conversation: str, number_of_players: int) -> tuple:
        print("vote")
        response = ""
        explanation = ""
        list_of_players = [f'player_{i}' for i in range(number_of_players)]

        try:
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

            if self.llm_name == "openai":
                messages = [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ]

                input_tokens = count_openai_input_tokens(messages, model=config.OPENAI_MODEL)

                llm_response = config.OPENAI_CLIENT.chat.completions.create(
                    model=config.OPENAI_MODEL,
                    messages=messages,
                    # temperature=0.3,
                )

                output_text = llm_response.choices[0].message.content.strip()
                output_tokens = count_openai_output_tokens(output_text, model=config.OPENAI_MODEL)

                self.input_tokens_used += input_tokens
                self.output_tokens_used += output_tokens

                lines = output_text.split("\n", 1)
                response = lines[0].strip().replace("player_", "")
                explanation = lines[1].strip() if len(lines) > 1 else "No explanation provided."
                response = int(response)

            elif self.llm_name == "gemini":
                chat = config.GEMINI_MODEL.start_chat()
                gemini_response = chat.send_message(system_message + "\n\n" + user_message)

                if hasattr(gemini_response, "text"):
                    lines = gemini_response.text.strip().split("\n", 1)
                    response = lines[0].strip().replace("player_", "")
                    explanation = lines[1].strip() if len(lines) > 1 else "No explanation provided."

            elif self.llm_name == "deepseek":
                llm_response = config.DEEPSEEK_CLIENT.chat.completions.create(
                    model=config.DEEPSEEK_MODEL,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.3,
                )
                lines = llm_response.choices[0].message.content.strip().split("\n", 1)
                response = lines[0].strip().replace("player_", "")
                explanation = lines[1].strip() if len(lines) > 1 else "No explanation provided."

            elif self.llm_name == "claude":
                llm_response = config.CLAUDE_CLIENT.messages.create(
                    model=config.CLAUDE_MODEL,
                    system=system_message,
                    messages=[
                        {"role": "user", "content": user_message}
                    ],
                    max_tokens=256
                )
                if hasattr(llm_response, "content"):
                    lines = llm_response.content[0].text.strip().split("\n", 1)
                    response = lines[0].strip().replace("player_", "")
                    explanation = lines[1].strip() if len(lines) > 1 else "No explanation provided."

            if response == "":
                raise Exception("Empty vote returned.")
            response = int(response)

            self.player_name_conversation_log.append((response, explanation))
            return response, explanation

        except Exception as e:
            print(f"[vote error] {e}")
            return -1, "Error in generating vote explanation."

    def guess_secret_word(self, conversation: str) -> str:
        # print("guess_secret_word")
        try:
            system_message = (
                f"{prompts_constants.SYSTEM_PROMPTS.get('rules')} \n"
                f"{prompts_constants.SYSTEM_PROMPTS.get(self.role)} \n"
                f"You are the spy. You were just caught, but you now have one chance to guess the secret word."
            )

            user_message = (
                f"Here is the full conversation record: {conversation} \n\n"
                "Based on this, make your best guess of the secret word. Respond with only the word, nothing else."
            )

            if self.llm_name == "openai":
                messages = [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ]

                input_tokens = count_openai_input_tokens(messages, model=config.OPENAI_MODEL)

                llm_response = config.OPENAI_CLIENT.chat.completions.create(
                    model=config.OPENAI_MODEL,
                    messages=messages,
                    # temperature=0.3,
                )

                output_text = llm_response.choices[0].message.content.strip()
                output_tokens = count_openai_output_tokens(output_text, model=config.OPENAI_MODEL)

                self.input_tokens_used += input_tokens
                self.output_tokens_used += output_tokens

                return output_text

            elif self.llm_name == "gemini":
                chat = config.GEMINI_MODEL.start_chat()
                gemini_response = chat.send_message(system_message + "\n\n" + user_message)
                return gemini_response.text.strip() if hasattr(gemini_response, "text") else "unknown"

            elif self.llm_name == "deepseek":
                llm_response = config.DEEPSEEK_CLIENT.chat.completions.create(
                    model=config.DEEPSEEK_MODEL,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.3,
                )
                return llm_response.choices[0].message.content.strip()

            elif self.llm_name == "claude":
                llm_response = config.CLAUDE_CLIENT.messages.create(
                    model=config.CLAUDE_MODEL,
                    system=system_message,
                    messages=[
                        {"role": "user", "content": user_message}
                    ],
                    max_tokens=256
                )
                return llm_response.content[0].text.strip() if hasattr(llm_response, "content") else "unknown"

            return "unknown"

        except Exception as e:
            print(f"[guess_secret_word error] {e}")
            return "error"
