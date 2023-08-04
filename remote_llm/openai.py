import os
from typing import Optional
from fastapi import HTTPException
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
import aiohttp
from logging import getLogger
log = getLogger("generator")

async def generate_openai(prompt: str, preprompt: Optional[str] = None) -> str:
    huggingface_key = os.environ.get("HUGGINGFACE_API_KEY")
    if huggingface_key is None:
        raise ValueError("HUGGINGFACE_API_KEY not set")

    url = os.environ.get("OPENAI_API_URL")
    if url is None:
        raise ValueError("OPENAI_API_URL not set")
    

    payload =  {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Say this is a test!"}],
        "temperature": 0.7
     }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url=url,
                        headers={'Authorization': f'Bearer {huggingface_key}'},
                        json=payload) as raw_response:
            json_response = await raw_response.json()
            if 'error' in json_response:
                log.error(f"Error generating: {json_response['error']}")
                raise HTTPException(
                    HTTP_429_TOO_MANY_REQUESTS, "Too Many Requests", headers={"Retry-After": str(1000)}
                )
    generated_text = json_response[0]['generated_text']
    return generated_text
