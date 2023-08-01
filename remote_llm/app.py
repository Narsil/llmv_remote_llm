from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
from logging import getLogger
log = getLogger(__name__)

from remote_llm.huggingface import generate_huggingface

app = FastAPI()


class GenerateRequest(BaseModel):
    prompt: str
    preprompt: Optional[str] = None
    model: Optional[str] = None


class GenerateResponse(BaseModel):
    generation: str = ""
    error: Optional[str] = None 


models = {
    "huggingface": generate_huggingface
}



@app.get("/")
async def generate(request: GenerateRequest) -> GenerateResponse:
    if request.model is None:
        return GenerateResponse(generation="", error="No model specified")
    
    if request.model not in models:
        return GenerateResponse(generation="", error="Model not found")
    
    try:
        generation = await models[request.model](request.prompt, request.preprompt)
        return GenerateResponse(generation=generation)
    except Exception as e:
        log.exception(e)
        return GenerateResponse(generation="", error=str(e))
    

@app.get("/models")
async def get_models() -> list:
    return list(models.keys())


@app.get("/health")
async def health() -> str:
    return "OK"


