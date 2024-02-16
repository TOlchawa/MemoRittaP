import os
import json
from openai import AsyncOpenAI

class OpenAIHelper:
    def __init__(self):
        openai_api_key = os.getenv('OPENAI_API_KEY')
        self.max_tokens = int(os.getenv('OPENAI_MAX_TOKENS', 256))
        self.client_openai = AsyncOpenAI(
            api_key=openai_api_key,  # this is also the default, it can be omitted
            organization='org-n9AnfI7a4lvpGr50hbypFLxB',
        )

    async def ask_openai(self, question):
        try:
            completion = await self.client_openai.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=[
                    {"role": "system", "content": "Jesteś bardzo dobrze wykształconym filozofem z obszerną wiedzą socjopolityczną (ze specjalizacją w historii politycznej USA). "
                                                  "Odpowiadaj w stylu Harvardzkim, kierując się zasadami podobnymi do tych stosowanych w debatach uniwersyteckich. "
                                                  "Odpowiadaj w języku, w którym zostało zadane pytanie."},
                    {"role": "user", "content": question}
                ],
                max_tokens=self.max_tokens
            )

            response_str = completion.model_dump_json(indent=2)
            response_json = json.loads(response_str)
            response_txt = response_json['choices'][0]['message']['content']

            return response_txt
        except Exception as e:
            return 'An error occurred: {}'.format(str(e))


    async def summarize_messages(self, message_list):
        messages = [
            {"role": "user", "content": msg} for msg in message_list
        ]

        try:
            completion = await self.client_openai.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=[
                             {"role": "system",
                              "content":
                                 "1. Zidentyfikuj kluczowe tematy dyskusji i wyróżnij główne argumenty przedstawione przez uczestników.\n" +
                                 "2. Zwróć uwagę na wszelkie wspólne wnioski lub obszary zgody między uczestnikami.\n" +
                                 "3. Podkreśl wszelkie istotne pytania, wątpliwości lub obszary kontrowersji, które pojawiły się w trakcie dyskusji.\n" +
                                 "4. Zapewnij krótkie wprowadzenie i zakończenie, które łączy całe podsumowanie i podkreśla znaczenie dyskusji.\n" +
                                 "5. Staraj się zachować neutralny ton i obiektywnie przedstawiać różne punkty widzenia.\n" +
                                 "Po zakończeniu, przedstaw podsumowanie w jasny i uporządkowany sposób, umożliwiając szybkie zrozumienie głównych punktów dyskusji."},
                         ] + messages,
                max_tokens=self.max_tokens
            )

            response_str = completion.model_dump_json(indent=2)
            response_json = json.loads(response_str)
            response_txt = response_json['choices'][0]['message']['content']

            return response_txt
        except Exception as e:
            return 'An error occurred: {}'.format(str(e))