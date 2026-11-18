# sidekick

Personal AI agents built with the [Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview).
Each agent is a subcommand of one CLI, `sidekick`.

## Agents

| Command | What it does |
| --- | --- |
| `sidekick commit` | Drafts a Conventional Commits message for the staged changes, shows a Japanese translation, and copies the message to the clipboard |

## Requirements

- Python 3.12 or later
- [uv](https://docs.astral.sh/uv/)
- Git
- Claude Code signed in with a Claude plan (run `claude`, then `/login`), or an `ANTHROPIC_API_KEY` environment variable

## Installation

```bash
git clone https://github.com/mniyk/sidekick.git
cd sidekick
uv tool install -e .
```

`uv tool install` puts the `sidekick` command on your PATH, so it works in any directory.
With `-e` (editable), it runs the code in this folder, so edits to the source take effect right away.

If the shell cannot find `sidekick`, run `uv tool update-shell` and open a new terminal.

After adding a dependency or changing `[project.scripts]` in `pyproject.toml`, reinstall:

```bash
uv tool install -e . --reinstall
```

To remove it:

```bash
uv tool uninstall sidekick
```

## Usage

### `sidekick commit`

Run it inside any Git repository after staging your changes.

```bash
git add .
sidekick commit
```

- The agent reads the staged diff and can open files in the repository, but it cannot edit files or commit.
- The message follows [the commit convention](src/sidekick/agents/commit/convention.md).
- If the branch name looks like `fix/42-cart-total`, `Refs: #42` is added. Use `-r 42` to set issue numbers yourself.
- If the staged changes mix more than one purpose, it suggests how to split them.

Paste the copied message with `git commit`.

## Project structure

One folder per agent, holding everything that agent needs.

```
src/sidekick/
├── cli.py              # registers each agent's command
└── agents/
    └── commit/
        ├── agent.py        # calls Claude through the Agent SDK
        ├── command.py      # the `sidekick commit` command
        └── convention.md   # the commit convention given to Claude
```

To add an agent, create a folder under `agents/` and register its command in `cli.py`.

## Development

Set up the development environment (creates `.venv` for your editor):

```bash
uv sync
```

Run from the project folder without installing:

```bash
uv run sidekick --help
```

## License

[MIT](LICENSE)
