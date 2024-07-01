import os
import asyncio
import json
import httpx

from typing import Dict
from fire import Fire
from coze.types import CozeRequest, CozeResponse, CozeStreamingResponse


class AsyncStream(object):
    def __init__(self, url: str, data: Dict, headers: Dict):
        self.url = url
        self.data = data
        self.headers = headers

    async def __aiter__(self):
        content = ""
        async with httpx.AsyncClient(timeout=600) as client:
            async with client.stream(
                "POST", self.url, json=self.data, headers=self.headers
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data:"):
                        event_data = line[len("data:") :]
                        data = json.loads(event_data)
                        stream = CozeStreamingResponse.model_validate(data)
                        if (
                            stream.event == "message"
                            and stream.message.type == "answer"
                        ):
                            content += data["message"]["content"]

                        stream.content = content

                        yield stream

    async def __anext__(self):
        pass


async def achat(request: CozeRequest):
    url = "https://api.coze.com/open_api/v2/chat"
    data = request.model_dump()
    api_key = os.getenv("COZE_API_KEY", None)
    if api_key is None:
        raise ValueError("COZE_API_KEY environment variable not set")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "*/*",
        "Connection": "keep-alive",
    }

    if not request.stream:
        async with httpx.AsyncClient(timeout=600) as client:
            response = await client.post(url, json=data, headers=headers)
            response.raise_for_status()

            result = CozeResponse.model_validate(response.json())
            if len(result.messages) > 0:
                message = result.messages[0]
                if message.type == "answer":
                    result.content = message.content

            return result

    return AsyncStream(url, data, headers)


async def test_achat(request: CozeRequest):
    response = await achat(request)
    if request.stream:
        async for stream in response:
            if stream.message is not None:
                if stream.message.type == "answer":
                    print(stream.message.content, end="", flush=True)
    else:
        print(response.content)


def test_chat(bot_id: str, query: str, user: str = "coze", stream: bool = True):
    request = CozeRequest.model_validate(
        {
            "bot_id": str(bot_id),
            "query": query,
            "user": user,
            "stream": stream,
        }
    )

    asyncio.run(test_achat(request))


if __name__ == "__main__":
    Fire(
        {
            "chat": test_chat,
        }
    )
