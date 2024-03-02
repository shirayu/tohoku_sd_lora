
SHELL=/bin/bash

all: lint_node lint_python

TARGET_DIRS:=./scripts

pytest:
	pytest -s
	
ruff:
	ruff format --respect-gitignore --check
	ruff check --respect-gitignore

yamllint:
	find . \( -name node_modules -o -name .venv \) -prune -o -type f -name '*.yml' -print \
		| xargs yamllint --no-warnings

lint_python: ruff pytest


pyright:
	npx pyright

markdownlint:
	find . -type d \( -name node_modules -o -name .venv \) -prune -o -type f -name '*.md' -print \
	| xargs npx markdownlint --config ./.markdownlint.json

lint_node: markdownlint pyright


style:
	find $(TARGET_DIRS) | grep '\.py$$' | xargs black
	find $(TARGET_DIRS) | grep '\.py$$' | xargs isort
