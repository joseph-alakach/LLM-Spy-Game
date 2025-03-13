import config
import prompts_constants

class Agent:
    LLM_NAMES = ["openai"]

    def __init__(self, llm_name: str, player_name: str, player_role: str, secret_word: str):
        self.llm_name = llm_name
        self.player_name = player_name
        self.role = player_role
        self.secret_word = f"The secret_word is: {secret_word}" if secret_word != "" else "You were not given the secret_word"
        self.player_name_conversation_log = []


    def ask_question(self, conversation: str) -> str:
        question = ""
        try:

            if self.llm_name == self.LLM_NAMES[0]:

                llm_response = config.OPENAI_MODEL.chat.completions.create(
                    model=prompts_constants.GPT_4O,
                    messages=[
                        {"role": "system",
                         "content": f"{prompts_constants.SYSTEM_PROMPTS.get('rules')} \n"
                                    f"{prompts_constants.SYSTEM_PROMPTS.get(self.role)} \n"
                                    f"Your name in the game is: {self.player_name} \n"
                                    f"{self.secret_word}"},
                        {"role": "user",
                         "content": f"""This is the conversation record so far: {conversation}. 

                         - **Do NOT ask a question that has already been asked before.** 
                         - **You must come up with a new question that has not been asked.**
                         - **Ensure that the question is relevant and helps progress the game.**
                         - **Return only the question.** 

                         Your question:"""},
                    ],
                    temperature=0.3,
                )
                question = llm_response.choices[0].message.content

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
                         "content": f"{prompts_constants.SYSTEM_PROMPTS.get('rules')} \n"
                                    f"{prompts_constants.SYSTEM_PROMPTS.get(self.role)} \n"
                                    f"Your name in the game is: {self.player_name} \n"
                                    f"{self.secret_word}"},
                        {"role": "user",
                         "content": f"This is the conversation record so far {conversation}. \n"
                                    f"Now it is your turn to respond to the last question in the conversation record. "
                                    f"Return only your response:"},
                    ],
                    temperature=0.3,
                )
                response = llm_response.choices[0].message.content

            if response == "":
                raise Exception

            self.player_name_conversation_log.append(response)
            return response

        except Exception as e:
            print(e)
            return f"Error generating response: llm_name: {self.llm_name}, player_name: {self.player_name}, role: {self.role}"

    def vote(self, conversation: str, number_of_players: int) -> tuple:
        response = ""
        explanation = ""
        list_of_players = [f'player_{i}' for i in range(number_of_players)]
        try:
            if self.llm_name == self.LLM_NAMES[0]:
                llm_response = config.OPENAI_MODEL.chat.completions.create(
                    model=prompts_constants.GPT_4O,
                    messages=[
                        {"role": "system",
                         "content": f"{prompts_constants.SYSTEM_PROMPTS.get('rules')} \n"
                                    f"{prompts_constants.SYSTEM_PROMPTS.get(self.role)} \n"
                                    f"Your name in the game is: {self.player_name} \n"
                                    f"{self.secret_word}"},
                        {"role": "user",
                         "content": f"""This is the conversation record so far: {conversation}. 

                         - Now it is the **voting round**. 
                         - Choose the **player you suspect the most** based on their answers. 
                         - Select from this list: {list_of_players}.
                         - **Return only one name in this format**: player_# 
                         - **Then, explain why you are voting for them in a short statement.**

                         Example response:  
                         player_3  
                         "I believe player_3 is the spy because their answer to X question was inconsistent with the secret word."

                         Your response:"""},
                    ],
                    temperature=0.3,
                )
                response_lines = llm_response.choices[0].message.content.split("\n", 1)
                response = response_lines[0].strip().replace("player_", "")
                explanation = response_lines[1].strip() if len(response_lines) > 1 else "No explanation provided."

                response = int(response)

            if response == "":
                raise Exception

            self.player_name_conversation_log.append((response, explanation))
            return response, explanation

        except Exception as e:
            print(e)
            return -1, "Error in generating vote explanation."