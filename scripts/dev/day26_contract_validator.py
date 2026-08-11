from pathlib import Path
import json
import yaml

ROOT = Path(__file__).resolve().parents[2]


def main():
    required = ['FR-034', 'FR-037', 'FR-041']
    impact = yaml.safe_load(
        (ROOT / 'qa-validation/traceability/day26-requirement-impact.yaml').read_text()
    )
    assert set(impact['requirements']) == set(required)
    schema = json.loads(
        (ROOT / 'packages/common-schemas/json/labeling-function-output.schema.json').read_text()
    )
    assert schema['properties']['ground_truth_claim']['const'] is False
    assert schema['properties']['expert_label_claim']['const'] is False
    print('DAY26 contract validator: PASS')


if __name__ == '__main__':
    main()
