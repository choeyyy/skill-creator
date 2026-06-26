# Extraction Patterns — Common Extractable Logic Catalog

Reference document for the Extractor agent. Load on demand; do not embed inline.

---

## 1. Pattern Types

Each pattern type represents a category of deterministic logic commonly found duplicated across skills.

| # | Pattern Type | Key Indicator | Typical Steps |
|---|--------------|---------------|---------------|
| 1 | Data Formatting | Transform structured data from one format to another | ≥3 (parse → transform → render) |
| 2 | API Request Sequence | Multi-step HTTP interaction with known schema | ≥4 (auth → request → parse → format) |
| 3 | File Operations | Read, transform, and write file content | ≥3 (read → transform → write) |
| 4 | Report Generation | Aggregate data and produce formatted output | ≥4 (gather → aggregate → template → output) |
| 5 | Validation Sequence | Check inputs/state against rules and report | ≥3 (check → validate → report) |

---

## 2. Detailed Pattern Descriptions

### 2.1 Data Formatting

**Description**: Converts structured data from one representation to another without semantic interpretation.

**Detection heuristics**:
- Steps reference format names (JSON, CSV, YAML, table, markdown)
- Transformation is mechanical (field mapping, column selection, string templates)
- No conditional logic based on content meaning

**Common variants**:

| Variant | Input | Output | Example |
|---------|-------|--------|---------|
| JSON → Markdown table | JSON array/object | Markdown table string | API response → readable table |
| CSV → Report | CSV file/string | Formatted report | Data export → summary document |
| Object → Template | Key-value data | Filled template string | Config values → config file |
| List → Enumeration | Array of items | Numbered/bulleted list | Search results → formatted list |

**CLI parameterization**:
- `--input` / `--input-format`: source data or file path
- `--output-format`: target format (table, csv, json, template)
- `--fields`: comma-separated field names to include
- `--template`: path to template file (for template variant)

---

### 2.2 API Request Sequence

**Description**: Multi-step HTTP interaction involving authentication, request execution, response parsing, and result formatting.

**Detection heuristics**:
- Steps mention tokens, headers, endpoints, HTTP methods
- Response handling follows parse → extract → format pattern
- Auth is token-based or key-based (not interactive OAuth)

**Common variants**:

| Variant | Auth | Method | Post-processing |
|---------|------|--------|-----------------|
| Token + GET + Format | Bearer token refresh | GET with query params | Parse JSON → format output |
| Key + POST + Extract | API key in header | POST with JSON body | Extract nested fields → table |
| Multi-request chain | Single auth, multiple calls | Sequential GETs | Merge responses → aggregate |

**CLI parameterization**:
- `--endpoint`: target URL or URL template
- `--auth-token` / `--auth-file`: authentication credential or file
- `--method`: HTTP method (default GET)
- `--body`: request body (for POST/PUT)
- `--extract`: JSONPath or field path for extraction
- `--output-format`: how to format the result

---

### 2.3 File Operations

**Description**: Read file(s), apply deterministic transformations, and write results.

**Detection heuristics**:
- Steps reference file paths, read/write operations
- Transformation is rule-based (regex, find-replace, restructure)
- No content interpretation required

**Common variants**:

| Variant | Read | Transform | Write |
|---------|------|-----------|-------|
| Template expansion | Template file + data | Variable substitution | Filled output file |
| Batch rename/restructure | Directory listing | Apply naming rules | Renamed/moved files |
| Content injection | Target file + snippet | Insert at marker/position | Updated file |
| Format conversion | Source file | Parse → re-serialize | Converted file |

**CLI parameterization**:
- `--input`: source file or directory path
- `--output`: destination file or directory path
- `--pattern`: regex or glob for matching
- `--replacement`: replacement string or template
- `--dry-run`: preview changes without writing

---

### 2.4 Report Generation

**Description**: Gather data from multiple sources, aggregate, and produce a formatted report.

**Detection heuristics**:
- Steps collect data from files, APIs, or command output
- Aggregation is arithmetic or categorical (counts, sums, groupings)
- Output uses a fixed template structure

**Common variants**:

| Variant | Sources | Aggregation | Output |
|---------|---------|-------------|--------|
| Status dashboard | Multiple API endpoints | Categorize by state | Markdown table/summary |
| Diff report | Two versions of data | Compare field-by-field | Change log with additions/removals |
| Metric summary | Log files or API data | Count, sum, average | Statistics table |
| Inventory report | Directory scan | List + metadata | Catalog document |

**CLI parameterization**:
- `--sources`: comma-separated paths or endpoints
- `--template`: report template path
- `--output`: output file path (or stdout)
- `--format`: output format (markdown, json, html)
- `--period`: time range for temporal data

---

### 2.5 Validation Sequence

**Description**: Check inputs or system state against a set of rules and produce a pass/fail report.

**Detection heuristics**:
- Steps reference rules, checks, requirements, constraints
- Each check produces a binary (pass/fail) or categorical result
- Results are aggregated into a summary verdict

**Common variants**:

| Variant | Target | Rules Source | Output |
|---------|--------|-------------|--------|
| File structure check | Directory tree | Expected structure definition | Missing/extra items report |
| Content validation | Document/config | Schema or rule set | Violations list |
| Dependency check | Package file | Required versions | Compatibility report |
| Pre-flight check | Environment | Required tools/configs | Readiness summary |

**CLI parameterization**:
- `--target`: file or directory to validate
- `--rules`: rules file or inline rule spec
- `--strict`: fail on warnings (default: fail on errors only)
- `--output-format`: report format (json, table, summary)

---

## 3. Viability Assessment

Use this table to score extraction viability:

| Factor | High | Medium | Low |
|--------|------|--------|-----|
| I/O clarity | Clear CLI args in, stdout/file out | Some args need complex types | Requires interactive input |
| Dependencies | stdlib only or 1-2 common packages | 3-5 packages, all on PyPI | Unusual deps or system-level requirements |
| Parameterization | All variants covered by args | Most variants covered, some hardcoded | Significant hardcoding needed per use |
| Determinism | Identical output for identical input | Output varies only in formatting | Output depends on timing or external state |
| Reuse potential | ≥3 skills would benefit | 2 skills benefit | Marginal benefit over inline |

**Scoring**: Count "High" factors. Viability = High (4-5), Medium (2-3), Low (0-1).

---

## 4. Exclusion Criteria

Do NOT flag as extractable:

| Criterion | Reason |
|-----------|--------|
| Requires LLM interpretation | Not deterministic |
| Single-use procedure | No reuse benefit |
| Interactive mid-flow | Cannot be CLI-ified |
| Context-dependent branching | Output varies by judgment |
| < 3 steps total | Too trivial to extract |
| Appears in only 1 skill | No duplication to eliminate |
