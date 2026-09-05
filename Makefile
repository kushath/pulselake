PYTHON ?= python

generate:
	$(PYTHON) -m src.pulselake.generator --events 10000 --seed 42 --output data/sample/events.jsonl

test:
	$(PYTHON) -m unittest discover -s tests -v

demo: generate test
	@echo "PulseLake Milestone 0/1 demo complete."
