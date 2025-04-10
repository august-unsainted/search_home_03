from openai import AsyncOpenAI
from config import AI_KEY1, AI_KEY2, AI_MODEL, AI_PROMPT

keys = [AI_KEY1, AI_KEY2]


async def send_ai_request(text: str) -> str | None:
    for current_key in keys:
        client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=current_key,
        )
        for _ in range(2):
            completion = await client.chat.completions.create(
                model=AI_MODEL,
                messages=[{"role": "user", "content": AI_PROMPT.format(text)}]
            )
            answer = completion.choices[0].message.content
            if answer is not None:
                return answer
    return None
