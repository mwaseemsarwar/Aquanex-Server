import asyncio
from typing import AsyncIterator, List
import structlog
from langchain_openai import ChatOpenAI
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from tenacity import retry, stop_after_attempt, wait_exponential
from openai import RateLimitError, AuthenticationError
from .config import settings
from .utils import FALLBACK_TEXT

logger = structlog.get_logger()


# ---------------------------------------------------
# Helpers
# ---------------------------------------------------
def _lc_messages(messages: List[dict]):
    """Convert plain dict messages into LangChain message objects."""
    lc_msgs = []
    for m in messages:
        role = m["role"].lower()
        if role == "system":
            lc_msgs.append(SystemMessage(content=m["content"]))
        elif role == "user":
            lc_msgs.append(HumanMessage(content=m["content"]))
        elif role == "assistant":
            lc_msgs.append(AIMessage(content=m["content"]))
        else:
            raise ValueError(f"Unsupported role: {role}")
    return lc_msgs


# ---------------------------------------------------
# Streaming from OpenAI
# ---------------------------------------------------
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
async def stream_openai(messages: List[dict], model: str | None) -> AsyncIterator[str]:
    """
    Stream tokens from OpenAI LLM with retries and error handling.
    """
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

    # inside stream_openai

    async def run_call():
        try:
            await llm.ainvoke(_lc_messages(messages), config={"callbacks": [handler]})
        except RateLimitError:
            logger.error("openai_rate_limit", error="429 Too Many Requests / quota exceeded")
            # Instead of raising, push a marker to queue
            await queue.put("⚠️ OpenAI quota exceeded. Switching to fallback...\n")
            done.set()
        except AuthenticationError:
            logger.error("openai_auth_error", error="Invalid or missing API key")
            await queue.put("⚠️ Invalid OpenAI API key. Please check server configuration.\n")
            done.set()
        except Exception as e:
            logger.exception("llm_invoke_failed", error=str(e))
            await queue.put("⚠️ Unexpected error with LLM backend. Using fallback...\n")
            done.set()

    task = asyncio.create_task(run_call())

    try:
        while True:
            try:
                token = await asyncio.wait_for(queue.get(), timeout=0.2)
                yield token
            except asyncio.TimeoutError:
                if done.is_set():
                    break
    finally:
        await task
        # If OpenAI failed, fallback to local model
        if queue.empty() and not done.is_set():
            async for word in stream_fallback():
                yield word


# ---------------------------------------------------
# Local fallback streamer
# ---------------------------------------------------
async def stream_fallback() -> AsyncIterator[str]:
    """Yield words from fallback text with small delay."""
    for word in FALLBACK_TEXT.split():
        yield word + " "
        await asyncio.sleep(0.015)
