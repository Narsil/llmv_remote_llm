import json
from typing import Optional
from fastapi import HTTPException
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
import aiohttp
from logging import getLogger
from remote_llm.constants import HF_KEY, HF_URL
log = getLogger("generator")

URL = f"{HF_URL}/h4-red-team/st-1"
PARAMETERS = {
    "max_new_tokens": 512,
    "temperature": 0.5,
    "top_p": 0.95
}
HEADERS = {'Authorization': f'Bearer {HF_KEY}'}

async def generate_stability(prompt: str, preprompt: Optional[str] = None) -> str:
    full_prompt = prompt
    payload = {'inputs': {"text":full_prompt, "past_user_inputs":[], "generated_responses":[]}, "parameters" : PARAMETERS}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url=URL,
                        headers=HEADERS,
                        json=payload) as raw_response:
            generated_text = ""
            async for line in raw_response.content:
                line = line.strip()
                if line:
                    data = json.loads(line[6:])
                    generated_text += data["text"]
            # if 'error' in json_response:
            #     log.error(f"Error generating: {json_response['error']}")
            #     raise HTTPException(
            #         HTTP_429_TOO_MANY_REQUESTS, "Too Many Requests", headers={"Retry-After": str(1000)}
            #     )
    return generated_text

async def stream_stability(prompt: str, preprompt: Optional[str] = None):
    full_prompt = prompt
    payload = {'inputs': {"text":full_prompt, "past_user_inputs":[], "generated_responses":[]}, "parameters" : PARAMETERS}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url=URL,
                        headers=HEADERS,
                        json=payload) as raw_response:
            generated_text = ""
            async for line in raw_response.content:
                if line.startswith(b"data:"):
                    data = json.loads(line[len("data:"):])
                    yield f'data:{json.dumps({"text": data["text"]})}\n'
