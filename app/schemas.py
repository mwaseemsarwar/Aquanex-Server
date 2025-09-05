from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    selectedModel: Optional[str] = Field(default=None)

class ErrorResponse(BaseModel):
    error: str
