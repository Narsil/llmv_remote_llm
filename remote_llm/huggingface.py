import os
from typing import Optional
from fastapi import HTTPException
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
import aiohttp
from logging import getLogger
log = getLogger(__name__)

async def generate_huggingface(prompt: str, preprompt: Optional[str] = None) -> str:
    huggingface_key = os.environ.get("HUGGINGFACE_API_KEY")
    if huggingface_key is None:
        raise ValueError("HUGGINGFACE_API_KEY not set")
    huggingface_url = os.environ.get("HUGGINGFACE_API_URL")
    if huggingface_url is None:
        raise ValueError("HUGGINGFACE_API_KEY not set")
    
    parameters = {
        "max_new_tokens": 1024,
        "repetition_penalty": 1.2,
        "return_full_text": False,
        "top_p": 0.95,
        "temperature": 0.9,
        "stop": ["<|endoftext|>"]
    }
    prompt_format = "<|system|>{preprompt}<|prompter|>{prompt}<|endoftext|><|assistant|>"

    full_prompt = prompt_format.replace("{preprompt}", preprompt).replace("{prompt}", prompt)

    
    async with aiohttp.ClientSession() as session:
        async with session.post(url=huggingface_url,
                        headers={'Authorization': f'Bearer {huggingface_key}'},
                        json={'inputs': full_prompt, "parameters" : parameters, "stream:": False}) as raw_response:
            json_response = await raw_response.json()
            if 'error' in json_response:
                log.error(f"Error generating: {json_response['error']}")
                raise HTTPException(
                    HTTP_429_TOO_MANY_REQUESTS, "Too Many Requests", headers={"Retry-After": str(1000)}
                )
    generated_text = json_response[0]['generated_text']
    return generated_text