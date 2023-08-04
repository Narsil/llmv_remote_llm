import json
from typing import Optional
from fastapi import HTTPException
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
import aiohttp
from logging import getLogger
from remote_llm.constants import HF_KEY, HF_URL
log = getLogger("generator")

URL = f"{HF_URL}/h4-red-team/o-1"
HEADERS = {'Authorization': f'Bearer {HF_KEY}'}
PARAMETERS = {"temperature": 0.7}

async def generate_openai(prompt: str, preprompt: Optional[str] = None) -> str:

    payload =  {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        **PARAMETERS
     }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url=URL,
                        headers=HEADERS,
                        json=payload) as raw_response:
            json_response = await raw_response.json()
    generated_text = json_response["choices"][0]["message"]['content']
    return generated_text

async def stream_openai(prompt: str, preprompt: Optional[str] = None):
    payload =  {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "stream": True,
        **PARAMETERS
     }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url=URL,
                        headers=HEADERS,
                        json=payload) as raw_response:
            async for line in raw_response.content:
                if line.startswith(b"data:"):
                    data = json.loads(line[len("data:"):])
                    if data["choices"][0]["finish_reason"]:
                        yield ""
                    yield f'data:{json.dumps({"text": data["choices"][0]["delta"]["content"]})}\n'
