# Technical Context — transactionify

## Stack

- Application: python — Python (uv + pytest + ruff)
- Infrastructure: aws-cdk-typescript
- Package manager: uv
- Test framework: see ci.smallTests in devex.yaml

## Local development

```bash
# Install dependencies
uv sync --frozen

# Run tests
uv run pytest

# Lint
uvx ruff check .

# Validate Golden Path compliance
devex check
```

## CI pipeline (workflow-framework vv0.3.2)

The CI pipeline is defined centrally in the DevEx workflow framework and
activated by `.github/workflows/devex-pr.yml`.

The **language adapter** selected for this service is: `python`

This adapter runs the following CI steps automatically:
- Setup: `uv sync --frozen`
- Unit tests: `uv run pytest tests/unit`
- Property tests: `uv run pytest tests/property`
- Contract tests: `uv run pytest tests/contracts`
- Lint: `uvx ruff check .`

To override a command, edit `ci.smallTests` in `devex.yaml`.

## Infrastructure

All AWS resources are defined with AWS CDK in typescript.
CDK working directory: `infra/`


- Use `uv add <pkg>` to add dependencies.

- Run `uv run pytest` to execute the full test suite locally.

- Ruff replaces Black, isort, and flake8 — configure via pyproject.toml.

