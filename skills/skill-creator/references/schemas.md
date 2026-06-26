# JSON Schemas

Schemas for all structured data files used in the skill-creator eval workflow.

## evals.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "test_cases": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "prompt", "expectations"],
        "properties": {
          "id": { "type": "string" },
          "prompt": { "type": "string" },
          "files": { "type": "array", "items": { "type": "string" } },
          "expectations": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["id", "description"],
              "properties": {
                "id": { "type": "string" },
                "description": { "type": "string" },
                "type": { "type": "string", "enum": ["contains", "format", "behavior", "absence"] }
              }
            }
          }
        }
      }
    }
  }
}
```

## grading.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["test_id", "config", "expectations", "overall", "pass_rate"],
  "properties": {
    "test_id": { "type": "string" },
    "config": { "type": "string", "enum": ["with_skill", "without_skill"] },
    "expectations": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "verdict"],
        "properties": {
          "id": { "type": "string" },
          "verdict": { "type": "string", "enum": ["pass", "fail", "partial"] },
          "evidence": { "type": "string" }
        }
      }
    },
    "overall": { "type": "string", "enum": ["pass", "fail"] },
    "pass_rate": { "type": "number", "minimum": 0, "maximum": 1 }
  }
}
```

## benchmark.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["with_skill", "without_skill", "delta", "test_count", "timestamp"],
  "properties": {
    "with_skill": {
      "type": "object",
      "properties": {
        "pass_rate": { "type": "number" },
        "mean_time_ms": { "type": "number" },
        "stddev_time_ms": { "type": "number" }
      }
    },
    "without_skill": {
      "type": "object",
      "properties": {
        "pass_rate": { "type": "number" },
        "mean_time_ms": { "type": "number" },
        "stddev_time_ms": { "type": "number" }
      }
    },
    "delta": {
      "type": "object",
      "properties": {
        "pass_rate": { "type": "number" },
        "time_ms": { "type": "number" }
      }
    },
    "test_count": { "type": "integer" },
    "timestamp": { "type": "string", "format": "date-time" }
  }
}
```

## history.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "versions": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["version", "timestamp", "pass_rate", "changes"],
        "properties": {
          "version": { "type": "integer" },
          "timestamp": { "type": "string", "format": "date-time" },
          "pass_rate": { "type": "number" },
          "changes": { "type": "string" },
          "parent": { "type": "integer" }
        }
      }
    },
    "current_best": { "type": "integer" }
  }
}
```

## timing.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "array",
  "items": {
    "type": "object",
    "required": ["test_id", "config", "duration_ms", "timestamp"],
    "properties": {
      "test_id": { "type": "string" },
      "config": { "type": "string", "enum": ["with_skill", "without_skill"] },
      "duration_ms": { "type": "number" },
      "timestamp": { "type": "string", "format": "date-time" }
    }
  }
}
```

## TODO: Full implementation pending

Schema validation tooling, migration scripts for schema version upgrades, and extended schemas for multi-skill comparative benchmarks to be added in a future iteration.
