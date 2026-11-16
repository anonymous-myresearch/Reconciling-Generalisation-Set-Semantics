.PHONY: check reference regression owl verify-hashes
check: reference regression owl
	@cat results/integration-status.json
reference:
	python3 reference/check_examples.py
regression:
	python3 tests/test_regressions.py
owl:
	python3 owl-reasoner/run.py
verify-hashes:
	sha256sum -c SHA256SUMS.txt
