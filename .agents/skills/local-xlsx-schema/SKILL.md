---
name: local-xlsx-schema
description: Use when a user provides a local .xlsx/.xlsm Excel workbook and wants its sheets inspected, normalized into entities, or converted into database schema, SQL migrations, seed data plans, import scripts, JSON schemas, or TypeScript types. Prefer this over API-based document conversion skills for local workbooks.
---

# Local XLSX Schema

Use this skill for local Excel workbooks that need to become durable application data structures.

## Workflow

1. Inspect the workbook locally before designing anything.
   - Prefer `scripts/inspect_workbook.py <file.xlsx>` when `openpyxl` is available.
   - Capture sheet names, dimensions, header rows, metadata rows, merged cells if relevant, and representative non-empty rows.

2. Classify each sheet.
   - `data`: rows with stable records, headers, and repeatable values.
   - `metadata`: key/value product or configuration facts.
   - `scoring`: score ranges, bands, rubrics, or result labels.
   - `draft`: notes, planning, free-form page copy, or TODOs. Do not model as first-class tables unless the user asks.

3. Normalize into entities.
   - Identify parent objects before child rows, such as workbook product -> assessment -> questions -> options.
   - Preserve order columns for user-facing sequencing.
   - Use lookup tables for reusable domains, industries, professions, levels, categories, topics, and score bands.
   - Use JSON only for content that is intentionally flexible or not queried independently.

4. Generate schema in the target project style.
   - For SQL projects, add a new forward migration instead of editing deployed migrations.
   - Match existing naming, ID, timestamp, constraint, and index conventions.
   - Use nullable fields for imported workbook columns that are incomplete or inconsistently populated.
   - Add uniqueness constraints around natural import identity where possible, such as `(assessment_id, question_order)`.

5. Document import assumptions.
   - Say which sheets were modeled and which were skipped.
   - Call out ambiguous headers, mixed data types, date-looking score cells, empty question groups, and generated slugs.

## Local Extraction

Run:

```bash
python3 .agents/skills/local-xlsx-schema/scripts/inspect_workbook.py "Workbook.xlsx"
```

The script prints compact JSON with workbook sheets, sample rows, inferred row kinds, and simple column statistics. Use it as evidence, not as the final schema design.

## Schema Heuristics

- Multiple-choice questions should usually be represented as a question table plus an option table with `option_key`, `option_order`, `option_text`, and `is_correct`.
- Score bands should be separate from questions when the workbook maps total score ranges to result labels.
- Profession or role-specific question banks should include `level` and `profession_id`/`position` on the assessment or question set, not duplicated only in question text.
- Keep raw source traceability with `source_sheet`, `source_row`, or `source_ref` when importing editorial content.
- Avoid destructive migration edits. If a schema already exists, create the next numbered migration.
