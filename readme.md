# POST TRUE UP

## Steps to Create a Jira API Token

This guide explains how to generate a Jira API token required for REST API authentication.

---

### Step 1: Open Account Settings

1. Log in to your Jira account.
2. Click on your profile avatar (top-right corner).
3. Select **Account settings**.

![Account Settings](https://github.com/user-attachments/assets/ffc6c3f0-727e-4034-91dc-0d01f3c7f48a)

---

### Step 2: Navigate to Security

1. In the Account Settings page, click on **Security** from the left-hand menu.

![Security Page](https://github.com/user-attachments/assets/e26e09ac-c5e2-47f5-9f53-fc380e6de2d0)

---

### Step 3: Open API Token Management

1. Scroll down to the **API tokens** section.
2. Click **Create and manage API tokens**.

![API Token Management](https://github.com/user-attachments/assets/5069639f-4b61-4611-8669-f91c0e0ae976)

---

### Step 4: Create a New API Token

1. Click **Create API token**.

![Create API Token](https://github.com/user-attachments/assets/48504c9f-0cd6-4a23-9479-9fdf26f02a8f)

---

### Step 5: Configure Token Details

1. Enter a meaningful **Label** (e.g., `post-true-up-validation`).
2. Select the **Expiry date** as required.
3. Click **Create**.

![Token Details](https://github.com/user-attachments/assets/4af4d8d3-a3e9-41f7-b82f-ce4a714ca8e0)

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


