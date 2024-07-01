from typing import Optional, List, Literal, Dict
from pydantic import BaseModel


class CozeMessage(BaseModel):
    role: Literal[
        "role",
        "assistant",
    ]
    type: Literal[
        "answer",
        "function_cal",
        "tool_response",
        "follow_up",
        "verbose",
    ]
    content: str
    content_type: Literal["text"]


class CozeRequest(BaseModel):
    bot_id: str
    conversation_id: Optional[str] = None
    user: str
    query: str
    chat_history: Optional[List[CozeMessage]] = None
    stream: bool = False
    custom_variables: Optional[Dict[str, str]] = None


class CozeCodeMsg(BaseModel):
    code: int
    msg: str


class CozeResponse(CozeCodeMsg):
    coversation_id: Optional[str] = None
    messages: Optional[List[CozeMessage]] = None
    content: Optional[str] = None


class CozeStreamingResponse(BaseModel):
    event: Literal["message", "done", "error"]
    message: Optional[CozeMessage] = None
    is_finish: Optional[bool] = None
    index: Optional[int] = None
    coversation_id: Optional[str] = None
    error_information: Optional[CozeCodeMsg] = None
    content: Optional[str] = None
