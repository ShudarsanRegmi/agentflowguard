# Security Demo: PII Leakage via Git Commit Messages

This repository demonstrates how **Personally Identifiable Information (PII)** — usernames, phone numbers, and salary data — can be leaked through **git commit messages** themselves.

---

## The Scenario

A team builds a payroll system. During development, developers accidentally include sensitive data directly in commit messages:

```
daf8d5a Added user jsmith with phone +1-555-123-4567
29f4382 Added admin user (admin, +1-555-987-6543)
12c373e Added payroll report generator, verified with jsmith (+1-555-123-4567) and admin (+1-555-987-6543) test data
8e7f344 Add manager bwilson (bob wilson, phone +1-555-567-8901)
e35d705 Added salary data: jsmith=55000, admin=120000, bwilson=85000
```

Even though the data in tracked files can be changed or deleted, **commit messages are part of the immutable git history**.

---

## How an Attacker Extracts the Data

```bash
# Search commit messages for phone patterns
git log --all --oneline --grep="555-"

# Search for specific usernames
git log --all --oneline --grep="jsmith\|bwilson"

# Search for salary/sensitive keywords
git log --all --oneline --grep="salary\|phone"

# Full log with messages
git log --all --format="%h %s"
```

---

## Why This Is Dangerous

- Commit messages are **never deleted** from git history (unlike files, which can be rewritten).
- `git log --grep` makes extraction trivial.
- Automated secret scanners (truffleHog, Gitleaks) scan commit messages by default.
- This pattern often occurs in:
  - "Added user X with email/phone" messages
  - Debug/testing commits referencing real PII
  - Comments in commit messages about credential changes

---

## Remediation

1. **Use a pre-commit hook** to scan commit messages for regex patterns (phone, email, SSN, etc.)
2. **Train developers** never to put PII in commit messages
3. If already committed, use `git filter-repo` to rewrite history (destructive — requires team coordination)
