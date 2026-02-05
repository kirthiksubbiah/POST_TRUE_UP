# POST TRUE UP

## Steps to Create a Jira API Token

### 1. Generate a JSM API token (Atlassian → Account → Security → API tokens).
### 2. Store JSM token in GitLab CI variables
### 3. Create/Update Kubernetes Secret from GitLab CI vars
### 4. App reads env vars from Secret
### 5. Python uses env vars for JSM API authentication

---

## Commit Message & Branch Naming Rules

### ✅ Commit Message Format

All commit messages must match one of the following patterns:


### Allowed Types

build | ci | docs | feat | fix | perf | refactor | style | test | chore | revert | merge

### Format

<type>(optional-scope): short description

### Valid Examples

feat(auth): add login validationfix: resolve crash on startupdocs(readme): update setup stepschore: update dependenciesmerge: branch develop into mainNotes added by release scriptProject initial commit

### ❌ Invalid Examples

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

feature_loginbugfix-123maindev-feature-1


---


