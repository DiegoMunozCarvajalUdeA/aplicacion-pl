.PHONY: setup run test lint fmt verify requirements ui-check manual-captures

OUT ?= /tmp/plapp-ui

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
	uv run ruff format .
	uv run ruff check --fix .

verify:
	uv run python scripts/verify.py "$(FILE)"

requirements:
	uv export --locked --no-dev --no-hashes --no-editable --output-file requirements.txt

ui-check:
	uv run python scripts/check_ui.py --serve --solutions --downloads --output "$(OUT)"

manual-captures:
	uv run python scripts/check_ui.py --serve --manual

