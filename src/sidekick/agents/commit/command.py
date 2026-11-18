"""The `sidekick commit` command."""

from __future__ import annotations

import asyncio
from typing import Annotated

import pyperclip
import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from sidekick.agents.commit import agent

out = Console()
err = Console(stderr=True)


def commit(
    ref: Annotated[
        list[int] | None,
        typer.Option("--ref", "-r", help="Issue number for a Refs footer. Repeatable."),
    ] = None,
) -> None:
    """Draft a commit message for the staged changes."""
    try:
        with err.status("Reading the staged changes..."):
            draft = asyncio.run(agent.draft(refs=ref))
    except agent.NothingStagedError as e:
        err.print(f"[yellow]{e}[/yellow]")
        raise typer.Exit(1)
    except (agent.GitError, agent.AgentError) as e:
        err.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    text = draft.message.format()
    out.print(Panel(Text(text), title="commit message", expand=False))

    if draft.translation:
        err.print(Panel(Text(draft.translation), title="日本語訳", expand=False, border_style="dim"))

    if draft.split_advice:
        err.print(Panel(Text(draft.split_advice), title="分けたほうがよさそうです", border_style="yellow"))

    try:
        pyperclip.copy(text)
        err.print("[green]Copied to the clipboard.[/green]")
    except pyperclip.PyperclipException as e:
        err.print(f"[yellow]Could not copy to the clipboard:[/yellow] {e}")
