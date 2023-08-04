import os
from typing import Optional
from fastapi import HTTPException
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
import aiohttp
from logging import getLogger
from remote_llm.constants import HF_KEY, HF_URL
log = getLogger("generator")

async def generate_huggingface(prompt: str, preprompt: Optional[str] = None) -> str:
    url = f"{HF_URL}/h4-red-team/f-1"
    
    parameters = {
        "max_new_tokens": 1024,
        "repetition_penalty": 1.2,
        "return_full_text": False,
        "top_p": 0.95,
        "temperature": 0.9,
        "stop": ["<|endoftext|>"]
    }
    full_prompt = f"<|system|>{preprompt}<|prompter|>{prompt}<|endoftext|><|assistant|>"
    headers = {'Authorization': f'Bearer {HF_KEY}'}

    
    async with aiohttp.ClientSession() as session:
        async with session.post(
                url=url,
                headers=headers,
                json={'inputs': full_prompt, "parameters" : parameters, "stream:": False}) as raw_response:
            json_response = await raw_response.json()
            if 'error' in json_response:
                log.error(f"Error generating: {json_response['error']}")
                raise HTTPException(
                    HTTP_429_TOO_MANY_REQUESTS, "Too Many Requests", headers={"Retry-After": str(1000)}
                )
    generated_text = json_response[0]['generated_text']
    return generated_text
