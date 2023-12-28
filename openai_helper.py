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
                    {"role": "system", "content": "You are a helpful assistant designed to help in prepare summary from conversation."},
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
