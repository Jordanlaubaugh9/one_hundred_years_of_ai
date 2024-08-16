import os
import traceback
from openai import OpenAI


class OpenAiService:
    MODEL = "gpt-4o-mini"

    @staticmethod
    def query(system_prompt: str):
        return OpenAiService.create_completion(system_prompt)

    @staticmethod
    def create_completion(system_prompt):
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        try:
            completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                ],
                model=OpenAiService.MODEL,
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            print(
                f"Failed to return result from Open AI Service: {e}. Traceback: {traceback.format_exc()}"
            )
            return None
