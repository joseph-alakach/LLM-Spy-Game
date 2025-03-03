import config
import prompts_constants

class Agent:
    LLM_NAMES = ["openai"]
    # ROLES = ["spy", "detective"]

    def __init__(self, llm_name: str, player_name: str, player_role: str):
        self.llm_name = llm_name
        self.player_name = player_name
        self.role = player_role
        self.player_name_conversation_log = []


    def ask_question(self, conversation: dict):
        response = ""
        try:

            if self.llm_name == self.LLM_NAMES[0]:

                llm_response = config.OPENAI_MODEL.chat.completions.create(
                    model=prompts_constants.GPT_4O,
                    messages=[
                        {"role": "system", "content": prompts_constants.SYSTEM_PROMPTS.get(self.role)},
                        # {"role": "user", "content": f"user prompt: {user_prompt}, page name: {page_name}"},
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
            response = (f"{e}"
                        f"Error generating response: llm_name: {self.llm_name}, player_name: {self.player_name}, role: {self.role}")
            return response


    def respond_to_question(self):
        pass


    def vote(self, player):
        pass