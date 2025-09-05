import asyncio
from typing import AsyncIterator, List
import structlog
from langchain_openai import ChatOpenAI
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from tenacity import retry, stop_after_attempt, wait_exponential
from .config import settings
from .utils import FALLBACK_TEXT

logger = structlog.get_logger()

def _lc_messages(messages: List[dict]):
    lc_msgs = []
    for m in messages:
        role = m["role"].lower()
        if role == "system":
            lc_msgs.append(SystemMessage(content=m["content"]))
        elif role == "user":
            lc_msgs.append(HumanMessage(content=m["content"]))
        elif role == "assistant":
            lc_msgs.append(AIMessage(content=m["content"]))
    return lc_msgs

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
async def stream_openai(messages: List[dict], model: str | None) -> AsyncIterator[str]:
    llm = ChatOpenAI(
        model=model or settings.OPENAI_MODEL,
        streaming=True,
        temperature=0.3,
        api_key=settings.OPENAI_API_KEY,
    )
    queue: asyncio.Queue[str] = asyncio.Queue()
    done = asyncio.Event()

    class Handler(BaseCallbackHandler):
        """Custom callback handler for streaming tokens."""
        
        async def on_llm_new_token(self, token: str, **kwargs):
            await queue.put(token)

        async def on_llm_end(self, *args, **kwargs):
            done.set()

        async def on_llm_error(self, error, **kwargs):
            logger.error("llm_error", error=str(error))
            done.set()

    handler = Handler()

    async def run_call():
        try:
            await llm.ainvoke(_lc_messages(messages), config={"callbacks": [handler]})
        except Exception as e:
            logger.exception("llm_invoke_failed", error=str(e))
            done.set()

    task = asyncio.create_task(run_call())
    while True:
        try:
            token = await asyncio.wait_for(queue.get(), timeout=0.1)
            yield token
        except asyncio.TimeoutError:
            if done.is_set():
                break
    await task

async def stream_fallback() -> AsyncIterator[str]:
    for word in FALLBACK_TEXT.split():
        yield word + " "
        await asyncio.sleep(0.015)
