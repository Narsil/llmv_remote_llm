import os
from typing import Optional
from fastapi import HTTPException
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
import aiohttp
from logging import getLogger
from remote_llm.constants import HF_KEY, HF_URL
log = getLogger("generator")

async def generate_openai(prompt: str, preprompt: Optional[str] = None) -> str:
    url = f"{HF_URL}/h4-red-team/o-1"

    payload =  {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
     }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url=url,
                        headers={'Authorization': f'Bearer {HF_KEY}'},
                        json=payload) as raw_response:
            json_response = await raw_response.json()
            # if 'error' in json_response:
            #     log.error(f"Error generating: {json_response['error']}")
            #     raise HTTPException(
            #         HTTP_429_TOO_MANY_REQUESTS, "Too Many Requests", headers={"Retry-After": str(1000)}
            #     )
    generated_text = json_response["choices"][0]["message"]['content']
    return generated_text
