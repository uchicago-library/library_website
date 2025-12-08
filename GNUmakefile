ifndef SECRETS_REPO_DIR
	SECRETS_REPO_DIR = ~
endif

SECRETS_REPO_NAME = lw-config
SECRETS_REPO_PATH = $(SECRETS_REPO_DIR)/$(SECRETS_REPO_NAME)
SETTINGS_PATH = ./library_website/settings
CURRENT_BRANCH = $$(git -C $(SECRETS_REPO_PATH) symbolic-ref --short HEAD)
CLONE_URL = wagtail@vault.lib.uchicago.edu:/data/vault/wagtail/$(SECRETS_REPO_NAME)

.PHONY: docker
docker: secrets docker-clean docker-cache

.PHONY: docker-cache
docker-cache: secrets
	./docker-setup.sh

.PHONY: docker-clean
docker-clean:
	./docker-cleanup.sh

.PHONY: update-secrets
update-secrets:
	git -C $(SECRETS_REPO_PATH) pull origin $(CURRENT_BRANCH)

.PHONY: install
install: 
	$(RM) $(SETTINGS_PATH)/secrets.py || true
	install -m 444 $(SECRETS_REPO_PATH)/secrets.py $(SETTINGS_PATH)

.PHONY: secrets
secrets: update-secrets install

.PHONY: create-repo
create-repo:
	mkdir -p $(SECRETS_REPO_DIR)
	git -C $(SECRETS_REPO_DIR) clone $(CLONE_URL)

.PHONY: clean
clean:
	$(RM) $(SETTINGS_PATH)/secrets.py || true
