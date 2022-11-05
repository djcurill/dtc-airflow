SHELL := /bin/bash
changeset := .changeset
dags := .changeset.dags
PYTHON := python3

detect-changes:
	branch_name=$$(git rev-parse --abrev-ref HEAD)
	if [ branch_name == 'main' ] ; then \
		git diff --name-only HEAD~1 HEAD > $(changeset) ;\
	else \
		git diff --name-only origin/main origin/${GITHUB_HEAD_REF} > $(changeset) ;\
	fi

detect-airflow-changes: $(changeset)
	cat $(changeset) | grep -E 'dags/.*.py|plugins/.*.py' > $(dags)

