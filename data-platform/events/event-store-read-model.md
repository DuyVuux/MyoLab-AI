# DAY53 Dual-Log Event Store Design v0.1

## Decision
Use two physically and semantically separate append-only streams.

1. **Compliance audit stream** — approval/security accountability. Pseudonymous actor identity may be retained under local research access policy.
2. **Research process stream** — workflow reconstruction, duration/process analysis and future learning-readiness. It uses role-level actor semantics and must not contain raw waveform, PHI, source paths or diagnostic text.

The streams may share `correlation_id`, `case_id` and `logical_action_id`; they do not share retention or access policy by assumption.

## Storage model
Each stream is newline-delimited canonical JSON wrapped in an integrity envelope:

`sequence -> previous_record_hash -> event -> record_hash`.

`record_hash = SHA256(canonical_json(sequence, previous_record_hash, event))`.

Any edit, deletion, reordering or insertion in the middle breaks replay verification. The reference implementation intentionally exposes append and read/replay only. There is no update/delete API.

## Idempotency
The event payload owns a deterministic `event_id`. Re-appending the exact same event ID and body is idempotent. Reusing an event ID with different content is rejected as `EVENT_ID_CONFLICT`.

## Process reconstruction
Research events carry `case_id`, `activity`, `state_before`, `state_after`, `correlation_id`, `reason_codes`, `source_refs`, versions and optional duration. Replay can reconstruct the ordered state transition sequence without reading raw signal data.

## Access and retention
This project is research-only. The design stores policy metadata but does not claim enterprise IAM or legal retention compliance. Compliance and research streams have distinct role allowlists. Persistent local JSONL is a research reference implementation, not a production clinical datastore.

## Safety boundary
No waveform, raw samples, patient name, MRN, source filesystem path, free-text clinical note or diagnosis may enter either normalized event schema. Fail closed on prohibited keys.
