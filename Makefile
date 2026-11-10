.PHONY: setup run test lint fmt verify requirements

setup:
	uv sync --locked

run:
	uv run streamlit run app/streamlit_app.py

test:
	uv run pytest

lint:
	uv run ruff check .
	uv run ruff format --check .

fmt:
	uv run ruff check --fix .
	uv run ruff format .

verify:
	uv run python scripts/verify.py "$(FILE)"

requirements:
	uv export --locked --no-dev --no-hashes --no-editable --output-file requirements.txt

