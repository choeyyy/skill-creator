---
name: log-analyzer
description: "Analyze logs"
---

# Log Analyzer

Read log files from the specified path and look for errors, warnings, and patterns that might indicate issues. Parse each line and categorize it by severity level. When you find recurring patterns, group them together and count occurrences. If there are stack traces, extract the root cause from the deepest frame. For each finding, note the timestamp range, affected component, and frequency. Compare against historical baselines if available, flagging any anomalies that deviate more than 2 standard deviations from the norm. Generate a summary with actionable recommendations sorted by severity, including suggested fixes where possible and links to relevant documentation or runbooks. Consider timezone differences when correlating events across distributed systems.

## Steps

- Read the log file
- Parse each line
- Find errors
- Generate summary

Use the output to help the user understand what went wrong.

If the file is too large, sample the first and last 1000 lines.
