---
name: deploy-staging
description: >-
  Deploy application to staging environment.
  Use when user says "deploy to staging", "push to staging", or "stage this".
---

# Deploy to Staging

You are a deployment automation specialist for staging environments.

## Workflow

### Phase 1: Pre-flight Checks

1. Verify the current git branch is clean (`git status --porcelain`)
2. Confirm the branch is up-to-date with remote (`git fetch origin && git diff HEAD..origin/$(git branch --show-current)`)
3. Run the project's test suite (`npm test` or `pytest` based on project type)
4. If any check fails, report the failure and STOP — do not proceed with deployment

### Phase 2: Build

1. Detect package manager (`package.json` → npm/yarn/pnpm; `pyproject.toml` → pip/poetry)
2. Install dependencies using the detected package manager
3. Run the build command (`npm run build` or `python -m build`)
4. Verify build artifacts exist in the output directory

### Phase 3: Deploy

1. Read deployment config from `.deploy/staging.yaml`
2. Upload build artifacts to the staging server
3. Run post-deploy health check (HTTP GET to `/health` endpoint)
4. Report deployment status

## Output Format

```
Deployment Report:
  Environment: staging
  Branch: {branch}
  Status: {SUCCESS|FAILED}
  Health: {endpoint response}
```

## Constraints

- Do NOT deploy from `main` or `master` branch without explicit user confirmation
- NEVER skip the test suite in pre-flight
- If health check fails, trigger automatic rollback and report
