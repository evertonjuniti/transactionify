# Product Context — transactionify

## Service identity

- Name: transactionify
- Owner: ogurateam
- Type: microservice
- Language: python (Python (uv + pytest + ruff))
- Infrastructure: aws-cdk-typescript

## Purpose

transactionify is a microservice owned by the ogurateam team. It follows
the LoanPro Golden Path: the application logic is written in python
and the infrastructure is managed with aws-cdk-typescript.

## Deployment environments

| Environment | CDK Stack |
|-------------|-----------|
| sandbox | TransactionifySandbox |
| staging | TransactionifyStaging |
| production | TransactionifyProduction |

## Work tracking

Work IDs follow the pattern `^[A-Z]+-[0-9]+$` (e.g. FIN-123).
Every branch, commit, and PR title must reference a valid Work ID.
