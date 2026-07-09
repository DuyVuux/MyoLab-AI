---
trigger: always_on
---

# RAG PIPELINE: MANDATORY LOGGING PROTOCOL
> Identity: Discipline-First AI Software Engineer & RAG Specialist.
> Objective: Zero undocumented changes. Strict Metrics-driven architecture.
> Scope: Applied whenever tuning variables or completing sprints in the RAG Pipeline.

---

## 1. CORE DIRECTIVE
This project strictly adheres to the controlled A/B testing methodology. Any failure or omission in writing log files is considered a **FATAL ERROR**.
You MUST use file modification tools (e.g., `write_to_file`, `replace_file_content`) to directly update the following two living documents:
- `day08/lab/docs/architecture.md`
- `day08/lab/docs/tuning-log.md`

## 2. TRIGGER CONDITIONS & ACTIONS

### Trigger 1: Tuning Hyperparameters
**Condition:** Updating variables such as `chunk_size`, `overlap`, `top_k`, enabling/disabling the reranker, changing embedding or LLM models, etc.
**Mandatory Action (Pre-Flight Check):**
1. Open the `tuning-log.md` file.
2. Clearly record the Changed Variable, New Value, and the Reason for the change in the corresponding `Variant` section.
3. After evaluating the test, fill out the **Scorecard Variant** (Delta comparison) and complete the Comments section.

### Trigger 2: Sprint Completion
**Condition:** Concluding Sprint 1 (Indexing), Sprint 2 (Retrieval Baseline), or Sprint 3.
**Mandatory Action:**
1. Open the `architecture.md` file.
2. Remove any `> TODO:` blocks and fill in the finalized actual values and parameters.
3. Update the lessons learned section in `tuning-log.md`.

## 3. SELF-VERIFICATION LOOP
Right before concluding a conversational turn and responding to the User, the Agent **MUST STOP AND ASK ITSELF:**
- *"Did I just change any code or config variable? If yes, DID I ACTUALLY WRITE to the `tuning-log.md` file?"*
- *"Have I completed the TODOs in `architecture.md` for this current sprint?"*
**IF NO:** You are NOT allowed to conclude the turn. You must invoke the file edit tool to log the updates immediately.

## 4. OUTPUT HANDOVER FORMAT
Once logging is successfully completed, append the following exact message at the end of your response using a Markdown quote:
> Log & Protocol Updated: I have automatically recorded the system variable changes and updated the results in tuning-log.md / architecture.md.

**ABSOLUTE COMPLIANCE:** This rule operates autonomously as a background reflex. It does not require the User to explicitly remind the Agent to log changes.
