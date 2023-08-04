import os
from typing import Optional
from fastapi import HTTPException
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
import aiohttp
from logging import getLogger
log = getLogger("generator")

async def generate_stability(prompt: str, preprompt: Optional[str] = None) -> str:
    stability_key = os.environ.get("HUGGINGFACE_API_KEY")
    if stability_key is None:
        raise ValueError("HUGGINGFACE_API_KEY not set")
    url = os.environ.get("STABILITY_API_URL")
    if url is None:
        raise ValueError("STABILITY_API_URL not set")
    
    parameters = {
        "max_new_tokens": 512,
        "temperature": 0.5,
        "top_p": 0.95
    }
    full_prompt = prompt
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url=url,
                        headers={'Authorization': f'Bearer {stability_key}'},
                        json={'inputs': full_prompt, "parameters" : parameters}) as raw_response:
            json_response = await raw_response.json()
            if 'error' in json_response:
                log.error(f"Error generating: {json_response['error']}")
                raise HTTPException(
                    HTTP_429_TOO_MANY_REQUESTS, "Too Many Requests", headers={"Retry-After": str(1000)}
                )
    generated_text = json_response[0]['generated_text']
    return generated_text