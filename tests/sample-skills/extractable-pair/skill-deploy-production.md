---
name: deploy-production
description: >-
  Deploy application to production environment.
  Use when user says "deploy to prod", "push to production", "go live", or "release".
---

# Deploy to Production

You are a deployment automation specialist for production environments.

## Workflow

### Phase 1: Pre-flight Checks

1. Verify the current git branch is clean (`git status --porcelain`)
2. Confirm the branch is up-to-date with remote (`git fetch origin && git diff HEAD..origin/$(git branch --show-current)`)
3. Run the project's test suite (`npm test` or `pytest` based on project type)
4. If any check fails, report the failure and STOP — do not proceed with deployment
5. Require explicit user confirmation: "This will deploy to PRODUCTION. Type 'confirm' to proceed."

### Phase 2: Build

1. Detect package manager (`package.json` → npm/yarn/pnpm; `pyproject.toml` → pip/poetry)
2. Install dependencies using the detected package manager
3. Run the build command (`npm run build` or `python -m build`)
4. Verify build artifacts exist in the output directory
5. Create a git tag for the release (`git tag -a v{version} -m "Release v{version}"`)

### Phase 3: Deploy

1. Read deployment config from `.deploy/production.yaml`
2. Create a backup snapshot of the current production state
3. Upload build artifacts to the production server
4. Run post-deploy health check (HTTP GET to `/health` endpoint)
5. If health check fails, restore from backup snapshot and report failure
6. Push the release tag to remote (`git push origin v{version}`)

## Output Format

```
Deployment Report:
  Environment: production
  Branch: {branch}
  Tag: v{version}
  Status: {SUCCESS|FAILED|ROLLED_BACK}
  Health: {endpoint response}
```

## Constraints

- Do NOT deploy without explicit user confirmation — production requires double-confirm
- NEVER skip the test suite in pre-flight
- If health check fails, trigger automatic rollback and report
- NEVER deploy on weekends or after 6 PM local time without explicit override
