PRE_DAY30_CONFIG ?= data-platform/configs/pre_day30_storage.local.yaml

.PHONY: pre-day30-bootstrap pre-day30-checks pre-day30-gate

pre-day30-bootstrap:
	bash scripts/dev/bootstrap_pre_day30_storage.sh --apply

pre-day30-checks:
	bash scripts/dev/run_pre_day30_checks.sh $(PRE_DAY30_CONFIG)

pre-day30-gate:
	python scripts/data/pre_day30_dual_gate.py --config $(PRE_DAY30_CONFIG) --output qa-validation/evidence/pre-day30/pre-day30-dual-gate.json
