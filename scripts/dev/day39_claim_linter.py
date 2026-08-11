from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
paths=[ROOT/'docs/00-executive/gates/GATE-C-R-qc-research-readiness.md',ROOT/'docs/00-executive/milestones/M2-R-qc-research-core.md',ROOT/'docs/00-executive/rebaseline/day39-evidence-index.md']
forbidden=['validated at vinmec','deployed at vinmec','hospital-ready','pilot-ready','clinically proven','diagnostic accuracy']
errors=[]
for p in paths:
 text=p.read_text(encoding='utf-8').lower()
 for token in forbidden:
  if token in text: errors.append((str(p),token))
if errors:
 print(errors); raise SystemExit(1)
print('DAY39 CLAIM LINTER PASS',len(paths))
