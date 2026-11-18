"""The `sidekick research` command."""

from __future__ import annotations

import asyncio
from typing import Annotated

import typer
from rich.console import Console
from rich.markdown import Markdown

from sidekick.agents.research import agent

out = Console()
err = Console(stderr=True)


def research(
    topic: Annotated[str, typer.Argument(help="What to research.")],
) -> None:
    """Research a topic on the web and show a report in Japanese."""
    try:
        with err.status("Researching...") as status:
            report = asyncio.run(agent.research(topic, on_step=status.update))
    except agent.AgentError as e:
        err.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    if out.is_terminal:
        out.print(Markdown(report))
    else:
        # Redirected to a file or a pipe: write the Markdown as it is.
        print(report)
