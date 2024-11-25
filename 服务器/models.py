from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    问题: str
    接口: Optional[str] = None

class TestRequest(BaseModel):
    问题: Optional[str] = '你好' 