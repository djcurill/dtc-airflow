SHELL := /bin/bash
MAKEFLAGS := s
changeset := .changeset
dags := .changeset.dags
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

deploy-dags:
	if [ -s $(dags) ]; then
		echo "Deploying dags..."
		cat $(dags) | gsutil -m cp -I "gs://$(GCP_COMPOSER_BUCKET)/dags"
		echo "Dags deployment complete!"
	else
		echo "No changes detected from DAGs"
	fi

deploy-plugins:
	if [ -s $(plugins) ]; then
		echo "Deploying plugins..."
		cat $(plugins) | gsutil -m cp -I "gs://$(GCP_COMPOSER_BUCKET)/dags"
		echo "Plugins deployment complete!"
	else
		echo "No changes detected from plugins"
	fi

cicd-deploy: 
	$(MAKE) deploy-dags 
	$(MAKE) deploy-plugins


	