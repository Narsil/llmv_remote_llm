import json
from typing import Optional
from fastapi import HTTPException
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
import aiohttp
from logging import getLogger
from remote_llm.constants import HF_KEY, HF_URL
log = getLogger("generator")

URL = f"{HF_URL}/h4-red-team/f-1"
PARAMETERS = {
    "max_new_tokens": 1024,
    "repetition_penalty": 1.2,
    "return_full_text": False,
    "top_p": 0.95,
    "temperature": 0.9,
    "stop": ["<|endoftext|>"]
}
HEADERS = {'Authorization': f'Bearer {HF_KEY}'}

async def generate_huggingface(prompt: str, preprompt: Optional[str] = None) -> str:
    full_prompt = f"<|system|>{preprompt}<|prompter|>{prompt}<|endoftext|><|assistant|>"
    payload = {'inputs': full_prompt, "parameters" : PARAMETERS, "stream": False}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
                url=URL,
                headers=HEADERS,
                json=payload) as raw_response:
            json_response = await raw_response.json()
            if 'error' in json_response:
                log.error(f"Error generating: {json_response['error']}")
                raise HTTPException(
                    HTTP_429_TOO_MANY_REQUESTS, "Too Many Requests", headers={"Retry-After": str(1000)}
                )
    generated_text = json_response[0]['generated_text']
    return generated_text

async def stream_huggingface(prompt: str, preprompt: Optional[str] = None):
    full_prompt = f"<|system|>{preprompt}<|prompter|>{prompt}<|endoftext|><|assistant|>"
    payload = {'inputs': full_prompt, "parameters" : PARAMETERS, "stream": True}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
                url=URL,
                headers=HEADERS,
                json=payload) as raw_response:
            async for line in raw_response.content:
                if line.startswith(b"data:"):
                    data = json.loads(line[len("data:"):])
                    yield f'data:{json.dumps({"text": data["token"]["text"]})}\n'
