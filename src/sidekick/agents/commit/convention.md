# Commit message convention

Follow Conventional Commits 1.0.0. For a small change, the header line alone is enough.

```text
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

## Header

- Write the description in English, in the imperative mood, starting with a lowercase letter
  (`add`, not `Added` or `adds`).
- Say what the commit does in one line of about 50 characters or less.
- Do not end the description with a period.
- Put `!` after the type (or scope) for a breaking change.

## Body

- Optional. Write it in English, as normal sentences (capitalized, ending with a period).
- Explain why the change was made. What changed is visible in the diff.
- Leave it out when the header already says everything.

## Footers

- A breaking change gets `BREAKING CHANGE: <what breaks and how to migrate>`.
- An issue is referenced with `Refs: #<number>`.
- To reference an issue only, the header and `Refs:` are enough; no body is needed.
- Pull request numbers are added automatically by GitHub on Squash and merge, so never write them.

## One change per commit

A commit holds one change. If the changes need two different types, they should be split into
separate commits.

## Types

Choose one of these eight. When unsure, ask "does the behavior change for the user?"
If yes, it is `feat` or `fix`.

| type     | when to use                                 |
| -------- | ------------------------------------------- |
| feat     | a new feature                               |
| fix      | a bug fix                                   |
| refactor | code restructuring that keeps the behavior  |
| perf     | a performance improvement                   |
| docs     | documentation only                          |
| style    | formatting and other changes with no effect |
| test     | adding or fixing tests                      |
| chore    | dependencies, settings, build, CI           |

## Scopes

A scope is optional. Use one only when the repository's recent history already uses it, and spell it
exactly the same way.

## Examples

```text
feat(auth): add password reset
```

```text
fix(cart): include shipping fee in cart total

The input value was not converted to a number.

Refs: #42
```

```text
docs: add setup steps to README

Refs: #43
```
