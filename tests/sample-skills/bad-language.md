---
name: 代码审查工具
description: >-
  Review code for common issues and suggest improvements.
---

# 代码审查助手

You are a code review assistant.

## 工作流程

1. 读取用户指定的文件
2. 分析代码质量
3. Generate a report with findings

## 输出格式

| 检查项 | 命令 | 状态 |
|--------|------|------|
| 语法检查 | `eslint .` | 通过 |
| 类型检查 | `tsc --noEmit` | 失败 |

## Context

This skill reviews JavaScript and TypeScript files for:
- Unused variables
- Missing error handling
- 不规范的命名

## Constraints

- Do NOT modify source files
- 如果文件不存在，停止并报告错误
- NEVER auto-fix without user confirmation

## Edge Cases

- If the file is binary, skip and report "不支持二进制文件"
- Empty files should be flagged as suspicious
