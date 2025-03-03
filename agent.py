import config
import prompts_constants

class Agent:
    LLM_NAMES = ["openai"]
    # ROLES = ["spy", "detective"]

    def __init__(self, llm_name: str, player_name: str, player_role: str, secret_word: str):
        self.llm_name = llm_name
        self.player_name = player_name
        self.role = player_role
        self.secret_word = f"The secret_word is : {secret_word}" if secret_word != "" else "You were not given the secret_word"
        self.player_name_conversation_log = []


    def ask_question(self, conversation: str) -> str:
        question = ""
        try:

            if self.llm_name == self.LLM_NAMES[0]:

                llm_response = config.OPENAI_MODEL.chat.completions.create(
                    model=prompts_constants.GPT_4O,
                    messages=[
                        {"role": "system",
                         "content": f"{prompts_constants.SYSTEM_PROMPTS.get('rules')} \n{prompts_constants.SYSTEM_PROMPTS.get(self.role)} \nYour name in the game is: {self.player_name} \n{self.secret_word}" },
                        {"role": "user",
                         "content": f"This is the conversation record so far {conversation}. \n Now it is your turn to ask a question to the player next to you, ask a question. Return only the question: Your question: "},
                    ],
                    temperature=0.3,
                )
                question = llm_response.choices[0].message.content

            else:
                pass

            if question == "":
                raise Exception

            self.player_name_conversation_log.append(question)
            return question

        except Exception as e:
            print(e)
            return f"Error generating question: llm_name: {self.llm_name}, player_name: {self.player_name}, role: {self.role}"


    def respond_to_question(self, conversation: str) -> str:
        response = ""
        try:

            if self.llm_name == self.LLM_NAMES[0]:

                llm_response = config.OPENAI_MODEL.chat.completions.create(
                    model=prompts_constants.GPT_4O,
                    messages=[
                        {"role": "system",
                         "content": f"{prompts_constants.SYSTEM_PROMPTS.get('rules')} \n{prompts_constants.SYSTEM_PROMPTS.get(self.role)} \nYour name in the game is: {self.player_name} \n{self.secret_word}"},
                        {"role": "user",
                         "content": f"This is the conversation record so far {conversation}. \nNow it is your turn to respond to the last question in the conversation record. Return only your response: Your response: "},
                    ],
                    temperature=0.3,
                )
                response = llm_response.choices[0].message.content

            else:
                pass

            if response == "":
                raise Exception

            self.player_name_conversation_log.append(response)
            return response

        except Exception as e:
            print(e)
            return f"Error generating response: llm_name: {self.llm_name}, player_name: {self.player_name}, role: {self.role}"


    def vote(self, conversation: str, number_of_players: int) -> int:
        response = ""
        list_of_players = [f'player_{i}' for i in range(number_of_players)]
        try:

            if self.llm_name == self.LLM_NAMES[0]:

                llm_response = config.OPENAI_MODEL.chat.completions.create(
                    model=prompts_constants.GPT_4O,
                    messages=[
                        {"role": "system",
                         "content": f"{prompts_constants.SYSTEM_PROMPTS.get('rules')} \n{prompts_constants.SYSTEM_PROMPTS.get(self.role)} \nYour name in the game is: {self.player_name} \n{self.secret_word}"},
                        {"role": "user",
                         "content": f"This is the conversation record so far {conversation}. \nNow it is the voting round based on the conversation record vote a player. From this list choose only 1 {list_of_players}. Your response: "},
                    ],
                    temperature=0.3,
                )
                response = llm_response.choices[0].message.content.replace("player_","")
                response = int(response)

            else:
                pass

            if response == "":
                raise Exception

            self.player_name_conversation_log.append(response)
            return response

        except Exception as e:
            print(e)
            return -1