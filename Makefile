.PHONY: install run install-dev

install:
	pip install -r requirements.txt

install-dev:
	pip install -e .

run:
	streamlit run alerttrack/app.py
