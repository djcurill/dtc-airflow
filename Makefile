SHELL := /bin/bash
MAKEFLAGS := s
changeset := .changeset
dags := .changeset.deploy
plugins := .changeset.plugins
PYTHON := python3
GCP_COMPOSER_BUCKET ?= ${GCP_COMPOSER_BUCKET}

detect-changes:
	branch_name=$$(git rev-parse --abbrev-ref HEAD)
	if [ branch_name == 'main' ] ; then \
		git diff --name-only HEAD~1 HEAD > $(changeset) ;\
	else \
		git diff --name-only origin/main > $(changeset) ;\
	fi
	cat $(changeset) | python cicd/stage_changes.py

cicd-deploy:
	echo "Deploying dags..."
	cat $(dags) | gsutil -m cp -I "gs://$(GCP_COMPOSER_BUCKET)/dags"
	echo "Dags deployment complete!"
	echo "Deploying plugins..."
	cat $(plugins) | gsutil -m cp -I "gs://$(GCP_COMPOSER_BUCKET)/plugins"
	echo "Plugins deployment complete!"
	