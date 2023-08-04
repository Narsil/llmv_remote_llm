import os

HF_KEY = os.environ.get("HUGGINGFACE_API_KEY")
if HF_KEY is None:
    raise ValueError("HUGGINGFACE_API_KEY not set")
HF_URL = os.getenv("HUGGINGFACE_API_URL")

