# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a minimal **AL (Application Language)** extension for **Microsoft Dynamics 365 Business Central** (GHE). It extends the Customer List page to display a "Hello" message on open.

## Project Structure

- `HelloWorld.al` — Single AL file; a `pageextension` on the built-in "Customer List" page
- `app.json` — Extension manifest: publisher `deveverett`, platform/application `23.0.0.0`, object ID range `50100–50149`

## Development

AL development requires the **AL Language extension** for VS Code and a Business Central sandbox or Docker container. There are no npm/build scripts in this repo — compilation and deployment are handled by the AL extension or `al build` CLI.

Object IDs for new objects must fall within the declared range: **50100–50149**.
