# BizPulse AI — Team Git Workflow

## Main Rule

`main` should always be runnable.

Do not develop large features directly on `main`.

## Recommended Branches

- `feature/data-analytics` — Member 1
- `feature/ai-ml` — Member 2
- `feature/frontend` — Member 3
- `feature/testing-reliability` — Member 4
- `feature/integration-demo` — Member 5

## Starting Your Branch

```bash
git checkout main
git pull origin main
git checkout -b feature/your-branch-name
```

Then push it:

```bash
git push -u origin feature/your-branch-name
```

## Before Merging

Always update your branch with the latest main:

```bash
git checkout main
git pull origin main
git checkout feature/your-branch-name
git merge main
```

Resolve conflicts locally, test, then push.

## Commit Style

Use small, clear commits:

```text
feat: add revenue and profit calculations
feat: add z-score anomaly detection
fix: handle missing CSV columns
test: add analytics KPI tests
docs: update demo instructions
```

## Merge Rule

Before merging to `main`:

1. App starts successfully.
2. No API keys are committed.
3. Existing features still work.
4. Tests pass where applicable.
5. Another teammate quickly reviews the change.

## Hackathon Integration Rule

Merge working slices early. Do not wait until the final sprint to integrate.
