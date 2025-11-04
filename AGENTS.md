# Repository Guidelines
@CLAUDE.md
## Project Structure & Module Organization
Place all runtime code under `src/sd_model_manager/`, grouping features by domain (`registry/`, `sync/`, `ui/`), and expose the CLI entry point through `src/sd_model_manager/__main__.py`. Keep shared utilities in `src/sd_model_manager/lib/` to avoid circular imports. Store automated tests in `tests/` with mirrors of the package layout, and put sample checkpoints or UI assets that are safe for version control in `assets/`. Use `docs/` for architecture notes and onboarding guides; remove any large binary weights before committing.

## Build, Test, and Development Commands
- `python -m venv .venv && source .venv/bin/activate`: create and activate the local environment.
- `python -m pip install -r requirements-dev.txt`: install runtime and toolchain dependencies.
- `python -m pip install -e .`: develop against the editable package during feature work.
- `pytest`: run the full automated test suite.
- `ruff check src tests` and `black src tests`: lint and format prior to a pull request.

## Coding Style & Naming Conventions
Target Python 3.11+, follow PEP 8, and default to four-space indentation. Package and module names stay lowercase with underscores (`sd_model_manager/registry_sync.py`), classes use CapWords, and functions plus variables remain snake_case. Prefer type hints and keep public functions documented with Google-style docstrings. Configuration constants live in `src/sd_model_manager/config.py`, while module-level logging uses the `sd_model_manager` logger namespace.

## Testing Guidelines
Write tests with `pytest`, naming files `test_<feature>.py` and fixtures `_fixture` to clarify scope. Add unit coverage for new logic, plus lightweight integration tests for CLI commands under `tests/cli/`. Aim for ≥85% line coverage; verify locally with `pytest --cov=sd_model_manager --cov-report=term-missing`. When mocking external services, save reusable fakes in `tests/helpers/`.

## Commit & Pull Request Guidelines
Use concise, imperative present-tense commit messages; the initial `first commit` sets the tone. Rebase before opening a pull request, squash noisy fixups, and ensure each PR describes the change, impact, and manual validation steps. Link relevant issues, attach screenshots for UI-oriented changes, and note any model files that must be fetched manually in the release notes.

## Security & Configuration Tips
Never commit API keys or proprietary checkpoints; reference them through `.env` entries documented in `docs/configuration.md`. Validate any download scripts against checksums and sign releases when distributing bundled models. Review dependencies for licenses compatible with model redistribution before adding them to `requirements-dev.txt`.

## Agent Interaction Rules
- During code review requests, do not apply repository changes unless the user explicitly asks for modifications.
