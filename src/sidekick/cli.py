"""Command line entry point: `sidekick <agent>`.

Each agent lives in its own folder under `sidekick/agents/` and is registered here.
"""

from __future__ import annotations

import typer

from sidekick.agents.commit.command import commit

app = typer.Typer(
    help="Personal AI agents built with the Claude Agent SDK.",
    no_args_is_help=True,
)


@app.callback()
def main() -> None:
    """Personal AI agents built with the Claude Agent SDK."""
    # Having a callback keeps `commit` a subcommand even while it is the only one.


app.command()(commit)
