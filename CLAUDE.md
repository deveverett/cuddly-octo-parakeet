# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

A mixed repository containing two distinct things:

1. **AL extension for Dynamics 365 Business Central** — the original purpose of the repo. The AL code targets BC platform/application version 23.0.0.0 and uses object ID range 50100–50149.
2. **Python computer-use demos** — Anthropic API scripts added during Claude Code sessions (`computer_use_demo.py`, `sampling_loop.py`).

## AL Development

AL is compiled and deployed via the **AL Language extension for VS Code** — there is no standalone CLI build tool. The standard workflow is:

- **Build/publish:** `Ctrl+Shift+P` → `AL: Publish` (requires a configured `launch.json` pointing at a BC sandbox or Docker container)
- **Download symbols:** `Ctrl+Shift+P` → `AL: Download Symbols` (populates `.alpackages/`)
- **Run tests:** BC test runner codeunits are executed from within the BC client or via the `BCContainerHelper` PowerShell module

Gitignored artifacts: `.alcache/`, `.alpackages/`, `.output/`, `*.app`, `rad.json`, `*.g.xlf`, `*.flf`, `TestResults.xml`.

## Python Scripts

Both scripts require `pip install anthropic`. `computer_use_demo.py` additionally requires `pip install pyautogui pillow`.

- **`computer_use_demo.py`** — self-contained computer-use agent. Run directly: `python computer_use_demo.py`. Requires `ANTHROPIC_API_KEY` in the environment.
- **`sampling_loop.py`** — reusable `sampling_loop()` function; import it into your own script. Pass `tool_version` as a date suffix (e.g. `"20251124"`) — the function resolves the correct beta flag and tool names automatically.
