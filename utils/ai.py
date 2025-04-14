import asyncio
from openai import AsyncOpenAI

from config import API_KEYS, AI_MODEL, AI_PROMPT
from utils.logger import log

sleep = 5
max_retries = 3
timeout = 60


async def send_ai_request(text: str) -> str | None:
    for i in range(len(API_KEYS)):
        client = AsyncOpenAI(base_url="https://openrouter.ai/api/v1", api_key=API_KEYS[i])
        for attempt in range(max_retries):
            try:
                completion = await asyncio.wait_for(
                    client.chat.completions.create(
                        model=AI_MODEL,
                        messages=[{"role": "user", "content": AI_PROMPT.format(text)}]
                    ),
                    timeout=timeout
                )
                answer = completion.choices[0].message.content
                return answer
            except TypeError:
                log(f'Ошибка у ключа №{i+1}: закончились запросы, пробую следующий.')
                break
            except asyncio.TimeoutError:
                log(f"Ошибка у ключа №{i+1}: вышло время ожидания, попытка {attempt+1}/{max_retries}.")
                await asyncio.sleep(sleep)
                continue
            except Exception as e:
                log(f"Ошибка у ключа №{i+1}: {e}, попытка {attempt+1}/{max_retries}.")
                await asyncio.sleep(sleep)
                continue
    return None
