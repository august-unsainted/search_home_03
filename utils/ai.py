import asyncio
from openai import AsyncOpenAI

from config import AI_MODEL, AI_PROMPT
from utils.file_system import get_json, write_info
from utils.logger import log

sleep = 5
max_retries = 3
timeout = 60


async def send_ai_request(text: str) -> str | None:
    api_keys = get_json('config')['API_KEYS']
    for i in range(len(api_keys)):
        client = AsyncOpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_keys[i])
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
                api_keys = api_keys[:i] + api_keys[i + 1:] + [api_keys[i]]
                write_info('API_KEYS', api_keys, 'config')
                break
            except Exception as err:
                if isinstance(err, asyncio.TimeoutError):
                    err = 'вышло время ожидания'
                log(f"Ошибка у ключа №{i+1}: {err}, попытка {attempt+1}/{max_retries}.")
                await asyncio.sleep(sleep)
                continue
    return None
