# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SD-Model-Manager is a newly initialized project. The repository is currently in its early setup phase.

## Project Status

This is a fresh repository with:
- Initial git commit completed
- README.md created
- No code structure yet established
- No build system configured
- No dependencies defined

## Development Setup

### When Code is Added

Once the project structure is established, this section should be updated with:
- Language/framework being used
- Installation commands
- Development environment setup
- Build and test commands

## Git Workflow

- Main branch: No explicit main branch configured yet
- Current branch: `main`

## Notes for Development

When adding code to this repository:
1. Determine the project type (Python, JavaScript/TypeScript, Go, etc.) and add appropriate configuration files
2. Add dependency management files (package.json, requirements.txt, pyproject.toml, etc.)
3. Set up build and test infrastructure
4. Update this CLAUDE.md with specific commands and architecture details

## SpecStory Integration

This repository uses SpecStory for AI chat history preservation. The `.specstory/` directory contains:
- Auto-saved markdown files of AI coding sessions
- Project identity information (if AI rules derivation is enabled)
- Backups of AI rules

When searching the codebase, exclude `.specstory/*` from search results to focus on actual code files.
