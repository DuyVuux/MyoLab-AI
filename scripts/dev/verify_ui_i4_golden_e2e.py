#!/usr/bin/env python3
import json,sys
from pathlib import Path
def main():
    root=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
    p=root/"qa-validation/evidence/ui-i4-golden-browser-e2e.json"
    if not p.exists():print("BLOCKED_FINAL_E2E: missing",p);return 6
    d=json.loads(p.read_text());e=[]
    if d.get("status")!="PASS":e.append("browser E2E did not PASS")
    if d.get("mock_route_interception") is not False:e.append("route interception must be false")
    if not d.get("fixture_sha256"):e.append("fixture sha missing")
    if d.get("exit_code")!=0:e.append("playwright exit nonzero")
    if e:
        print("BLOCKED_FINAL_E2E");[print("-",x) for x in e];return 6
    print("PASS: UI-I4 real browser E2E")
    return 0
if __name__=="__main__":raise SystemExit(main())
