"""Draft a Conventional Commits message for the staged changes.

The agent only reads: it gets the staged diff from us and may open files in the
repository for context, but it cannot edit files, run commands or commit.
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from importlib.resources import files
from pathlib import Path

from claude_agent_sdk import ClaudeAgentOptions, ResultMessage, query

TYPES = ["feat", "fix", "refactor", "perf", "docs", "style", "test", "chore"]
READ_ONLY_TOOLS = ["Read", "Grep", "Glob"]
MAX_DIFF_CHARS = 60_000
RECENT_LOG_COUNT = 15
# Branch names follow "type/123-short-name" when they belong to an issue.
BRANCH_ISSUE = re.compile(r"^[a-z]+/(\d+)-")

SCHEMA = {
    "type": "object",
    "properties": {
        "type": {"type": "string", "enum": TYPES},
        "scope": {
            "type": "string",
            "description": "Scope without parentheses, or an empty string for none.",
        },
        "breaking": {"type": "boolean"},
        "description": {
            "type": "string",
            "description": "Imperative, lowercase start, no trailing period, about 50 characters.",
        },
        "body": {
            "type": "string",
            "description": "Why the change was made, in English sentences, or an empty string.",
        },
        "breaking_change": {
            "type": "string",
            "description": "Text for the BREAKING CHANGE footer, or an empty string.",
        },
        "translation": {
            "type": "string",
            "description": (
                "A Japanese translation of the description and the body, for the user to read. "
                "Keep the type and scope as they are. Do not translate footers."
            ),
        },
        "split_advice": {
            "type": "string",
            "description": (
                "If the staged changes mix more than one purpose, explain in Japanese how to "
                "split them into separate commits. Otherwise an empty string."
            ),
        },
    },
    "required": [
        "type",
        "scope",
        "breaking",
        "description",
        "body",
        "breaking_change",
        "translation",
        "split_advice",
    ],
    "additionalProperties": False,
}

SYSTEM_PROMPT = """\
You write git commit messages for the staged changes of a repository.
Follow the convention below exactly. You may open files in the repository with your tools
when the diff alone does not show why a change was made, but keep it brief.
Do not write Refs or pull request footers; the caller adds them.

<convention>
{convention}
</convention>
"""


class GitError(RuntimeError):
    """A git command failed."""


class NothingStagedError(RuntimeError):
    """There are no staged changes to describe."""


class AgentError(RuntimeError):
    """The agent did not return a usable message."""


@dataclass
class CommitMessage:
    type: str
    description: str
    scope: str = ""
    breaking: bool = False
    body: str = ""
    footers: list[str] = field(default_factory=list)

    def format(self) -> str:
        header = self.type
        if self.scope:
            header += f"({self.scope})"
        if self.breaking:
            header += "!"
        header += f": {self.description}"

        parts = [header]
        if self.body:
            parts.append(self.body.strip())
        if self.footers:
            parts.append("\n".join(self.footers))
        return "\n\n".join(parts)


@dataclass
class Draft:
    message: CommitMessage
    translation: str = ""
    split_advice: str = ""


def git(*args: str, cwd: Path | None = None) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        raise GitError(proc.stderr.strip() or f"git {' '.join(args)} failed")
    return proc.stdout


def load_convention() -> str:
    return files(__package__).joinpath("convention.md").read_text(encoding="utf-8")


def issue_from_branch(branch: str) -> int | None:
    match = BRANCH_ISSUE.match(branch)
    return int(match.group(1)) if match else None


def build_prompt(*, status: str, log: str, diff: str) -> str:
    if len(diff) > MAX_DIFF_CHARS:
        diff = (
            diff[:MAX_DIFF_CHARS]
            + "\n\n[The diff was cut here. Open the changed files if you need the rest.]"
        )
    return (
        "Write the commit message for these staged changes.\n\n"
        f"## Staged files\n{status or '(none)'}\n\n"
        f"## Recent commits (match their scopes and wording)\n{log or '(no commits yet)'}\n\n"
        f"## Staged diff\n{diff}"
    )


async def ask_agent(prompt: str, repo: Path) -> ResultMessage:
    options = ClaudeAgentOptions(
        system_prompt=SYSTEM_PROMPT.format(convention=load_convention()),
        tools=READ_ONLY_TOOLS,
        allowed_tools=READ_ONLY_TOOLS,
        permission_mode="dontAsk",
        setting_sources=[],
        cwd=repo,
        max_turns=10,
        output_format={"type": "json_schema", "schema": SCHEMA},
    )
    result: ResultMessage | None = None
    async for message in query(prompt=prompt, options=options):
        if isinstance(message, ResultMessage):
            result = message
    if result is None:
        raise AgentError("The agent ended without a result.")
    return result


async def draft(refs: list[int] | None = None) -> Draft:
    repo = Path(git("rev-parse", "--show-toplevel").strip())
    diff = git("diff", "--staged", cwd=repo)
    if not diff.strip():
        raise NothingStagedError("No staged changes. Run `git add` first.")

    status = git("diff", "--staged", "--name-status", cwd=repo).strip()
    try:
        log = git("log", f"-{RECENT_LOG_COUNT}", "--format=%s", cwd=repo).strip()
    except GitError:  # a repository without commits yet
        log = ""

    if not refs:
        branch = git("branch", "--show-current", cwd=repo).strip()
        issue = issue_from_branch(branch)
        refs = [issue] if issue else []

    result = await ask_agent(build_prompt(status=status, log=log, diff=diff), repo)
    data = result.structured_output
    if result.is_error or not isinstance(data, dict):
        raise AgentError(result.result or f"The agent stopped with '{result.subtype}'.")

    footers = []
    if data["breaking"] and data["breaking_change"].strip():
        footers.append(f"BREAKING CHANGE: {data['breaking_change'].strip()}")
    footers += [f"Refs: #{n}" for n in refs]

    message = CommitMessage(
        type=data["type"],
        scope=data["scope"].strip(),
        breaking=data["breaking"],
        description=data["description"].strip().rstrip("."),
        body=data["body"].strip(),
        footers=footers,
    )
    return Draft(
        message=message,
        translation=data["translation"].strip(),
        split_advice=data["split_advice"].strip(),
    )
