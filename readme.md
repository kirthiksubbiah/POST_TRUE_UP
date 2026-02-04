# POST TRUE UP

Validation framework for Jira Service Management migrations using Playwright and REST APIs.


---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Running Tests](#running-tests)
- [Logging](#logging)
- [Security Notes](#security-notes)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

This project is a Python-based application designed to:

- Automate validation tasks
- Interact with external systems via REST APIs
- Perform UI-based checks using Playwright
- Support migration or regression verification workflows

The application is intended for **internal / controlled environments**.

---

## Features

- UI automation using Playwright
- REST API validation using `requests`
- Pytest-based test execution
- Modular helper architecture
- Structured logging to file and console
- CLI-driven execution support

---

## Project Structure
Commit Message & Branch Naming Rules
✅ Commit Message Format
All commit messages must match one of the following patterns:
Allowed types
build | ci | docs | feat | fix | perf | refactor | style | test | chore | revert | merge
Format
<type>(optional-scope): short description
Valid examples
feat(auth): add login validationfix: resolve crash on startupdocs(readme): update setup stepschore: update dependenciesmerge: branch develop into mainNotes added by release scriptProject initial commit
❌ Invalid examples
added new featurebug fixFEAT: something
🌿 Branch Naming Convention
Branch names must follow one of these patterns:
Standard branches
feature/<name>-<number>hotfix/<name>-<number>uat/<name>-<number>pilot/<name>-<number>
OR using hyphens
feature-<name>-<number>hotfix-<name>-<number>uat-<name>-<number>pilot-<name>-<number>
Special allowed branches
livetraintmo/main
Valid examples
feature-login-123hotfix/payment-45uat-search-9pilot/onboarding-101live
❌ Invalid examples
feature_loginbugfix-123maindev-feature-1
