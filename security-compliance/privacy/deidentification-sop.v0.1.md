# MotionLab De-identification SOP v0.1

**Status:** DRAFT CONTROL — requires Vinmec privacy/data-governance approval before use with patient data.

## Purpose
Create a governed analysis derivative without silently destroying the immutable source or claiming anonymity that has not been demonstrated.

## Input
- source export in approved restricted location;
- source identifier/hash;
- data-use purpose;
- governance/consent status;
- operator identity authorized for the source zone.

## Procedure
1. **Preflight:** verify approved environment and authorization. If unknown, STOP with `PRIVACY_PATH_NOT_APPROVED`.
2. **Inventory identifiers:** inspect metadata keys, filenames/path components and free text. Do not inspect/transfer more raw data than necessary.
3. **Generate canonical analysis ID:** random/non-semantic ID; never derive from name/MRN/date of birth.
4. **Separate identity mapping:** if a re-linkage map is operationally required, store it outside the analysis repository in the approved restricted system. DAY05 does not define its physical location.
5. **Transform derivative (HIPAA Safe Harbor):** remove all 18 direct identifiers; sanitize filename/project/record-name/free text; retain only purpose-required fields (Data Minimization).
6. **Temporal fields & Quasi-identifiers (GDPR Pseudonymisation):** exact date/time retention or transformation is policy-dependent. Apply date-shifting or generalization. If not approved by Expert Determination, mark `TBD` and block the derivative from downstream patient-data use.
7. **Validate:** scan structured fields against the identifier policy; perform human review of free text and file names.
8. **Provenance:** record source hash, transformation policy version, reviewer status and derivative hash. Never overwrite raw.
9. **Access:** apply least privilege from `patient-data-access-matrix.v0.1.yaml` or stricter site policy.
10. **Release gate:** derivative is usable only when governance status and de-identification review are explicit. `UNKNOWN` is not equivalent to approved.

## Failure states
- `PRIVACY_PATH_NOT_APPROVED`
- `DIRECT_IDENTIFIER_DETECTED`
- `FREE_TEXT_REVIEW_REQUIRED`
- `DEIDENTIFICATION_STATUS_UNKNOWN`
- `GOVERNANCE_STATUS_UNKNOWN`
- `ACCESS_NOT_AUTHORIZED`
- `RETENTION_POLICY_TBD`

## Non-goals
- This SOP does not certify HIPAA compliance or any other jurisdiction-specific compliance.
- It does not guarantee irreversible anonymization.
- It does not authorize cloud transfer, external sharing or research use.
