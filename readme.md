# POST TRUE UP

Validation framework for Jira Service Management migrations using Playwright and REST APIs

---

## Table of Contents

- Overview
- Features
- Project Structure
- Commit Message Rules
- Branch Naming Convention
- Prerequisites
- Installation
- Configuration
- Usage
- Running Tests
- Logging
- Security Notes
- Troubleshooting
- Contributing
- License

---

## Overview

This project is a Python-based validation framework designed for Jira Service Management (JSM) migration and post-migration true-up validation.

It supports:
- Migration validation
- Regression verification
- API and UI consistency checks

This framework is intended for internal and controlled environments only.

---

## Features

- UI automation using Playwright
- REST API validation using requests
- Pytest-based execution
- Modular helper architecture
- Structured logging (file and console)
- CLI-driven execution
- Designed for migration and post-true-up workflows

---

## Project Structure

project-root/
├── config/          # Environment and authentication configuration
├── helpers/         # Shared utilities and helpers
├── tests/           # Pytest test cases
├── logs/            # Execution logs
├── reports/         # Test reports (optional)
├── requirements.txt
└── README.md

---

## Commit Message & Branch Naming Rules

### Commit Message Format

All commit messages must match one of the following patterns:


### Allowed Types

build | ci | docs | feat | fix | perf | refactor | style | test | chore | revert | merge

### Format

<type>(optional-scope): short description

### Valid Examples

feat(auth): add login validationfix: resolve crash on startupdocs(readme): update setup stepschore: update dependenciesmerge: branch develop into mainNotes added by release scriptProject initial commit

### Invalid Examples

added new featurebug fixFEAT: something

---

## 🌿 Branch Naming Convention

Branch names must follow one of these patterns:

### Standard Branches

feature/<name>-<number>hotfix/<name>-<number>uat/<name>-<number>pilot/<name>-<number>


OR using hyphens:

feature-<name>-<number>hotfix-<name>-<number>uat-<name>-<number>pilot-<name>-<number>

### Special Allowed Branches

livetraintmo/main

### Valid Examples

feature-login-123hotfix/payment-45uat-search-9pilot/onboarding-101live

### ❌ Invalid Examples

feature_login  
bugfix-123  
main  
dev-feature-1

---

## Prerequisites

- Python 3.10 or higher
- Node.js (required for Playwright)
- Jira Service Management access (API and UI)
- Git

---

## Installation

git clone <repository-url>  
cd <project-root>  
pip install -r requirements.txt  
playwright install

---

## Configuration

- Configure environment values in the config directory
- Store API tokens securely
- Do not commit secrets to source control

---

## Usage

The framework supports:
- API-only validations
- UI-only validations
- Combined UI + API migration checks

Execution is driven via Pytest.

---

## Running Tests

pytest -v

Optional flags:

pytest -s  
pytest -k <keyword>

---

## Logging

- Logs are written to console and files
- Log files are stored in the logs directory
- Logs are structured for debugging and audit review

---

## Security Notes

- Internal use only
- Never commit credentials or tokens
- Rotate API tokens regularly
- Follow organizational security policies

---

## Troubleshooting

- Playwright browser missing: run playwright install
- Authentication failures: verify tokens and permissions
- Migration mismatches: validate source vs target data

---

## Contributing

- Follow commit and branch naming rules strictly
- Add tests for all new validations
- Keep helpers reusable
- Ensure tests pass before submitting PRs

---

## License

Internal use only. Refer to organizational licensing policies.
