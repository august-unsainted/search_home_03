from openai import AsyncOpenAI
from config import API_KEYS, AI_MODEL, AI_PROMPT


async def send_ai_request(text: str) -> str | None:
    for current_key in API_KEYS:
        client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=current_key,
        )
        for _ in range(2):
            try:
                completion = await client.chat.completions.create(
                    model=AI_MODEL,
                    messages=[{"role": "user", "content": AI_PROMPT.format(text)}]
                )
                answer = completion.choices[0].message.content
                if answer:
                    return answer
            except TypeError:
                continue

    return None
