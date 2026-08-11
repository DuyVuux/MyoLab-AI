from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
M = ROOT / 'qa-validation/evidence/day26-artifact-manifest.json'


def main():
    m = json.loads(M.read_text())
    missing = [x for x in m['managed_files'] if not (ROOT / x).is_file()]
    if missing:
        raise SystemExit('missing: ' + str(missing))
    print('DAY26 artifact checker: PASS', len(m['managed_files']))


if __name__ == '__main__':
    main()
