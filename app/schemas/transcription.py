from pydantic import BaseModel
from typing import Dict

class TranscriptionResponse(BaseModel):
    original_text: str
    structured: Dict[str, str]