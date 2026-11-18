"""Research a topic on the web and write a report in Japanese.

The agent can only search the web and read web pages: it cannot touch files or run commands.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import date
from importlib.resources import files

from claude_agent_sdk import AssistantMessage, ClaudeAgentOptions, ResultMessage, query

WEB_TOOLS = ["WebSearch", "WebFetch"]


class AgentError(RuntimeError):
    """The agent did not return a report."""


def load_prompt() -> str:
    text = files(__package__).joinpath("prompt.md").read_text(encoding="utf-8")
    return text.replace("{today}", date.today().isoformat())


def describe_step(name: str, tool_input: dict) -> str | None:
    """Turn a tool call into a short line for the progress display."""
    if name == "WebSearch":
        return f"Searching: {tool_input.get('query', '')}"
    if name == "WebFetch":
        return f"Reading: {tool_input.get('url', '')}"
    return None


async def research(topic: str, on_step: Callable[[str], None] | None = None) -> str:
    options = ClaudeAgentOptions(
        system_prompt=load_prompt(),
        tools=WEB_TOOLS,
        allowed_tools=WEB_TOOLS,
        permission_mode="dontAsk",
        setting_sources=[],
    )

    result: ResultMessage | None = None
    async for message in query(prompt=f"Topic: {topic}", options=options):
        if isinstance(message, AssistantMessage) and on_step:
            for block in message.content:
                step = describe_step(getattr(block, "name", ""), getattr(block, "input", None) or {})
                if step:
                    on_step(step)
        elif isinstance(message, ResultMessage):
            result = message

    if result is None or result.is_error or not result.result:
        reason = result.result if result and result.result else "no report was returned"
        raise AgentError(f"The research failed: {reason}")
    return result.result
