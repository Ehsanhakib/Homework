# DS5110 HW5. Run everything with:  make all
SHELL := sh
PY    := python
RAW   := data/raw/AmesHousing.txt
CLEAN := data/processed/ames_clean.csv

.PHONY: all validate clean

all: validate reports/report.md

$(RAW):
	$(PY) src/download.py $(RAW)

$(CLEAN): $(RAW) src/clean.py src/validate.py
	mkdir -p data/processed
	$(PY) src/clean.py $(RAW) $(CLEAN)

# Succeeds only if validation FAILS on raw data and PASSES on cleaned data.
validate: $(CLEAN) $(RAW)
	@if $(PY) src/validate.py $(RAW) --raw; then exit 1; fi
	$(PY) src/validate.py $(CLEAN)

reports/report.md: $(CLEAN) src/missingness.py src/impute.py src/evaluate.py
	mkdir -p reports/figures reports/results
	$(PY) src/missingness.py $(CLEAN)
	$(PY) src/impute.py $(CLEAN)
	$(PY) src/evaluate.py $(CLEAN)
	@echo "Results written to reports/. Update reports/report.md if it is hand-written."

clean:
	rm -rf data/processed reports/figures reports/results
