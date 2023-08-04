from typing import Optional, List
from fastapi import FastAPI
from pydantic import BaseModel
from starlette.status import HTTP_404_NOT_FOUND, HTTP_422_UNPROCESSABLE_ENTITY
from logging import getLogger
log = getLogger("generator")

from remote_llm.huggingface import generate_huggingface
from remote_llm.stability import generate_stability
from remote_llm.openai import generate_openai

app = FastAPI()


class GenerateRequest(BaseModel):
    prompt: str
    preprompt: Optional[str] = None
    model: str


class GenerateResponse(BaseModel):
    generation: str = ""
    error: Optional[str] = None 


models = {
    "huggingface": generate_huggingface,
    "stability": generate_stability,
    "openai": generate_openai,
}


@app.get("/generate")
async def generate(request: GenerateRequest) -> GenerateResponse:
    if request.model not in models:
        return HTTP_404_NOT_FOUND("Model not found")
    
    try:
        generation = await models[request.model](request.prompt, request.preprompt)
        return GenerateResponse(generation=generation)
    except Exception as e:
        log.exception(e)
        return GenerateResponse(generation="", error=str(e))
    

@app.get("/models")
async def get_models() -> List[str]:
    return list(models.keys())


@app.get("/health")
async def health() -> str:
    return "OK"


