from openai import OpenAI
from config import AI_KEY, AI_MODEL, AI_PROMPT

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=AI_KEY,
)


async def send_ai_request(text: str) -> str:
    completion = client.chat.completions.create(
        model=AI_MODEL,
        messages=[{"role": "user",
                   "content": AI_PROMPT.format(text)}])
    return completion.choices[0].message.content
