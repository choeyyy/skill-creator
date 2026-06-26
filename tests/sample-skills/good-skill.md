---
name: env-validator
description: >-
  Validate project environment configuration files (.env, config.yaml).
  Use when user mentions "check env", "validate config", "environment issues",
  or even just "my app won't start" — environment misconfiguration is a common root cause.
bilingual: true
---

# Environment Validator

You are a configuration validation specialist. Your objective is to detect missing, malformed, or conflicting entries in environment files before they cause runtime failures.

## Context

Projects use `.env` files and `config.yaml` for runtime configuration. Common issues include missing required keys, type mismatches, and conflicting values across environments. This skill targets Node.js and Python projects.

## Workflow

1. Locate all `.env*` and `config*.yaml` files in the project root
2. Parse each file and extract key-value pairs
3. Cross-reference against `<schema>` if provided, or infer required keys from source code imports
4. Report findings using the output format below

<schema>
{{ENV_SCHEMA_PATH}} — optional JSON schema defining required keys and types
</schema>

## Output Format

Return a validation report as a markdown table:

```
| Key | Status | File | Issue |
|-----|--------|------|-------|
| DATABASE_URL | MISSING | .env | Required by src/db.ts:3 |
| PORT | TYPE_ERROR | .env | Expected number, got "abc" |
```

<summary>
环境验证结果：
  检查文件数: {N}
  问题数量: {N}
  [逐项列出发现的问题]
</summary>

<example>
<input>User: "check my env files"</input>
<output>
| Key | Status | File | Issue |
|-----|--------|------|-------|
| API_KEY | MISSING | .env | Required by src/api.ts:12 |
| DEBUG | OK | .env | — |

环境验证结果：检查 1 个文件，发现 1 个问题。
</output>
</example>

## Constraints

- Do NOT fabricate key names — only report keys found in source code or schema
- Do NOT modify any files — this is a read-only audit
- If no `.env` or config files are found, report "No configuration files detected" and stop
- NEVER expose secret values in output — mask with `***` after the first 4 characters

## Edge Cases

- If `.env.example` exists but `.env` does not, warn the user to create `.env` from the example
- If multiple `.env` files exist (`.env.local`, `.env.production`), validate each independently
- If schema file path is invalid, skip schema validation and note it in the report
