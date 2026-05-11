# Golden Path Standards — transactionify

This file provides Amazon Q Developer with context about the LoanPro Golden
Path conventions that apply to this repository.

## Work ID convention

Every branch, commit message, and PR title must include a Work ID.

- Branch pattern: `^(feature|fix|chore|hotfix)/[A-Z]+-[0-9]+-[a-z0-9-]+$`
- Commit pattern: `^\[[A-Z]+-[0-9]+\] .+`
- PR title pattern: `^\[[A-Z]+-[0-9]+\] .+`

Example: `feature/FIN-123-add-validation` / `[FIN-123] Add validation`

## Language and tooling

- Application language: **python** (Python (uv + pytest + ruff))
- Infrastructure framework: **aws-cdk-typescript**
- Test command: `uv run pytest`
- Lint command: `uvx ruff check .`

## CI pipeline

This repository calls the centralized DevEx reusable workflow at
`@v0.3.2`. The pipeline runs:

1. Governance (Work ID, PR template, reviewer count)
2. Small Tests (unit, property, contract, lint)
3. CDK synth
4. Sequential deployment: sandbox → staging → production
5. DORA and audit telemetry

Do not duplicate pipeline logic here. Customise via `devex.yaml`.

## Forbidden patterns

- Do not hardcode AWS account IDs or credentials.
- Do not merge without two approving reviews.
- Do not push directly to `main`.
- Do not modify `.github/workflows/devex-pr.yml` — use `devex upgrade` instead.
