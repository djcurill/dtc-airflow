SHELL := /bin/bash
# MAKEFLAGS := s
changeset := .changeset
deployset := .changeset.deploy
PYTHON := python3
GCP_COMPOSER_BUCKET ?= ${GCP_COMPOSER_BUCKET}

detect-changes:
	branch_name=$$(git rev-parse --abbrev-ref HEAD)
	if [ branch_name == 'main' ] ; then \
		git diff --name-only HEAD~1 HEAD > $(changeset) ;\
	else \
		git diff --name-only origin/main > $(changeset) ;\
	fi
	cat $(changeset) | python cicd/stage_changes.py > $(deployset)

cicd-deploy:
	cat $(deployset) | gsutil -m cp -I $(GCP_COMPOSER_BUCKET)
	