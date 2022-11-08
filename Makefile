SHELL := /bin/bash
# MAKEFLAGS := s
changeset := .changeset
deployset := .changeset.deploy
PYTHON := python3

detect-changes:
	branch_name=$$(git rev-parse --abbrev-ref HEAD)
	if [ branch_name == 'main' ] ; then \
		git diff --name-only HEAD~1 HEAD > $(changeset) ;\
	else \
		git diff --name-only origin/main > $(changeset) ;\
	fi
	cat $(changeset) | python cicd/stage_changes.py > $(deployset)
	cat $(deployset)

cicd-deploy:
	cat $(deployset) | python cicd/deploy.py
